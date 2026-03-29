"""
contact.py

Extração de dados de contato do currículo.
"""

from __future__ import annotations

import re
from typing import List, Optional

from src.infrastructure.parsers.cv_extractors.models import ContactInfo
from src.infrastructure.parsers.cv_extractors.patterns import EMAIL_RE, PHONE_RE
from src.infrastructure.parsers.cv_extractors.sectioning import normalize_text


def _safe_strip(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    stripped = s.strip()
    return stripped if stripped else None


def extract_emails(cv_text: str) -> List[str]:
    text = normalize_text(cv_text)
    emails = [m.group("email") for m in EMAIL_RE.finditer(text)]

    seen: set[str] = set()
    result: List[str] = []
    for e in emails:
        e_norm = e.strip()
        if e_norm.lower() not in seen:
            seen.add(e_norm.lower())
            result.append(e_norm)
    return result


def _normalize_phone(phone: str) -> str:
    phone = phone.strip()
    has_plus = phone.startswith("+")
    digits = re.sub(r"\D", "", phone)
    return ("+" if has_plus else "") + digits


def extract_phones(cv_text: str) -> List[str]:
    """
    Extrai telefones com validação leve baseada em quantidade de dígitos.
    """
    text = normalize_text(cv_text)
    phones: List[str] = []

    for m in PHONE_RE.finditer(text):
        raw = m.group("phone")
        normalized = _normalize_phone(raw)
        digits_only = re.sub(r"\D", "", normalized)
        if 8 <= len(digits_only) <= 15:
            phones.append(normalized)

    seen: set[str] = set()
    result: List[str] = []
    for p in phones:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result


def extract_name(cv_text: str) -> Optional[str]:
    """
    Heurística para nome: tenta a primeira linha "bem formada" do topo.
    """
    text = normalize_text(cv_text)
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if not lines:
        return None

    candidate_lines = lines[:8]
    for ln in candidate_lines:
        if EMAIL_RE.search(ln) or PHONE_RE.search(ln):
            continue
        if re.search(
            r"(?i)\b(experiencia|experience|skills|formacao|education|idiomas|projetos|certifica)",
            ln,
        ):
            continue

        tokens = [t for t in re.split(r"\s+", ln) if t]
        if len(tokens) >= 2 and re.search(r"[A-Za-zÀ-ÿ]", ln):
            cleaned = re.sub(r"\s{2,}", " ", ln).strip()
            cleaned = cleaned.strip(" -|_•*")
            if len(cleaned) >= 4:
                return cleaned
    return None


def extract_location(cv_text: str) -> Optional[str]:
    """
    Heurística: procura por headings de localização; caso contrário, tenta
    linhas iniciais parecidas com "Cidade/UF".
    """
    text = normalize_text(cv_text)
    headings = ["Localização", "Localizacao", "Location", "Cidade", "City", "Estado", "State"]

    # Procura por linha com "Localização: ..."
    for h in headings:
        pattern = re.compile(rf"(?im)^\s*{re.escape(h)}\s*:\s*(?P<loc>.+?)\s*$")
        m = pattern.search(text)
        if m:
            return _safe_strip(m.group("loc"))

    # Faz varredura nas primeiras linhas procurando cidade/UF.
    # UF (Brasil) - usado para evitar falsos positivos em nomes/cargos.
    uf_pt = (
        "AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MG|MS|MT|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|"
        "SC|SP|SE|TO"
    )
    loc_pattern_sep = re.compile(
        # Captura "São Paulo/SP" e "Campinas - SP"
        rf"(?P<loc>[A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)*\s*(?:/|-)\s*(?:{uf_pt})\b)",
        re.IGNORECASE,
    )
    loc_pattern_space = re.compile(
        # Captura "São Paulo SP" (sem / ou -)
        rf"(?P<loc>[A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)*\s+(?:{uf_pt})\b)",
        re.IGNORECASE,
    )
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    for ln in lines[:12]:
        if EMAIL_RE.search(ln) or PHONE_RE.search(ln):
            continue
        m = loc_pattern_sep.search(ln) or loc_pattern_space.search(ln)
        if m and len(ln) <= 80:
            return _safe_strip(m.group("loc"))
    return None


def extract_contact_info(cv_text: str) -> ContactInfo:
    """
    Extrai nome/email/telefone/localização.
    """
    emails = extract_emails(cv_text)
    phones = extract_phones(cv_text)
    return ContactInfo(
        name=extract_name(cv_text),
        email=emails[0] if emails else None,
        phone=phones[0] if phones else None,
        location=extract_location(cv_text),
    )

