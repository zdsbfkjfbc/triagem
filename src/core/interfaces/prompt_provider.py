from abc import ABC, abstractmethod

class PromptProvider(ABC):
    @abstractmethod
    def get_extraction_prompt(self, text: str) -> str:
        """Retorna o prompt para extração básica de dados."""
        pass

    @abstractmethod
    def get_job_analysis_prompt(self, job_description: str) -> str:
        """Prompt para transformar a vaga em um perfil estruturado (Fase 2)."""
        pass

    @abstractmethod
    def get_triage_prompt(self, candidate_json: str, job_profile_json: str, level: str) -> str:
        """Prompt para triagem em um dos níveis: basic, short ou full (Fase 3/4)."""
        pass
