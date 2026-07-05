import subprocess
import sys
import time
import threading
import os

def run_command(command, prefix):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
    for line in iter(process.stdout.readline, ''):
        print(f"[{prefix}] {line.strip()}")
    process.stdout.close()
    process.wait()

def start_backend():
    print("Starting FastAPI Backend...")
    # Make sure we use the virtual environment if it exists, otherwise python
    python_cmd = r".venv\Scripts\python.exe" if os.path.exists(r".venv\Scripts\python.exe") else "python"
    run_command(f"{python_cmd} -m uvicorn backend.api.app:app --host 0.0.0.0 --port 8000", "BACKEND")

def start_frontend():
    print("Starting Streamlit Frontend...")
    python_cmd = r".venv\Scripts\python.exe" if os.path.exists(r".venv\Scripts\python.exe") else "python"
    run_command(f"{python_cmd} -m streamlit run frontend/streamlit/app.py --server.port 8501", "FRONTEND")

if __name__ == "__main__":
    print("========================================================")
    print("INITIALIZING APEX AI UNIFIED ENVIRONMENT")
    print("========================================================")
    
    backend_thread = threading.Thread(target=start_backend)
    frontend_thread = threading.Thread(target=start_frontend)
    
    backend_thread.daemon = True
    frontend_thread.daemon = True
    
    backend_thread.start()
    time.sleep(3) # Give backend a moment to spin up
    frontend_thread.start()
    
    time.sleep(2)
    print("\n========================================================")
    print("DEPLOYMENT SUCCESSFUL!")
    print("ACCESS APEX AI HERE: http://localhost:8501")
    print("========================================================\n")
    print("(Press Ctrl+C to stop both servers)\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Apex AI Unified Environment...")
        sys.exit(0)
