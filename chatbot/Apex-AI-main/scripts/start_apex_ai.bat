@echo off
echo ==============================================
echo   Apex AI Local Deployment Startup Script
echo ==============================================

echo [1] Ensuring virtual environment exists...
if not exist .venv (
    python -m venv .venv
)

echo [2] Checking Dependencies...
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt

echo [3] Starting Ollama Backend Engine...
start cmd /k "ollama serve"

echo Waiting for Ollama to initialize...
timeout /t 5 /nobreak > nul

echo [4] Ensuring Gemma Model is loaded...
ollama pull gemma:2b

echo [5] Starting FastAPI Backend...
start cmd /k "call .venv\Scripts\activate.bat && cd backend && uvicorn api.app:app --reload --host 0.0.0.0 --port 8000"

echo [6] Starting Streamlit Frontend...
start cmd /k "call .venv\Scripts\activate.bat && cd frontend\streamlit && streamlit run app.py"

echo ==============================================
echo Apex AI is now running! 
echo Frontend: http://localhost:8501
echo Backend: http://localhost:8000/docs
echo ==============================================
