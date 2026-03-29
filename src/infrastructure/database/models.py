from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    """Modelo para recrutadores/analistas de RH."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(20), default='recruiter') # 'admin' ou 'recruiter'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    jobs = relationship("Job", back_populates="owner")

class Job(Base):
    """Modelo para as Vagas cadastradas."""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    requirements_json = Column(JSON, nullable=True) # Perfil interpretado pela IA
    status = Column(String(20), default='open') # 'open', 'closed'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="jobs")
    results = relationship("TriageResult", back_populates="job")

class CandidateModel(Base):
    """Modelo para Candidatos (Cache de Extração)."""
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True)
    file_hash = Column(String(64), unique=True, index=True) # Hash MD5/SHA256
    name = Column(String(100))
    email = Column(String(255), nullable=True) # E-mail de contato
    extracted_json = Column(JSON) # Dados estruturados (JSON)
    original_text = Column(Text) # Texto puro do currículo
    created_at = Column(DateTime, default=datetime.utcnow)
    
    results = relationship("TriageResult", back_populates="candidate")

class TriageResult(Base):
    """Ranking e análises de uma triagem específica."""
    __tablename__ = 'triage_results'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    score = Column(Float)
    analysis_json = Column(JSON) # Veredito, pontos fortes, lacunas
    status = Column(String(20), default='novo') # 'novo', 'triado', 'entrevista', 'aprovado', 'reprovado'
    recruiter_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    job = relationship("Job", back_populates="results")
    candidate = relationship("CandidateModel", back_populates="results")

class TriageTask(Base):
    """Controle de progresso de lotes em background."""
    __tablename__ = 'triage_tasks'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), unique=True) # Um lote por vaga por vez
    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    status = Column(String(20), default='running') # 'running', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TriageError(Base):
    """Registro de falhas específicas por arquivo."""
    __tablename__ = 'triage_errors'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    file_name = Column(String(255))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
