# Plano: Limpeza Total + Frontend React Real (BRBPO V3)

## Problema
O frontend **Next.js nunca foi construído**. A pasta `frontend/` contém apenas um `next_help.txt`. O sistema ainda depende do **Streamlit** (legado). Precisamos limpar o lixo e construir o React de verdade.

## O Que FICA (Backend Python — Essencial)
```
src/
├── core/            ✅ Domínio (entidades, interfaces)
├── application/     ✅ Serviços de triagem
├── infrastructure/  ✅ AI, DB, Parsers, Security
├── interface/
│   ├── api.py       ✅ FastAPI (motor da V3)
│   └── cli.py       ✅ CLI útil para testes
├── main.py          ✅ Entry point
```

## O Que SAI (Lixo / Legado)
| Arquivo/Pasta | Motivo |
|---|---|
| `src/interface/web.py` | Streamlit legado — substituído pelo React |
| `.streamlit/` | Config do Streamlit — não mais necessário |
| `run.bat` | Script antigo do Streamlit |
| `run_v3.bat` | Script híbrido que ainda usava Streamlit |
| `extractors.py` | Arquivo solto na raiz — já existe em parsers |
| `refactor-triage-system.md` | Doc de refactoring antiga |
| `test.pdf` | Arquivo de teste na raiz |
| `frontend/next_help.txt` | Lixo do create-next-app que falhou |
| `tmp/` | Pasta temporária |
| `__pycache__/` (raiz) | Cache Python |
| `.mypy_cache/` | Cache do mypy |
| `.pytest_cache/` | Cache do pytest |
| `.ruff_cache/` | Cache do ruff |

## O Que SERÁ CONSTRUÍDO (Frontend React)
```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx        # Shell: Sidebar + Main
│   │   ├── page.tsx          # Dashboard (métricas)
│   │   ├── jobs/page.tsx     # Gestão de Vagas
│   │   ├── triage/page.tsx   # Upload + Processamento
│   │   └── talent/page.tsx   # Talent Pool (analytics)
│   ├── components/
│   │   ├── Sidebar.tsx       # Nav lateral DevTask-style
│   │   ├── JobCard.tsx       # Card de vaga
│   │   ├── CandidateRow.tsx  # Linha do talent pool
│   │   └── MetricCard.tsx    # Card de métrica
│   └── lib/
│       └── api.ts            # Cliente HTTP para FastAPI
├── tailwind.config.ts
├── package.json
└── next.config.ts
```

## Script de Inicialização (Novo)
```
run.bat → Inicia FastAPI (porta 8000) + Next.js dev (porta 3000)
```

## Verificação
- FastAPI docs acessível em `localhost:8000/docs`
- React rodando em `localhost:3000`
- Dashboard carregando dados reais da API
