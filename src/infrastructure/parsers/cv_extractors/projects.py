"""
projects.py

Extração de projetos relevantes do CV.
"""

from __future__ import annotations

import re
from typing import List, Optional

from src.infrastructure.parsers.cv_extractors.models import ProjectItem
from src.infrastructure.parsers.cv_extractors.patterns import TECH_REGEXES
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


def parse_projects(cv_text: str, target_position: Optional[int] = None) -> List[ProjectItem]:
    text = normalize_text(cv_text)

    all_headings = [
        "Projetos",
        "Projects",
        "Experiência",
        "Experience",
        "Formação",
        "Education",
        "Skills",
        "Habilidades",
        "Idiomas",
        "Languages",
        "Certificações",
        "Certificacoes",
    ]

    section = extract_section_text(
        text,
        headings=["Projetos", "Projects"],
        all_headings_for_cut=all_headings,
        target_position=target_position,
    )
    if not section:
        return []

    entries = _split_entries(section)
    projects: List[ProjectItem] = []

    url_re = re.compile(r"https?://[^\s)]+", re.IGNORECASE)

    for entry in entries:
        entry_clean = entry.strip()
        if not entry_clean:
            continue

        link_m = url_re.search(entry_clean)
        link = link_m.group(0) if link_m else None
        entry_wo_link = url_re.sub("", entry_clean).strip()

        lines = [ln.strip() for ln in entry_wo_link.split("\n") if ln.strip()]
        if not lines:
            continue

        name = lines[0].strip(" -•*")

        tech_found: List[str] = []
        for kw, rx in TECH_REGEXES.items():
            if rx.search(entry_wo_link):
                tech_found.append(kw)

        dedup_tech: List[str] = []
        seen: set[str] = set()
        for t in tech_found:
            if t.lower() in seen:
                continue
            seen.add(t.lower())
            dedup_tech.append(t)

        desc_parts = lines[1:]
        description = "\n".join(desc_parts).strip() if desc_parts else None
        description = description if description and description.strip() else None

        try:
            projects.append(ProjectItem(name=name, tech=dedup_tech, description=description, link=link))
        except ValueError:
            continue

    return projects

