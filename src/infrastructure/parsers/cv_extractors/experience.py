"""
experience.py

Extração de experiências profissionais do CV.
"""

from __future__ import annotations

import re
from typing import List, Optional

from src.infrastructure.parsers.cv_extractors.models import Experience
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
    """
    Quebra uma seção em entradas prováveis usando linhas em branco e bullets.
    """
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


def parse_experiences(cv_text: str, target_position: Optional[int] = None) -> List[Experience]:
    text = normalize_text(cv_text)

    all_headings = [
        "Experiência",
        "Experience",
        "Experiência Profissional",
        "Professional Experience",
        "Formação",
        "Education",
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
        headings=[
            "Experiência",
            "Experience",
            "Experiência Profissional",
            "Professional Experience",
            "Experiencias",
        ],
        all_headings_for_cut=all_headings,
        target_position=target_position,
    )
    if not section:
        return []

    entries = _split_entries(section)
    experiences: List[Experience] = []

    # Palavras comuns de cargo (PT/EN) para melhorar detecção.
    job_role_keywords = re.compile(
        r"(?i)\b("
        r"analista|desenvolvedor|engenheiro|developer|software|sênior|senior|pleno|junior|lead|manager|coordenador|coordinator|"
        r"consultor|consultant|architect|arquiteto|product|produto|data|cientista|science|ml|machine learning|"
        r"backend|frontend|full[- ]?stack|fullstack"
        r")\b"
    )

    for entry in entries:
        entry_clean = re.sub(r"\s+", " ", entry).strip()
        if not entry_clean:
            continue

        if re.search(r"(?i)^(experi[eê]ncia|experience)\s*:", entry_clean):
            continue

        duration = _extract_period(entry_clean)
        without_dates = PERIOD_RE.sub("", entry_clean).strip()

        entry_lines = [ln.strip() for ln in without_dates.split("\n") if ln.strip()]
        if not entry_lines:
            entry_lines = [without_dates]

        company = ""
        role = ""
        description_parts: List[str] = []

        for ln in entry_lines[:4]:
            if not role and job_role_keywords.search(ln):
                role = ln
            if not company and re.search(
                r"(?i)\b(ltda|s\.a\.|sa\.|inc\.|gmbh|ltd\.|corp\.|s\.p\.a\.|sa)\b",
                ln,
            ):
                company = ln

        if not company and entry_lines:
            company = entry_lines[0]
        if not role:
            role = entry_lines[1] if len(entry_lines) > 1 else entry_lines[0]

        company = re.sub(r"\s*[|•-]\s*", " ", company).strip()
        role = role.strip()

        for ln in entry_lines:
            ln_norm = ln.strip()
            if ln_norm == company or ln_norm == role:
                continue
            description_parts.append(ln_norm)

        description = "\n".join(description_parts).strip() if description_parts else None
        description = description if description and description.strip() else None

        if not company.strip() or not role.strip():
            continue

        try:
            experiences.append(
                Experience(company=company, role=role, duration=duration, description=description)
            )
        except ValueError:
            continue

    return experiences

