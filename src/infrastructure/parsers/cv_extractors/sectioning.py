"""
sectioning.py

Helpers para normalizar texto e extrair seções por headings.
"""

from __future__ import annotations

import re
from typing import List, Optional, Sequence, Tuple


class SectioningError(ValueError):
    """Erro para falhas de normalização/segmentação."""


def _ensure_str(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise SectioningError(f"{field_name} deve ser uma string.")
    return value


def normalize_text(cv_text: str) -> str:
    """
    Normaliza o texto para facilitar regex e segmentação.
    """

    cv_text = _ensure_str(cv_text, "cv_text")
    cv_text = cv_text.replace("\r\n", "\n").replace("\r", "\n")
    cv_text = re.sub(r"[ \t]+", " ", cv_text)
    return cv_text.strip()


def _find_heading_positions(text: str, headings: Sequence[str]) -> List[Tuple[int, str]]:
    """
    Encontra posições (índice de caractere) das seções por headings.
    """

    positions: List[Tuple[int, str]] = []
    for h in headings:
        h_escaped = re.escape(h).replace(r"\ ", r"\s+")
        pattern = re.compile(rf"(?im)^\s*{h_escaped}\s*:?$", re.MULTILINE)
        m = pattern.search(text)
        if m:
            positions.append((m.start(), h))

    positions.sort(key=lambda x: x[0])
    return positions


def extract_section_text(
    cv_text: str,
    headings: Sequence[str],
    all_headings_for_cut: Optional[Sequence[str]] = None,
    target_position: Optional[int] = None,
    max_chars: int = 40000,
) -> Optional[str]:
    """
    Extrai o bloco de texto correspondente a uma seção (heurística).

    - `headings`: nomes/variantes da seção alvo.
    - `all_headings_for_cut`: headings que delimitam o fim da seção (próxima seção).
    - `target_position`: índice no texto para escolher seções quando há múltiplas ocorrências.
    """

    text = normalize_text(cv_text)

    if target_position is not None and (target_position < 0 or target_position >= len(text)):
        # Edge case: não falha, apenas ignora a preferência por contexto.
        target_position = None

    start_positions = _find_heading_positions(text, headings)
    if not start_positions:
        return None

    chosen_start_idx, _chosen_heading = start_positions[0]
    if target_position is not None:
        chosen_start_idx, _chosen_heading = min(start_positions, key=lambda x: abs(x[0] - target_position))

    end_idx = len(text)
    if all_headings_for_cut:
        cut_positions = _find_heading_positions(text, all_headings_for_cut)
        candidates = [pos for pos in cut_positions if pos[0] > chosen_start_idx]
        if candidates:
            end_idx = min(candidates, key=lambda x: x[0])[0]

    section_text = text[chosen_start_idx:end_idx].strip()
    if len(section_text) > max_chars:
        section_text = section_text[:max_chars].rstrip()

    return section_text if section_text else None

