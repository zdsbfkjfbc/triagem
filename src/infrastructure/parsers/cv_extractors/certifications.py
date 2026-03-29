"""
certifications.py

Extração de certificações.
"""

from __future__ import annotations

import re
from typing import List, Optional

from src.infrastructure.parsers.cv_extractors.models import CertificationItem
from src.infrastructure.parsers.cv_extractors.sectioning import extract_section_text, normalize_text


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


def parse_certifications(cv_text: str, target_position: Optional[int] = None) -> List[CertificationItem]:
    text = normalize_text(cv_text)

    all_headings = [
        "Certificações",
        "Certificacoes",
        "Idiomas",
        "Languages",
        "Formação",
        "Education",
        "Experiência",
        "Experience",
        "Projetos",
        "Projects",
        "Skills",
        "Habilidades",
    ]

    section = extract_section_text(
        text,
        headings=["Certificações", "Certificacoes"],
        all_headings_for_cut=all_headings,
        target_position=target_position,
    )
    if not section:
        return []

    entries = _split_entries(section)
    items: List[CertificationItem] = []

    for entry in entries:
        entry_clean = re.sub(r"\s+", " ", entry).strip()
        if not entry_clean:
            continue

        date_match = re.search(r"\b(19\d{2}|20\d{2})\b", entry_clean)
        date = date_match.group(0) if date_match else None

        parts = [p.strip() for p in re.split(r"\s*(?:-|:)\s*", entry_clean) if p.strip()]
        if not parts:
            continue

        name = parts[0]
        issuer: Optional[str] = None
        details: Optional[str] = None

        if len(parts) >= 2:
            remaining: List[str] = []
            for p in parts[1:]:
                if date and re.fullmatch(rf"{re.escape(date)}", p):
                    continue
                remaining.append(p)

            if remaining:
                issuer = remaining[0]
                if len(remaining) > 1:
                    details = " - ".join(remaining[1:])

        name = name.strip(" -•*")
        issuer = issuer.strip() if issuer else None
        details = details.strip() if details else None

        try:
            items.append(CertificationItem(name=name, issuer=issuer, date=date, details=details))
        except ValueError:
            continue

    return items

