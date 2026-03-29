import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEFAULT_CULTURAL_VALUES: str = """
    - Inovação e proatividade
    - Trabalho em equipe e colaboração
    - Foco em resultados e qualidade de código
    """

settings = Settings()
