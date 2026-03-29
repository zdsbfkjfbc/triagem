from abc import ABC, abstractmethod
from src.core.entities.candidate import Candidate
from src.application.analyzers import ScoreCandidato

class BaseScorer(ABC):
    @abstractmethod
    def score(self, candidate: Candidate, context: str) -> ScoreCandidato:
        """Gera um score específico para o candidato."""
        pass
