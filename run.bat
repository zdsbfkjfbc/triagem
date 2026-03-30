@echo off
setlocal

echo ==========================================
echo    BRBPO TRIAGE ENTERPRISE V3
echo    Backend: FastAPI :8000
echo    Frontend: Next.js :3000
echo ==========================================
echo.

if not exist .venv\Scripts\python.exe (
  echo [setup] Ambiente virtual nao encontrado. Criando .venv...
  py -m venv .venv
)

if not exist .venv\Scripts\python.exe (
  echo [erro] Nao foi possivel criar/achar o Python em .venv\Scripts\python.exe
  exit /b 1
)

echo [setup] Sincronizando dependencias Python...
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt
if errorlevel 1 (
  echo [erro] Falha ao instalar dependencias Python.
  exit /b 1
)

echo [1/2] Iniciando Backend (FastAPI)...
start "BRBPO-API" cmd /k "cd /d %~dp0 && .venv\Scripts\python -m uvicorn src.interface.api:app --host 0.0.0.0 --port 8000 --reload"

if not exist frontend\node_modules (
  echo [setup] Instalando dependencias frontend via npm install...
  cd /d %~dp0\frontend
  npm install
  if errorlevel 1 (
    echo [erro] Falha ao instalar dependencias frontend.
    exit /b 1
  )
  cd /d %~dp0
)

where npm >nul 2>nul
if errorlevel 1 (
  echo [erro] npm nao encontrado no PATH. Instale Node.js 18+ e tente novamente.
  exit /b 1
)

echo [2/2] Iniciando Frontend (React)...
start "BRBPO-WEB" cmd /k "cd /d %~dp0\frontend && npm run dev"
