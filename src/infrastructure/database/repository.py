from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
import os
from pathlib import Path
from typing import List, Optional, Any
from .models import Base, Job, CandidateModel, TriageResult, TriageTask, TriageError

# Configuração Padrão: SQLite Local - Caminho Absoluto Garantido
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SQLITE_PATH = PROJECT_ROOT / "triage.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}")

class TriageRepository:
    def __init__(self, db_url: str = DATABASE_URL):
        # Aumentamos o timeout para 30s para evitar travamentos em gravações paralelas (SQLite)
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False, "timeout": 30})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Garantir que as tabelas existem (Criação Automática no Início)
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    # --- Operações de Vagas (Jobs) ---
    def create_job(self, title: str, description: str, requirements_json: Optional[dict] = None, owner_id: Optional[int] = None) -> Job:
        with self.get_session() as session:
            job = Job(title=title, description=description, requirements_json=requirements_json, owner_id=owner_id)
            session.add(job)
            session.commit()
            session.refresh(job)
            return job

    def list_jobs(self, status: str = 'open') -> List[Job]:
        with self.get_session() as session:
            # Type ignoring due to SQLAlchemy dynamic query resolution in Mypy
            return session.query(Job).filter(Job.status == status).all() # type: ignore

    def delete_job(self, job_id: int) -> bool:
        with self.get_session() as session:
            job = session.get(Job, job_id)
            if job:
                session.delete(job)
                session.commit()
                return True
            return False

    # --- Operações de Candidatos ---
    def get_candidate_by_hash(self, file_hash: str) -> Optional[CandidateModel]:
        with self.get_session() as session:
            return session.query(CandidateModel).filter(CandidateModel.file_hash == file_hash).first() # type: ignore

    def create_candidate(self, file_hash: str, name: str, extracted_json: dict, original_text: str, email: Optional[str] = None) -> CandidateModel:
        with self.get_session() as session:
            # Note: Usamos CandidateModel explicitamente para evitar colisão com a Entidade Candidate
            candidate = CandidateModel(
                file_hash=file_hash, 
                name=name, 
                email=email, 
                extracted_json=extracted_json, 
                original_text=original_text
            )
            session.add(candidate)
            session.commit()
            session.refresh(candidate)
            return candidate

    # --- Operações de Resultados (CRM) ---
    def save_triage_result(
        self,
        job_id: int,
        candidate_id: int,
        score: float,
        analysis_json: Any,
        status: str = "novo",
    ) -> TriageResult:
        with self.get_session() as session:
            result = TriageResult(
                job_id=job_id,
                candidate_id=candidate_id,
                score=score,
                analysis_json=analysis_json,
                status=status,
            )
            session.add(result)
            session.commit()
            session.refresh(result)
            return result

    def update_result_status(self, result_id: int, status: str) -> bool:
        with self.get_session() as session:
            result = session.get(TriageResult, result_id)
            if result:
                result.status = status
                session.commit()
                return True
            return False

    def update_result_notes(self, result_id: int, notes: str) -> bool:
        with self.get_session() as session:
            result = session.get(TriageResult, result_id)
            if result:
                result.recruiter_notes = notes
                session.commit()
                return True
            return False

    def delete_triage_result(self, result_id: int) -> bool:
        with self.get_session() as session:
            result = session.get(TriageResult, result_id)
            if result:
                session.delete(result)
                session.commit()
                return True
            return False

    # --- Operações de Monitoramento (Ciclo 3) ---
    def create_or_update_task(self, job_id: int, total_files: int) -> TriageTask:
        with self.get_session() as session:
            task = session.query(TriageTask).filter(TriageTask.job_id == job_id).first()
            if task:
                task.total_files = total_files
                task.processed_files = 0
                task.status = 'running'
            else:
                task = TriageTask(job_id=job_id, total_files=total_files)
                session.add(task)
            
            # Limpar erros antigos desse job_id para o frontend não mostrar 'fantasmas'
            session.query(TriageError).filter(TriageError.job_id == job_id).delete()
            
            session.commit()
            session.refresh(task)
            return task

    def increment_task_progress(self, job_id: int, status: str = 'running'):
        with self.get_session() as session:
            task = session.query(TriageTask).filter(TriageTask.job_id == job_id).first()
            if task:
                task.processed_files += 1
                if task.processed_files >= task.total_files:
                    task.status = 'completed'
                else:
                    task.status = status
                session.commit()

    def log_triage_error(self, job_id: int, file_name: str, error_message: str):
        with self.get_session() as session:
            err = TriageError(job_id=job_id, file_name=file_name, error_message=error_message)
            session.add(err)
            session.commit()

    def get_task_status(self, job_id: int) -> Optional[dict]:
        with self.get_session() as session:
            task = session.query(TriageTask).filter(TriageTask.job_id == job_id).first()
            if not task:
                return None
            return {
                "job_id": task.job_id,
                "total": task.total_files,
                "processed": task.processed_files,
                "status": task.status,
                "percent": round((task.processed_files / task.total_files * 100), 1) if task.total_files > 0 else 0
            }

    def get_job_errors(self, job_id: int) -> List[TriageError]:
        with self.get_session() as session:
            return session.query(TriageError).filter(TriageError.job_id == job_id).all()
