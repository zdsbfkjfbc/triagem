# Triagem

Sistema corporativo para triagem automatizada de currículos com IA, parseamento estrutural e matching semântico.

## Quick Start

Requisitos:
- Python 3.10+
- Node.js 18+

Na raiz do projeto (Windows), execute:

```cmd
.\run.bat
```

Isso inicia:
- Backend FastAPI em `http://localhost:8000`
- Frontend Next.js em `http://localhost:3000`
- Swagger em `http://localhost:8000/docs`

## Primeira execução (máquina nova)

1. Clone o repositório.
2. Abra um terminal na raiz.
3. Execute `.\run.bat`.
4. Em outro terminal, crie o usuário admin inicial:

```cmd
.\.venv\Scripts\python scripts\seed_admin.py
```

5. Faça login em `http://localhost:3000` com:
- usuário: `admin`
- senha: `admin123`

## Se algo falhar

- Erro de `py` não reconhecido: instale Python e marque "Add Python to PATH".
- Erro de `npm`: instale Node.js 18+ e rode `.\run.bat` novamente.
- Porta ocupada (`3000` ou `8000`): feche processos antigos usando essas portas.
- Login falhando: rode novamente `.\.venv\Scripts\python scripts\seed_admin.py`.

## Stack

- Backend: FastAPI
- Banco: SQLite + SQLAlchemy
- Frontend: Next.js + React
- Styling: TailwindCSS
- IA: OpenRouter

## Estrutura

```text
/Triage
├── src/
├── frontend/
├── scripts/
├── config/
└── run.bat
```

## License

MIT - BRBPO Recruitment Core Systems.
