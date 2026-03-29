from dataclasses import dataclass
from typing import Dict, Optional, Any
from src.core.entities.candidate import Candidate

@dataclass(frozen=True)
class ScoreCandidato:
    valor: float  # 0-100
    justificativa: str

@dataclass(frozen=True)
class AnaliseCandidato:
    nome: str
    scores: Dict[str, ScoreCandidato]
    score_final: float
    recomendacao: str

class CandidateScorer:
    """
    O Orquestrador (Composite) que coordena múltiplos Scorers.
    """
    def __init__(self, scorers: Dict[str, Any], weights: Optional[Dict[str, float]] = None):
        self.scorers = scorers
        self.weights = weights or {
            "technical": 0.35,
            "experience": 0.25,
            "cultural": 0.20,
            "potential": 0.20
        }

    def analyze(self, candidate: Candidate, job_desc: str) -> AnaliseCandidato:
        results = {}
        final = 0.0
        
        for key, scorer in self.scorers.items():
            result = scorer.score(candidate, job_desc)
            results[key] = result
            final += result.valor * self.weights.get(key, 0)

        # Recomendação
        if final >= 80:
            rec = "FORTE"
        elif final >= 50:
            rec = "MÉDIO"
        else:
            rec = "FRACO"

        return AnaliseCandidato(
            nome=candidate.name,
            scores=results,
            score_final=round(final, 2),
            recomendacao=rec
        )
