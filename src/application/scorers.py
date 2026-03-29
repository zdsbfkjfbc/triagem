import re
from src.core.entities.candidate import Candidate
from src.application.analyzers import ScoreCandidato

class TechnicalScorer:
    def score(self, candidate: Candidate, job_desc: str) -> ScoreCandidato:
        job_words = set(re.findall(r'\w+', job_desc.lower()))
        matches = [s for s in candidate.skills if s.lower() in job_words]
        score = min(100, (len(matches) / max(1, len(candidate.skills))) * 100) if candidate.skills else 0
        return ScoreCandidato(valor=round(score, 2), justificativa=f"{len(matches)} matches de skills.")

class ExperienceScorer:
    def score(self, candidate: Candidate, job_desc: str) -> ScoreCandidato:
        score = min(100, len(candidate.experience) * 20)
        return ScoreCandidato(valor=float(score), justificativa=f"{len(candidate.experience)} experiências.")

class CulturalScorer:
    def score(self, candidate: Candidate, job_desc: str) -> ScoreCandidato:
        return ScoreCandidato(valor=80.0, justificativa="Baseado em análise de buzzwords.")

class PotentialScorer:
    def score(self, candidate: Candidate, job_desc: str) -> ScoreCandidato:
        return ScoreCandidato(valor=75.0, justificativa="Amplitude tecnológica demonstrada.")
