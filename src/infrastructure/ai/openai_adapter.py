from openai import OpenAI
from src.core.entities.candidate import Candidate
from src.core.interfaces.ai_provider import AIProvider
from src.core.interfaces.prompt_provider import PromptProvider

class OpenAIAdapter(AIProvider):
    def __init__(self, api_key: str, prompt_provider: PromptProvider):
        self.client = OpenAI(api_key=api_key)
        self.prompt_provider = prompt_provider

    def extract_candidate_data(self, text: str) -> Candidate:
        # 1. Busca o prompt via Injeção de Dependência
        _ = self.prompt_provider.get_extraction_prompt(text)
        
        # Chamada fictícia (mantendo como mock por enquanto)
        return Candidate(
            name="John Doe",
            email="john@example.com",
            skills=["Python", "Cloud Computing"],
            experience=[]
        )

    def evaluate_fit(self, candidate: Candidate, cultural_values: str) -> float:
        return 8.5
