from src.core.interfaces.prompt_provider import PromptProvider

class DefaultPromptProvider(PromptProvider):
    def get_extraction_prompt(self, text: str) -> str:
        """Fase 1: Extração Técnica e Gélida de Dados."""
        return (
            "Sua tarefa é extrair dados de um currículo e transformá-los em um JSON puro.\n"
            "Cumpra rigorosamente o esquema abaixo:\n"
            "{\n"
            "  \"name\": \"Nome Completo\",\n"
            "  \"email\": \"email@exemplo.com\",\n"
            "  \"phone\": \"(00) 00000-0000\",\n"
            "  \"skills\": [\"skill1\", \"skill2\"],\n"
            "  \"experience\": [\n"
            "    {\"role\": \"Cargo\", \"company\": \"Empresa\", \"duration\": \"Tempo\"}\n"
            "  ]\n"
            "}\n"
            "Regras Críticas:\n"
            "1. Se um campo não for encontrado, retorne \"\" (string vazia) ou [] (lista vazia).\n"
            "2. Retorne APENAS o objeto JSON. Não adicione markdown (```json) ou explicações.\n"
            "3. Não invente dados.\n\n"
            f"TEXTO DO CURRÍCULO:\n{text}"
        )

    def get_job_analysis_prompt(self, job_description: str) -> str:
        """Fase 2: Interpretação Sênior da Vaga."""
        return f"""Analise esta descrição de vaga e gere um perfil técnico estruturado em JSON.
        
VAGA:
{job_description}

FORMATO DE SAÍDA:
{{
  "title": "Título real da função",
  "seniority": "Junior|Pleno|Senior|Specialist",
  "functional_core": "Descreva o núcleo real da função em uma frase",
  "requirements": {{
    "mandatory": ["itens que sem eles o candidato é descartado"],
    "important": ["diferenciais competitivos"],
    "soft_skills": []
  }}
}}
Retorne APENAS o JSON puro."""

    def get_triage_prompt(self, candidate_json: str, job_profile_json: str, level: str) -> str:
        """Fase 3/4: Triagem Multi-Nível."""
        
        depth_instructions = ""
        if level == "basic":
            depth_instructions = "Retorne apenas o 'score_final' (0-10) e um 'veredito' de uma frase."
        elif level == "short":
            depth_instructions = "Retorne 'score_final', 'veredito', 'pontos_fortes' (top 3) e 'lacunas' (top 3)."
        else:
            depth_instructions = """Realize uma auditoria completa. Retorne:
            - score_final (0-10)
            - veredito detalhado
            - analise_senioridade (aderência ao cargo)
            - evidencias_fortes (lista com justificativa)
            - lacunas_criticas (lista)
            - sugestao_entrevista (pergunta chave)"""

        return f"""Você é um Avaliador de RH Sênior do Brasil. 
Compare o CANDIDATO contra os REQUISITOS da vaga abaixo.

REQUISITOS (JobProfile):
{job_profile_json}

CANDIDATO (JSON):
{candidate_json}

OBJETIVO DA RESPOSTA:
{depth_instructions}

REGRAS CRÍTICAS: 
1. Saída deve ser EXCLUSIVAMENTE um JSON válido. Não adicione prefixos ou notas informais.
2. Todo o texto gerado (veredito, análise, evidências e perguntas) DEVE SER RIGOROSAMENTE EM PORTUGUÊS DO BRASIL (PT-BR)."""
