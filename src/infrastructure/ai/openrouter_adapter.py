from openai import OpenAI
import json
import re
from typing import List, Optional

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.core.entities.candidate import Candidate, Experience, JobProfile
from src.core.interfaces.ai_provider import AIProvider
from src.core.interfaces.prompt_provider import PromptProvider


class OpenRouterAdapter(AIProvider):
    def __init__(
        self,
        api_key: str,
        prompt_provider: PromptProvider,
        model_id: str = "google/gemini-2.0-flash-lite-preview-02-05:free",
    ):
        if not api_key:
            raise ValueError("API Key ausente. O processamento nao pode continuar.")

        if not api_key.startswith("sk-or"):
            print("Aviso: a chave nao parece ser do OpenRouter (esperava sk-or-...).")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model_id = model_id
        self.prompt_provider = prompt_provider
        self.fast_fallback_models: List[str] = [
            "openai/gpt-oss-20b:free",
            "google/gemini-2.0-flash-lite-preview-02-05:free",
            "meta-llama/llama-3.2-3b-instruct:free",
        ]

    def _extract_json(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
            cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                return {}

    def _call_ai_once(self, system_prompt: str, user_prompt: str, model_id: str, timeout_s: int = 45) -> dict:
        response = self.client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=2048,
            timeout=timeout_s,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Resposta vazia da OpenRouter.")
        return self._extract_json(content)

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=lambda retry_state: print(
            f"Falha na IA. Tentando novamente ({retry_state.attempt_number}/3)..."
        ),
    )
    def _call_ai_with_retry(self, system_prompt: str, user_prompt: str, model_id: str) -> dict:
        return self._call_ai_once(system_prompt, user_prompt, model_id, timeout_s=45)

    def _call_ai_fast_with_fallback(self, system_prompt: str, user_prompt: str, model_id: str) -> dict:
        preferred_models = [model_id] + [m for m in self.fast_fallback_models if m != model_id]
        last_error: Optional[Exception] = None

        for candidate_model in preferred_models:
            try:
                print(f"Tentando modelo rapido: {candidate_model}")
                return self._call_ai_once(system_prompt, user_prompt, candidate_model, timeout_s=20)
            except Exception as e:
                last_error = e
                print(f"Falha no modelo {candidate_model}: {e}")
                continue

        if last_error:
            raise last_error
        return {}

    def _call_ai(
        self,
        system_prompt: str,
        user_prompt: str,
        model_id: Optional[str] = None,
        fast_mode: bool = False,
    ) -> dict:
        target_model = model_id or self.model_id
        try:
            if fast_mode:
                return self._call_ai_fast_with_fallback(system_prompt, user_prompt, target_model)
            return self._call_ai_with_retry(system_prompt, user_prompt, target_model)
        except Exception as e:
            print(f"Erro final na chamada AI ({target_model}): {e}")
            return {}

    def extract_candidate_data(self, text: str) -> Candidate:
        system = "Voce e um extrator de dados JSON preciso."
        prompt = self.prompt_provider.get_extraction_prompt(text)
        data = self._call_ai(system, prompt)

        raw_exp = data.get("experience", [])
        experiences = []
        for item in raw_exp:
            if isinstance(item, dict):
                experiences.append(
                    Experience(
                        company=item.get("company", ""),
                        role=item.get("role", ""),
                        duration=item.get("duration", ""),
                    )
                )

        return Candidate(
            name=data.get("name", "Nome Oculto"),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            skills=data.get("skills", []),
            experience=experiences,
        )

    def analyze_job(self, job_description: str) -> JobProfile:
        system = "Voce e um Analista de RH focado em arquitetura de cargos."
        prompt = self.prompt_provider.get_job_analysis_prompt(job_description)
        data = self._call_ai(system, prompt)

        return JobProfile(
            title=data.get("title", "Vaga Sem Titulo"),
            seniority=data.get("seniority", "N/A"),
            functional_core=data.get("functional_core", ""),
            requirements=data.get("requirements", {}),
            raw_description=job_description,
        )

    def perform_triage(self, candidate: Candidate, job_profile: JobProfile, level: str) -> dict:
        system = "Voce e um Avaliador de RH Senior Critico."

        cand_dict = {
            "name": candidate.name,
            "skills": candidate.skills,
            "experience": [
                {
                    "role": exp.role if hasattr(exp, "role") else (exp.get("role", "N/A") if isinstance(exp, dict) else "N/A"),
                    "company": exp.company if hasattr(exp, "company") else (exp.get("company", "N/A") if isinstance(exp, dict) else "N/A"),
                }
                for exp in candidate.experience
            ],
        }

        job_dict = {
            "title": job_profile.title,
            "seniority": job_profile.seniority,
            "requirements": job_profile.requirements,
        }

        prompt = self.prompt_provider.get_triage_prompt(
            json.dumps(cand_dict),
            json.dumps(job_dict),
            level,
        )

        fast_mode = level == "basic"
        return self._call_ai(system, prompt, fast_mode=fast_mode)
