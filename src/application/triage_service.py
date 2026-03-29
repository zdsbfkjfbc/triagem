import os
import time
import hashlib
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore
from src.core.entities.candidate import Candidate, JobProfile, Experience
from src.core.interfaces.ai_provider import AIProvider
from src.core.interfaces.file_parser import FileParser
from src.infrastructure.database.repository import TriageRepository

class ResumeTriageApp:
    def __init__(self, parser: FileParser, ai: AIProvider, repository: TriageRepository = None):
        self.parser = parser
        self.ai = ai
        self.repo = repository or TriageRepository()
        self.max_workers = 3 # Limite de concorrência global (Oprimiza Performance vs Estabilidade)
        self.semaphore = Semaphore(self.max_workers)

    def _get_file_hash(self, file_path: str) -> str:
        """Calcula o hash MD5 para detecção de duplicatas."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def process_single_resume(self, path: str, job_profile: JobProfile, job_id: int) -> Candidate:
        """Processa um único arquivo com controle de concorrência e semáforo."""
        with self.semaphore:
            t_init = time.time()
            f_hash = self._get_file_hash(path)
            
            # --- 1. Deduplicação (Cache Global) ---
            candidate = None
            cached_candidate = self.repo.get_candidate_by_hash(f_hash)
            if cached_candidate:
                # Reconstrução segura (Fase de Estabilização V4.5)
                exp_list = cached_candidate.extracted_json.get("experience", [])
                experiences = [Experience(**e) if isinstance(e, dict) else e for e in exp_list]
                
                candidate = Candidate(
                    name=cached_candidate.name,
                    email=getattr(cached_candidate, 'email', ""),
                    skills=cached_candidate.extracted_json.get("skills", []),
                    experience=experiences,
                    metadata={"cached": True}
                )
                cand_id = cached_candidate.id
            else:
                # Extração Real (IA)
                text = self.parser.parse(path)
                candidate = self.ai.extract_candidate_data(text)
                
                extracted_data = {
                    "skills": candidate.skills,
                    "experience": [exp.__dict__ for exp in candidate.experience]
                }
                new_cand = self.repo.create_candidate(f_hash, candidate.name, extracted_data, text, email=candidate.email)
                cand_id = new_cand.id

            # --- 2. Triagem (Match Rápido) ---
            basic_match = self.ai.perform_triage(candidate, job_profile, level="basic")
            
            # Validação Estrita (Evitar salvar lixo se IA der erro de token)
            if not basic_match or "score_final" not in basic_match:
                raise ValueError(f"Falha na IA: Não foi possível analisar o candidato {candidate.name} para esta vaga (Erro de API ou Token).")
                
            candidate.fast_match = basic_match
            candidate.fit_score = float(basic_match.get("score_final", 0.0))
            candidate.detailed_audit = None
            
            # Triagem Profunda Apenas Para Acima de 7.5
            if candidate.fit_score >= 7.5:
                print(f"🕵️ {candidate.name} obteve {candidate.fit_score}. Acionando Auditoria Profunda...")
                detailed = self.ai.perform_triage(candidate, job_profile, level="full")
                if detailed and "score_final" in detailed:
                    candidate.detailed_audit = detailed
            
            # Persistência do Resultado
            analysis_data = {
                "fast_match": candidate.fast_match,
                "detailed_audit": candidate.detailed_audit
            }
            self.repo.save_triage_result(job_id, cand_id, candidate.fit_score, analysis_data)
            
            candidate.metadata["total_time"] = round(time.time() - t_init, 2)
            return candidate

    def process_resumes(self, file_paths: List[str], job_description: str, job_id: int = None) -> Tuple[List[Candidate], JobProfile]:
        """Processa lote em PARALELO com barra de progresso no console."""
        
        print(f"🚀 Iniciando Triagem de {len(file_paths)} arquivos...")
        job_profile = self.ai.analyze_job(job_description)
        
        if not job_id:
            new_job = self.repo.create_job(
                title=job_profile.title, 
                description=job_description,
                requirements_json=job_profile.requirements
            )
            job_id = new_job.id

        results = []
        total = len(file_paths)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_single_resume, p, job_profile, job_id): p for p in file_paths}
            
            count = 0
            for future in as_completed(futures):
                count += 1
                file_path = futures[future]
                file_name = os.path.basename(file_path)
                
                try:
                    candidate = future.result()
                    results.append(candidate)
                    
                    # Atualiza Progresso no Banco (Ciclo 3)
                    self.repo.increment_task_progress(job_id)
                    
                    # Log de Progresso Visual
                    progress = int((count / total) * 10)
                    bar = "█" * progress + "-" * (10 - progress)
                    print(f"[{bar}] {int(count/total*100)}% | {candidate.name} finalizado.")
                    
                except Exception as exc:
                    print(f"❌ Erro ao processar {file_name}: {exc}")
                    # Registra Erro no Banco (Ciclo 3)
                    self.repo.log_triage_error(job_id, file_name, str(exc))
                    # Mesmo com erro, incrementamos o progresso (como finalizado com erro)
                    self.repo.increment_task_progress(job_id, status='running')

        results.sort(key=lambda x: x.fit_score, reverse=True)
        return results, job_profile
