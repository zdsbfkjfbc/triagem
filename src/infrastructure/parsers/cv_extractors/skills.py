"""
skills.py

Extração de habilidades técnicas a partir do texto do currículo.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from src.infrastructure.parsers.cv_extractors.patterns import TECH_REGEXES
from src.infrastructure.parsers.cv_extractors.sectioning import extract_section_text, normalize_text


def extract_skills_technical(cv_text: str, target_position: Optional[int] = None) -> List[str]:
    """
    Extrai skills técnicas:
    1) Se houver seção de skills, parseia lista separada por vírgula/; e bullets.
    2) Caso contrário, tenta inferir por ocorrência de keywords no texto.
    """
    text = normalize_text(cv_text)

    all_headings = [
        "Skills",
        "Habilidades",
        "Experiência",
        "Experience",
        "Formação",
        "Education",
        "Idiomas",
        "Languages",
        "Certificações",
        "Certificacoes",
        "Projetos",
        "Projects",
    ]
    skills_section = extract_section_text(
        text,
        headings=["Skills", "Habilidades"],
        all_headings_for_cut=all_headings,
        target_position=target_position,
    )

    found: List[Tuple[int, str]] = []  # (pos, keyword)

    if skills_section:
        body = re.sub(
            r"(?im)^\s*(skills|habilidades)\s*:?\s*$",
            "",
            skills_section,
            flags=re.MULTILINE,
        ).strip()

        if body:
            parts = re.split(r"[,;•\n]+", body)
            for part in parts:
                item = part.strip()
                if not item:
                    continue
                item = re.sub(r"\s+", " ", item)

                # Mantém apenas itens que batem com keywords conhecidas (robustez).
                for kw, rx in TECH_REGEXES.items():
                    if rx.search(item):
                        # Posição exata não é essencial para parsing; é para ordenar.
                        found.append((text.lower().find(item.lower()), kw))
                        break

    if not found:
        for kw, rx in TECH_REGEXES.items():
            m = rx.search(text)
            if m:
                found.append((m.start(), kw))

    found.sort(key=lambda x: x[0])

    # Dedup mantendo primeira ocorrência.
    seen: set[str] = set()
    ordered: List[str] = []
    for _pos, kw in found:
        kw_norm = kw.strip()
        if kw_norm.lower() not in seen:
            seen.add(kw_norm.lower())
            ordered.append(kw_norm)
    return ordered

