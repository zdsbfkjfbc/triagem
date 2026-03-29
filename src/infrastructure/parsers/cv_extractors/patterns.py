"""
patterns.py

Regex e palavras-chave reutilizadas pelos parsers do currículo.
"""

from __future__ import annotations

import re
from typing import Dict, Sequence


EMAIL_RE = re.compile(
    r"(?P<email>[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})",
    re.IGNORECASE,
)

# Aceita formatos comuns de telefone no BR e internacional.
PHONE_RE = re.compile(r"(?P<phone>\+?\d[\d\-\s().]{7,}\d)")

# Durações/períodos: "Jan 2020 - Mar 2022", "2020 - 2022", "2022 - Atual"
MONTHS_PT = "jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez"
MONTHS_EN = (
    "jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
    "aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
)

MONTH_RE = rf"(?:{MONTHS_PT}|{MONTHS_EN})"
YEAR_RE = r"(?:19\d{2}|20\d{2})"
PRESENT_RE = r"(?:atual|present|hoje|agora)"

PERIOD_RE = re.compile(
    rf"(?P<start>(?:{MONTH_RE}\s*)?{YEAR_RE})\s*(?:[-–—to]\s*)?(?P<end>(?:{MONTH_RE}\s*)?(?:{YEAR_RE}|{PRESENT_RE}))",
    re.IGNORECASE,
)


TECH_KEYWORDS: Sequence[str] = (
    # Linguagens
    "Python",
    "Django",
    "Flask",
    "FastAPI",
    "Pydantic",
    "JavaScript",
    "TypeScript",
    "Node.js",
    "SQL",
    "Java",
    "C#",
    "C++",
    # Bancos e caches
    "PostgreSQL",
    "MySQL",
    "SQLite",
    "MongoDB",
    "Redis",
    # Infra / DevOps
    "Docker",
    "Kubernetes",
    "AWS",
    "GCP",
    "Azure",
    "Terraform",
    "Ansible",
    "CI/CD",
    "Linux",
    # Web / front-end
    "React",
    "Next.js",
    "HTML",
    "CSS",
    # Dados / ML
    "Pandas",
    "NumPy",
    "scikit-learn",
    "sklearn",
    "Pytest",
    "Celery",
    "RabbitMQ",
    "Kafka",
    # APIs / Arquitetura
    "REST",
    "REST API",
    "GraphQL",
    "OAuth",
    "JWT",
    "RESTful",
    "Microservices",
    "Microservice",
    "API",
    # Qualidade/automação
    "Git",
    "GitHub",
    "Selenium",
    "Playwright",
    "Jest",
    # ORM
    "SQLAlchemy",
)


def _build_keyword_regex(keyword: str) -> re.Pattern[str]:
    escaped = re.escape(keyword)
    if " " in keyword:
        # Permite casamento direto da sequência.
        return re.compile(rf"(?i){escaped}")
    return re.compile(rf"(?i)\b{escaped}\b")


TECH_REGEXES: Dict[str, re.Pattern[str]] = {k: _build_keyword_regex(k) for k in TECH_KEYWORDS}

