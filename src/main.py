from config.settings import settings
from src.infrastructure.parsers.file_parsers import TXTParser
from src.infrastructure.ai.openai_adapter import OpenAIAdapter
from src.infrastructure.ai.prompt_provider import DefaultPromptProvider
from src.application.triage_service import ResumeTriageApp
from src.application.analyzers import CandidateScorer
from src.application.scorers import TechnicalScorer, ExperienceScorer, CulturalScorer, PotentialScorer

def main():
    print("--- Sistema de Triagem (Refatorado) ---")
    
    # 1. Configurar infraestrutura com Inversão de Dependência
    parser = TXTParser()
    prompt_provider = DefaultPromptProvider()
    ai = OpenAIAdapter(api_key=settings.OPENAI_API_KEY, prompt_provider=prompt_provider)
    
    # 2. Configurar Scorers (Strategy Pattern)
    scorers = {
        "technical": TechnicalScorer(),
        "experience": ExperienceScorer(),
        "cultural": CulturalScorer(),
        "potential": PotentialScorer()
    }
    scorer_orchestrator = CandidateScorer(scorers=scorers)
    
    # 3. Rodar aplicação
    app = ResumeTriageApp(parser, ai)
    
    test_file = "resume_test.txt"
    job_desc = "Dev Python Senior, FastAPI, Cloud. Foco em Inovação."

    candidates = app.process_resumes([test_file], settings.DEFAULT_CULTURAL_VALUES)
    
    for c in candidates:
        analise = scorer_orchestrator.analyze(c, job_desc)
        print(f"\nResultado Final: {analise.score_final} ({analise.recomendacao})")
        for key, detail in analise.scores.items():
            print(f"- {key}: {detail.valor} | {detail.justificativa}")

if __name__ == "__main__":
    main()
