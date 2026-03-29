@echo off
echo ==========================================
echo    BRBPO TRIAGE ENTERPRISE V3
echo    Backend: FastAPI :8000
echo    Frontend: Next.js :3000
echo ==========================================
echo.
echo [1/2] Iniciando Backend (FastAPI)...
start "BRBPO-API" cmd /k "cd /d %~dp0 && .venv\Scripts\python -m uvicorn src.interface.api:app --host 0.0.0.0 --port 8000 --reload"
echo [2/2] Iniciando Frontend (React)...
cd /d %~dp0\frontend
npm run dev
