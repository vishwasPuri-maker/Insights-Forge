#!/bin/bash
echo "=============================================="
echo "  Apex AI Local Deployment Startup Script"
echo "=============================================="

echo "[1] Checking Dependencies..."
python3 -m pip install -r requirements.txt

echo "[2] Starting Ollama Backend Engine..."
ollama serve &
OLLAMA_PID=$!
sleep 5

echo "[3] Ensuring Gemma Model is loaded..."
ollama pull gemma:2b

echo "[4] Starting FastAPI Backend..."
cd backend/api && uvicorn app:app --reload --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

echo "[5] Starting Streamlit Frontend..."
cd ../../frontend/streamlit && streamlit run app.py &
STREAMLIT_PID=$!

echo "=============================================="
echo "Apex AI is now running!"
echo "Frontend: http://localhost:8501"
echo "Backend: http://localhost:8000/docs"
echo "Press Ctrl+C to stop all services."
echo "=============================================="

trap "kill $OLLAMA_PID $FASTAPI_PID $STREAMLIT_PID" EXIT
wait
