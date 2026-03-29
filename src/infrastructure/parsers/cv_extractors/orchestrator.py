"""
orchestrator.py

Orquestração: chama os parsers de cada seção e monta o JSON final.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.infrastructure.parsers.cv_extractors.contact import extract_contact_info
from src.infrastructure.parsers.cv_extractors.education import parse_education
from src.infrastructure.parsers.cv_extractors.experience import parse_experiences
from src.infrastructure.parsers.cv_extractors.languages import parse_languages
from src.infrastructure.parsers.cv_extractors.models import CVData, ExtractionError, validate_extracted_cv_data
from src.infrastructure.parsers.cv_extractors.patterns import TECH_KEYWORDS  # noqa: F401 (mantido p/ transparência)
from src.infrastructure.parsers.cv_extractors.projects import parse_projects
from src.infrastructure.parsers.cv_extractors.skills import extract_skills_technical
from src.infrastructure.parsers.cv_extractors.certifications import parse_certifications
from src.infrastructure.parsers.cv_extractors.sectioning import normalize_text


def _ensure_optional_int(value: Any, field_name: str) -> Optional[int]:
    if value is None:
        return None
    if not isinstance(value, int):
        raise ExtractionError(f"{field_name} deve ser um inteiro ou None.")
    return value


def extract_cv_data(cv_text: str, target_position: Optional[int] = None) -> Dict[str, Any]:
    """
    Entrada:
    - cv_text: texto bruto do CV já convertido para string
    - target_position: posição alvo (índice de caractere) opcional

    Saída:
    - dict compatível com JSON:
      nome, email, telefone, localização,
      experiences, skills_technical, education, languages,
      certifications, projects
    """

    if not isinstance(cv_text, str):
        raise ExtractionError("cv_text deve ser uma string.")

    text = normalize_text(cv_text)
    tpos = _ensure_optional_int(target_position, "target_position")
    if tpos is not None and (tpos < 0 or tpos >= len(text)):
        tpos = None

    contact = extract_contact_info(text)
    skills = extract_skills_technical(text, target_position=tpos)
    experiences = parse_experiences(text, target_position=tpos)
    education = parse_education(text, target_position=tpos)
    languages = parse_languages(text, target_position=tpos)
    certifications = parse_certifications(text, target_position=tpos)
    projects = parse_projects(text, target_position=tpos)

    cv = CVData(
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        location=contact.location,
        experiences=experiences,
        skills_technical=skills,
        education=education,
        languages=languages,
        certifications=certifications,
        projects=projects,
    )

    out = cv.to_json_dict()
    # Valida shape mínimo antes de retornar.
    validate_extracted_cv_data(out)
    return out

