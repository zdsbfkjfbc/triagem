# Triagem

> Sistema corporativo avançado para triagem automatizada de currículos utilizando Inteligência Artificial, Parseamento Estrutural e Matching Semântico. Desenvolvido para escalar pipelines de recrutamento com precisão cirúrgica.

## 🚀 Quick Start

O sistema foi arquitetado para desenvolvimento contínuo e escalável utilizando um ponto de entrada unificado. 

**Requisitos Essenciais:**
- Python 3.10+
- Node.js 18+
- Chave de API do OpenRouter (inserida no arquivo `.env` protegido)

**Como iniciar a aplicação localmente:**

No diretório raiz (Windows), execute o orquestrador para iniciar simultaneamente o Backend e o Frontend:
```cmd
.\run.bat
```
*Isto irá compilar a aplicação e expor o painel em `http://localhost:3000` bem como a documentação Swagger da API em `http://localhost:8000/docs`.*

---

## ✨ Features

- **Triagem em Duas Fases Automáticas (Performance-First):**  
  Aplica uma extração e pontuação lexical rápida inicial. Mutações e auditorias com LLMs avançados são disparadas **apenas** quando o candidato atinge o *Threshold* de `7.5` de fit para aquela vaga.
- **Agnóstico a LLMs (OpenRouter Integration):**  
  Suporta +26 modelos de alto raciocínio de graça e pagos (incluindo Gemini, Claude-3.5 e Llama) garantindo ZERO vendor-lock in.
- **Extração Semântica Criteriosa (Língua Portuguesa Enforced):**  
  Detecção inteligente de hard skills, soft skills, proficiência em idiomas e alertas sobre eventuais inconsistências no histórico profissional do candidato, obrigando o retorno do robô estritamente em Português do Brasil.
- **Painel Editorial de Revisão (Claude-Style Clean UI):**  
  Interface em Modo Pesquisa (Research Mode). Limpa, veloz e minimalista; ajuda recrutadores a visualizarem milhares de currículos sem cansaço visual, substituindo o excesso de cores por um design utilitário.
- **Full CRUD & SQLite Modularizado:**  
  Persistência de eventos e banco de dados *Zero-config* (embeddable). Facilidade completa para deletar processos seletivos e candidatos descartados instantaneamente.

---

## 🏗️ Architecture Stack

Nossas escolhas seguiram um padrão Clean Architecture priorizando **Responsabilidade Única** e **Separação de Domínios**.

| Camada | Tecnologia | Função |
|----------|-------------|---------|
| **Backend** | FastAPI (Python) | API REST extremamente rápida, assíncrona e documentada |
| **Banco de Dados** | SQLite com SQLAlchemy | Modelagem relacional para Jobs e Candidatos |
| **Integração IA** | LlamaIndex / OpenRouter | Conexão semântica via Prompt Providers customizados |
| **Frontend** | Next.js (TS React) | App Router, SSR/CSR, e gerência paralela de estados |
| **Styling** | TailwindCSS v4 | Utility first, tipografia de pesquisa e responsividade extrema |

---

## 📂 Visão Geral de Diretórios

```text
/Triage
├── src/                      # Backend Core Application
│   ├── application/          # Regras de Negócio e Serviços (Ex: triage_service.py)
│   ├── infrastructure/       # Banco de Dados (Repository, SQLite) e IA (OpenRouter)
│   ├── interface/            # Rotas REST da FastAPI (api.py)
│   └── lib/                  # Utilitários de parsing (PDF Reader) e Helpers
├── frontend/                 # Frontend Modern App
│   ├── src/app/              # Next.js App Router (Dashboard, Core UI)
│   ├── src/components/       # Componentes ShadCN e Botões modulares
│   └── src/lib/              # Requisições API e Client Side utils
├── .agent/                    # (Ignorado no Git) Conhecimento Arquitetural e Prompts Internos
└── run.bat                   # Entrypoint Global de Execução
```

---

## 🛡️ Segurança e Práticas do Repositório

Este repositório atinge altos níveis de conformidade de engenharia de software:
1. **Blindagem de Segredos:** Arquivos iterativos, `__pycache__`, pastas `node_modules` massivas, e arquivos `.env` jamais são commitados. Nosso robô possui `.gitignore` reforçado.
2. **Separação Lógica de Logs:** Documentações da estratégia de agentes internos (`.agent/`) são geridas puramente fora do escopo visível da equipe comum.
3. **Database Localized:** O Banco de Dados operacional não existe no GitHub para proteger o PII (Personally Identifiable Information) dos candidatos importados durante o debug de desenvolvimento.

---

## ⚙️ License
MIT - BRBPO Recruitment Core Systems.
