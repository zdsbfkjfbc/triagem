import argparse

from src.application.triage_service import ResumeTriageApp
from src.infrastructure.parsers.file_parsers import TXTParser
from src.infrastructure.ai.openai_adapter import OpenAIAdapter
from src.infrastructure.ai.openrouter_adapter import OpenRouterAdapter
from src.infrastructure.ai.prompt_provider import DefaultPromptProvider

def main():
    parser = argparse.ArgumentParser(description="Resume Triage System CLI")
    parser.add_argument("--files", nargs="+", required=True, help="Lista de arquivos de currículo (.txt)")
    parser.add_argument("--values", required=True, help="Valores culturais para avaliação")
    parser.add_argument("--provider", choices=["openai", "openrouter"], default="openrouter", help="Provedor de IA")
    parser.add_argument("--api-key", required=True, help="Chave de API do provedor")

    args = parser.parse_args()

    # 1. Setup Providers
    prompt_p = DefaultPromptProvider()
    if args.provider == "openai":
        ai_provider = OpenAIAdapter(api_key=args.api_key, prompt_provider=prompt_p)
    else:
        ai_provider = OpenRouterAdapter(api_key=args.api_key, prompt_provider=prompt_p)

    # 2. Setup Parser (Defaulting to TXT for now)
    file_parser = TXTParser()

    # 3. Setup App
    app = ResumeTriageApp(parser=file_parser, ai=ai_provider)

    # 4. Run Process
    results = app.process_resumes(args.files, args.values)

    # 5. Output Results
    print("\n" + "="*30)
    print("RESULTADOS DA TRIAGEM (RANKING)")
    print("="*30)
    for i, candidate in enumerate(results, 1):
        print(f"{i}. {candidate.name} - Score: {candidate.fit_score:.2f}")
        print(f"   Email: {candidate.email}")
        print(f"   Skills: {', '.join(candidate.skills)}")
        print("-" * 20)

if __name__ == "__main__":
    main()
