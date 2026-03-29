"""
education.py

Extração de formação acadêmica.
"""

from __future__ import annotations

import re
from typing import List, Optional

from src.infrastructure.parsers.cv_extractors.models import EducationItem
from src.infrastructure.parsers.cv_extractors.patterns import PERIOD_RE
from src.infrastructure.parsers.cv_extractors.sectioning import extract_section_text, normalize_text


def _extract_period(duration_text: str) -> Optional[str]:
    if not duration_text:
        return None
    m = PERIOD_RE.search(duration_text)
    if not m:
        return None
    start = m.group("start").strip()
    end = m.group("end").strip()

    end_norm = end
    if re.search(r"(?i)\b(atual|present)\b", end):
        end_norm = "Atual" if re.search(r"(?i)atual", end) else "Present"

    return f"{start} - {end_norm}"


def _split_entries(section_text: str) -> List[str]:
    lines = [ln.rstrip() for ln in section_text.split("\n")]
    cleaned_lines: List[str] = []
    for ln in lines:
        cleaned_lines.append("" if not ln.strip() else ln)

    joined = "\n".join(cleaned_lines)
    joined = re.sub(r"(?m)^\s*[-•*]\s+", "- ", joined)

    chunks = [c.strip() for c in re.split(r"\n\s*\n", joined) if c.strip()]
    if len(chunks) <= 1:
        chunks2 = [c.strip() for c in re.split(r"(?m)^\s*-\s+", joined) if c.strip()]
        return chunks2 if len(chunks2) > 1 else chunks
    return chunks


def parse_education(cv_text: str, target_position: Optional[int] = None) -> List[EducationItem]:
    text = normalize_text(cv_text)

    all_headings = [
        "Formação",
        "Education",
        "Experiência",
        "Experience",
        "Skills",
        "Habilidades",
        "Idiomas",
        "Languages",
        "Certificações",
        "Certificacoes",
        "Projetos",
        "Projects",
    ]

    section = extract_section_text(
        text,
        headings=["Formação", "Education"],
        all_headings_for_cut=all_headings,
        target_position=target_position,
    )
    if not section:
        return []

    entries = _split_entries(section)
    items: List[EducationItem] = []

    degree_keywords = re.compile(
        r"(?i)\b(engenharia|bacharel|licen[çc]a|mestrado|doutorado|mba|b\.?s\.?|m\.?s\.?|degree|computer|science|"
        r"informatica|informática|tecnologia|t\.i\.|an[aá]lise)\b"
    )

    for entry in entries:
        entry_clean = re.sub(r"\s+", " ", entry).strip()
        if not entry_clean:
            continue

        duration = _extract_period(entry_clean) or None
        without_dates = PERIOD_RE.sub("", entry_clean).strip()
        lines = [ln.strip() for ln in without_dates.split("\n") if ln.strip()]
        if not lines:
            lines = [without_dates]

        institution = lines[0]
        degree: Optional[str] = None
        details: Optional[str] = None

        if len(lines) > 1 and degree_keywords.search(lines[1]):
            degree = lines[1]
            details = "\n".join(lines[2:]).strip() or None
        else:
            for ln in lines[1:4]:
                if degree_keywords.search(ln):
                    degree = ln
                    break

            details = "\n".join([ln for ln in lines[1:] if ln != degree]).strip() or None

        try:
            items.append(
                EducationItem(
                    institution=institution.strip(),
                    degree=degree,
                    duration=duration,
                    details=details,
                )
            )
        except ValueError:
            continue

    return items

