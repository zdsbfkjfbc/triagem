from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class Experience:
    company: str
    role: str
    duration: str
    description: Optional[str] = None

@dataclass
class JobProfile:
    """Perfil técnico estruturado da vaga (Fase 2)."""
    title: str
    seniority: str
    functional_core: str
    requirements: Dict[str, List[str]]
    raw_description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Candidate:
    name: str 
    email: str = ""
    phone: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    experience: List[Experience] = field(default_factory=list)
    education: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    
    # Resultados da Triagem 3-Níveis (Fase 3/4)
    fit_score: float = 0.0
    fast_match: Optional[Dict[str, Any]] = None      # Nível 1: Score + Veredito Minimalista
    short_analysis: Optional[Dict[str, Any]] = None  # Nível 2: Pontos Chave + Gaps
    detailed_audit: Optional[Dict[str, Any]] = None  # Nível 3: Auditoria Sênior Completa
    
    metadata: Dict[str, Any] = field(default_factory=dict) 

@dataclass
class EvaluationScore:
    technical_fit: float = 0.0 
    cultural_fit: float = 0.0  
    experience_fit: float = 0.0 
    overall_score: float = 0.0
    reasoning: str = ""
