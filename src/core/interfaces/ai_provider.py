from abc import ABC, abstractmethod
from src.core.entities.candidate import Candidate, JobProfile

class AIProvider(ABC):
    @abstractmethod
    def extract_candidate_data(self, text: str) -> Candidate:
        """Extrai dados estruturados de um texto bruto (Fase 1)."""
        pass

    @abstractmethod
    def analyze_job(self, job_description: str) -> JobProfile:
        """Gera o perfil técnico estruturado da vaga (Fase 2)."""
        pass

    @abstractmethod
    def perform_triage(self, candidate: Candidate, job_profile: JobProfile, level: str) -> dict:
        """Executa a triagem em níveis (basic, short, full) (Fase 3/4)."""
        pass
