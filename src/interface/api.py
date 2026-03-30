# ruff: noqa: E402
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import os
import shutil
import tempfile
from typing import List
from datetime import datetime

# 🛡️ Middleware de Segurança Customizado
class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src 'self' fonts.gstatic.com;"
        return response

app = FastAPI(title="BRBPO Triage API", version="3.3.1")

# 🔒 Segurança e Hardening
app.add_middleware(SecureHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importações absolutas para evitar problemas em tempo de execução
from src.application.triage_service import ResumeTriageApp
from src.infrastructure.parsers.file_parsers import UniversalParser
from src.infrastructure.ai.openrouter_adapter import OpenRouterAdapter
from src.infrastructure.ai.prompt_provider import DefaultPromptProvider
from src.infrastructure.database.repository import TriageRepository
from src.infrastructure.security.auth import AuthManager
from src.interface.schemas import JobRead, TalentResultRead, StatusUpdateSchema, NotesUpdateSchema
from src.infrastructure.database.models import TriageResult, CandidateModel, Job # Import centralizado

repo = TriageRepository()
auth_manager = AuthManager()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- Utilitários de Autenticação ---

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependência para verificar se o token é válido e retornar o usuário."""
    payload = auth_manager.decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

# --- Endpoints de Autenticação ---

@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint para autenticação de recrutadores e geração de token JWT."""
    with repo.get_session() as session:
        user = auth_manager.authenticate_user(session, form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Usuário ou senha incorretos.")
        
        access_token = auth_manager.create_access_token(
            data={"sub": user.username, "role": user.role}
        )
        return {"access_token": access_token, "token_type": "bearer"}

# --- Endpoints de Negócio (Protegidos) ---

@app.get("/jobs", response_model=List[JobRead])
async def get_jobs():
    """Retorna todas as vagas (Público)."""
    return repo.list_jobs()

@app.post("/jobs", response_model=JobRead)
async def create_job(
    title: str = Form(...), 
    description: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Cadastra uma nova oportunidade (Protegido)."""
    existing_jobs = repo.list_jobs()
    if any(j.title.lower() == title.lower() for j in existing_jobs):
        raise HTTPException(status_code=400, detail="Uma vaga com este título já existe.")
    return repo.create_job(title, description)

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: int, current_user: dict = Depends(get_current_user)):
    """Exclui uma vaga do sistema (Protegido)."""
    success = repo.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vaga não encontrada.")
    return {"status": "deleted", "job_id": job_id}

@app.post("/triage/batch", status_code=202)
async def run_batch_triage(
    background_tasks: BackgroundTasks,
    api_key: str = Form(...),
    model_id: str = Form("minimax/minimax-01"),
    job_id: int = Form(...),
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Executa a triagem em lote (Protegido)."""
    with repo.get_session() as session:
        job = session.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        job_description = job.description # Extrai dados antes de fechar o context

    # Inicializa monitoramento no processo principal para evitar 404 no primeiro poll (Ciclo 3.5)
    repo.create_or_update_task(job_id, len(files))

    temp_dir = tempfile.mkdtemp()
    temp_paths = []
    for f in files:
        path = os.path.join(temp_dir, f.filename)
        with open(path, "wb") as bf:
            shutil.copyfileobj(f.file, bf)
        temp_paths.append(path)

    # Função interna para evitar passagem de objetos de sessão SQLAlchemy entre threads
    def process_triage_background(temp_paths: List[str], job_description: str, job_id: int, api_key: str, model_id: str):
        prompt_p = DefaultPromptProvider()
        
        try:
            ai = OpenRouterAdapter(api_key=api_key, prompt_provider=prompt_p, model_id=model_id)
            triage_app = ResumeTriageApp(parser=UniversalParser(), ai=ai, repository=repo)
            
            # Repassamos o job_id para o service que agora tem logs e barra de progresso no console
            triage_app.process_resumes(temp_paths, job_description, job_id=job_id)
            
            # Finaliza tarefa com sucesso
            repo.increment_task_progress(job_id, status='completed')
            
        except Exception as e:
            print(f"❌ Falha crítica no lote {job_id}: {e}")
            repo.log_triage_error(job_id, "SISTEMA", str(e))
            repo.increment_task_progress(job_id, status='failed')
        finally:
            # Limpeza de diretório temporário
            try:
                shutil.rmtree(os.path.dirname(temp_paths[0]))
            except OSError:
                pass

    background_tasks.add_task(process_triage_background, temp_paths, job_description, job_id, api_key, model_id)

    return {
        "status": "processing", 
        "message": f"Olá {current_user['sub']}, triagem iniciada.",
        "job_id": job_id
    }

@app.get("/triage/status/{job_id}")
async def get_triage_status(job_id: int, current_user: dict = Depends(get_current_user)):
    """Retorna o status em tempo real do processamento (Ciclo 3)."""
    status = repo.get_task_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Nenhuma tarefa encontrada para esta vaga.")
    return status

@app.get("/triage/errors/{job_id}")
async def get_triage_errors(job_id: int, current_user: dict = Depends(get_current_user)):
    """Retorna o relatório de erros de um lote (Ciclo 3)."""
    errors = repo.get_job_errors(job_id)
    return [
        {"file_name": e.file_name, "error": e.error_message, "date": e.created_at} 
        for e in errors
    ]

@app.get("/talent-pool", response_model=List[TalentResultRead])
async def get_talent_pool(current_user: dict = Depends(get_current_user)):
    """Retorna o histórico completo com tratamento robusto de nulos (Protegido)."""
    with repo.get_session() as session:
        # Query explícita para evitar problemas de lazy loading
        query = session.query(TriageResult, CandidateModel, Job).join(CandidateModel, TriageResult.candidate_id == CandidateModel.id).join(Job, TriageResult.job_id == Job.id)
        results = query.all()
        
        output = []
        for r, c, j in results:
            # Garantia de integridade para o Pydantic (A10: Exceptional Conditions)
            output.append({
                "id": r.id,
                "candidate_id": c.id,
                "candidate_name": c.name or "Candidato Sem Nome",
                "job_title": j.title or "Vaga Sem Título",
                "score": float(r.score) if r.score is not None else 0.0,
                "analysis": r.analysis_json or {"veredito": "Sem análise disponível."},
                "status": r.status or "novo",
                "recruiter_notes": r.recruiter_notes,
                "original_text": c.original_text,
                "date": r.created_at if r.created_at else datetime.utcnow()
            })
        return output

@app.patch("/talent-pool/{result_id}/status")
async def update_candidate_status(
    result_id: int, 
    update: StatusUpdateSchema,
    current_user: dict = Depends(get_current_user)
):
    """Atualiza o estágio do candidato (Protegido)."""
    success = repo.update_result_status(result_id, update.status)
    if not success:
        raise HTTPException(status_code=404, detail="Resultado de triagem não encontrado.")
    return {"status": "updated", "new_pipeline_stage": update.status}

@app.patch("/talent-pool/{result_id}/notes")
async def update_candidate_notes(
    result_id: int, 
    update: NotesUpdateSchema,
    current_user: dict = Depends(get_current_user)
):
    """Atualiza anotações (Protegido)."""
    success = repo.update_result_notes(result_id, update.notes)
    if not success:
        raise HTTPException(status_code=404, detail="Resultado de triagem não encontrado.")
    return {"status": "updated", "notes_saved": True}

@app.delete("/talent-pool/{result_id}")
async def delete_candidate_from_pool(
    result_id: int, 
    current_user: dict = Depends(get_current_user)
):
    """Exclui permanentemente o resultado da triagem de um candidato. (Protegido)."""
    success = repo.delete_triage_result(result_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resultado de triagem não encontrado.")
    return {"status": "deleted", "result_id": result_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
