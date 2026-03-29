"""
languages.py

Extração de idiomas e níveis a partir do texto.
"""

from __future__ import annotations

import re
from typing import List, Optional

from src.infrastructure.parsers.cv_extractors.models import LanguageItem
from src.infrastructure.parsers.cv_extractors.sectioning import extract_section_text, normalize_text


def parse_languages(cv_text: str, target_position: Optional[int] = None) -> List[LanguageItem]:
    text = normalize_text(cv_text)

    all_headings = [
        "Idiomas",
        "Languages",
        "Formação",
        "Education",
        "Experiência",
        "Experience",
        "Skills",
        "Habilidades",
        "Certificações",
        "Certificacoes",
        "Projetos",
        "Projects",
    ]
    section = extract_section_text(
        text,
        headings=["Idiomas", "Languages"],
        all_headings_for_cut=all_headings,
        target_position=target_position,
    )
    if not section:
        return []

    languages: List[LanguageItem] = []
    lines = [ln.strip() for ln in section.split("\n") if ln.strip()]

    if lines and re.match(r"(?i)^\s*(idiomas|languages)\s*:?\s*$", lines[0]):
        lines = lines[1:]

    for ln in lines:
        m = re.match(r"^\s*(?P<lang>.+?)\s*(?:-|:|/)\s*(?P<level>.+?)\s*$", ln)
        if not m:
            tokens = re.split(r"\s+", ln)
            if len(tokens) >= 2:
                lang = " ".join(tokens[:-1]).strip()
                level = tokens[-1].strip()
                if lang and level:
                    try:
                        languages.append(LanguageItem(language=lang, level=level))
                    except ValueError:
                        pass
            continue

        lang = m.group("lang").strip()
        level = m.group("level").strip()

        level = re.sub(
            r"(?i)\b(fluente|fluent|avancado|advanced|intermedi[eá]rio|intermediate|b[aá]sico|basic|nativo|native)\b",
            level,
            level,
        )

        if not lang:
            continue
        try:
            languages.append(LanguageItem(language=lang, level=level or None))
        except ValueError:
            continue

    # Dedup por language (case-insensitivo)
    seen: set[str] = set()
    unique: List[LanguageItem] = []
    for item in languages:
        key = item.language.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique

