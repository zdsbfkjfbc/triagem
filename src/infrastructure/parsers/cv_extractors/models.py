"""
models.py

Dataclasses e validação do formato JSON retornado pela extração do CV.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, TypedDict


@dataclass(frozen=True)
class ContactInfo:
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    name: Optional[str] = None


@dataclass(frozen=True)
class Experience:
    company: str
    role: str
    duration: Optional[str] = None
    description: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.company, str) or not self.company.strip():
            raise ValueError("Experience.company deve ser uma string não vazia.")
        if not isinstance(self.role, str) or not self.role.strip():
            raise ValueError("Experience.role deve ser uma string não vazia.")
        if self.duration is not None and not isinstance(self.duration, str):
            raise ValueError("Experience.duration deve ser None ou string.")
        if self.description is not None and not isinstance(self.description, str):
            raise ValueError("Experience.description deve ser None ou string.")


@dataclass(frozen=True)
class EducationItem:
    institution: str
    degree: Optional[str] = None
    duration: Optional[str] = None
    details: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.institution, str) or not self.institution.strip():
            raise ValueError("EducationItem.institution deve ser uma string não vazia.")
        if self.degree is not None and not isinstance(self.degree, str):
            raise ValueError("EducationItem.degree deve ser None ou string.")
        if self.duration is not None and not isinstance(self.duration, str):
            raise ValueError("EducationItem.duration deve ser None ou string.")
        if self.details is not None and not isinstance(self.details, str):
            raise ValueError("EducationItem.details deve ser None ou string.")


@dataclass(frozen=True)
class LanguageItem:
    language: str
    level: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.language, str) or not self.language.strip():
            raise ValueError("LanguageItem.language deve ser string não vazia.")
        if self.level is not None and not isinstance(self.level, str):
            raise ValueError("LanguageItem.level deve ser None ou string.")


@dataclass(frozen=True)
class CertificationItem:
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    details: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("CertificationItem.name deve ser string não vazia.")
        if self.issuer is not None and not isinstance(self.issuer, str):
            raise ValueError("CertificationItem.issuer deve ser None ou string.")
        if self.date is not None and not isinstance(self.date, str):
            raise ValueError("CertificationItem.date deve ser None ou string.")
        if self.details is not None and not isinstance(self.details, str):
            raise ValueError("CertificationItem.details deve ser None ou string.")


@dataclass(frozen=True)
class ProjectItem:
    name: str
    tech: List[str] = field(default_factory=list)
    description: Optional[str] = None
    link: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("ProjectItem.name deve ser string não vazia.")
        if not isinstance(self.tech, list) or any(not isinstance(x, str) for x in self.tech):
            raise ValueError("ProjectItem.tech deve ser uma lista de strings.")
        if self.description is not None and not isinstance(self.description, str):
            raise ValueError("ProjectItem.description deve ser None ou string.")
        if self.link is not None and not isinstance(self.link, str):
            raise ValueError("ProjectItem.link deve ser None ou string.")


@dataclass(frozen=True)
class CVData:
    """
    Estrutura final do CV extraído.

    Observação: para JSON, campos opcionais serão serializados como `null`.
    """

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    experiences: List[Experience] = field(default_factory=list)
    skills_technical: List[str] = field(default_factory=list)
    education: List[EducationItem] = field(default_factory=list)
    languages: List[LanguageItem] = field(default_factory=list)
    certifications: List[CertificationItem] = field(default_factory=list)
    projects: List[ProjectItem] = field(default_factory=list)

    def to_json_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "experiences": [asdict(e) for e in self.experiences],
            "skills_technical": list(self.skills_technical),
            "education": [asdict(e) for e in self.education],
            "languages": [asdict(lang) for lang in self.languages],
            "certifications": [asdict(c) for c in self.certifications],
            "projects": [asdict(p) for p in self.projects],
        }


class ExtractionError(ValueError):
    """Erro para sinalizar falha de validação/extração."""


class ExtractedCVSchema(TypedDict, total=False):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    experiences: List[Dict[str, Any]]
    skills_technical: List[str]
    education: List[Dict[str, Any]]
    languages: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]


def validate_extracted_cv_data(data: Dict[str, Any]) -> None:
    """
    Valida o shape mínimo do JSON retornado pela extração.
    """

    if not isinstance(data, dict):
        raise ExtractionError("data deve ser um dict.")

    def _opt_str(k: str) -> None:
        if k in data and data[k] is not None and not isinstance(data[k], str):
            raise ExtractionError(f"data['{k}'] deve ser string ou None.")

    _opt_str("name")
    _opt_str("email")
    _opt_str("phone")
    _opt_str("location")

    for k in ["skills_technical", "experiences", "education", "languages", "certifications", "projects"]:
        if k not in data:
            raise ExtractionError(f"data deve conter a chave '{k}'.")

    if not isinstance(data["skills_technical"], list) or any(not isinstance(x, str) for x in data["skills_technical"]):
        raise ExtractionError("data['skills_technical'] deve ser uma lista de strings.")

    for k in ["experiences", "education", "languages", "certifications", "projects"]:
        if not isinstance(data[k], list) or any(not isinstance(x, dict) for x in data[k]):
            raise ExtractionError(f"data['{k}'] deve ser uma lista de dicts.")

