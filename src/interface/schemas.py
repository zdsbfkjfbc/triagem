from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

# --- Enums Simulados (Strings fixas) ---
# Status: 'novo', 'triado', 'entrevista', 'aprovado', 'reprovado'

class JobBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str

class JobCreate(JobBase):
    pass

class JobRead(JobBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class TalentResultRead(BaseModel):
    id: int
    candidate_id: int
    candidate_name: str
    job_title: str
    score: float
    analysis: Any # JSON
    status: str
    recruiter_notes: Optional[str] = None
    original_text: Optional[str] = None
    date: datetime

    class Config:
        from_attributes = True

class StatusUpdateSchema(BaseModel):
    status: str = Field(..., pattern="^(novo|revisao_assistida|triado|entrevista|aprovado|reprovado)$")

class NotesUpdateSchema(BaseModel):
    notes: str
