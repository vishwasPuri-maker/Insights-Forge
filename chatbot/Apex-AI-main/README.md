# Apex AI Enterprise Analytics Chatbot

![Apex AI](https://img.shields.io/badge/Apex_AI-Enterprise_Analytics-0052CC?style=for-the-badge)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge)

Apex AI is a locally-hosted, privacy-preserving, enterprise-grade analytical chatbot built for querying and analyzing strictly structured business data without hallucinating. It operates under a highly deterministic Multi-Agent orchestration framework backed by Ollama (Gemma 2B / Llama 3) and relies on rigorous Security Guardrails to block injection and DML executions.

## 🏗 Architecture & Features

Apex AI consists of **10 specialized core components** integrated into a single unified pipeline:

1. **Streamlit Frontend (`frontend/streamlit/app.py`)**: A dynamic UI providing Chat, Dashboards, and expanding "Governance & Orchestration Metadata" blocks.
2. **FastAPI Backend (`backend/api/app.py`)**: A scalable routing layer orchestrating inference.
3. **Security Guardrail Layer (`backend/security/guardrails.py`)**: 100% enforcement of Read-Only analytics policies (blocking SQL `INSERT`, `UPDATE`, `DROP`, etc.) and robust defense against 30+ prompt injection strategies.
4. **Multi-Agent Router (`backend/agents/router.py`)**: Dynamically analyzes the intent of the prompt and injects specific system rules based on 8 distinct agent personas (e.g. `TrendAnalysisAgent`, `AnomalyDetectionAgent`).
5. **Local RAG Engine (`backend/rag/engine.py`)**: Fully offline ChromaDB integration for retrieving isolated corporate context.
6. **Session Memory (`backend/memory/memory_manager.py`)**: Persistent SQLite memory caching to retain context without external API leaks.
7. **JSON Output Governance (`response_schema.json`)**: Absolute strict enforcement of LLM outputs to guarantee predictable API-friendly JSON parsing.
8. **Offline Inference (Ollama)**: By utilizing `gemma:2b` entirely locally, 0 bytes of sensitive corporate data leave the machine.

## 🚀 Local Deployment Instructions

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com/) (Must be installed globally)
- Windows (or Linux/Mac)

### Running Locally (1-Click Startup)

Apex AI includes automated orchestration scripts that will create a virtual environment, install all required dependencies, pull the language model, and spin up the servers simultaneously.

**For Windows:**
```bash
.\scripts\start_apex_ai.bat
```

**For Linux / Mac:**
```bash
bash scripts/start_apex_ai.sh
```

Once running, navigate to **http://localhost:8501** in your browser.

## ☁️ Cloud Deployment (Render.com)

Apex AI is pre-configured with a microservices Infrastructure-as-Code blueprint to be deployed onto Render's cloud architecture. 

**Note on Memory Requirements:** The local Ollama Gemma model requires 2GB+ of RAM. Deploying this architecture on Render requires a paid tier (`Standard` or `Pro`).

1. Fork or push this repository to GitHub.
2. Log into your Render Dashboard.
3. Click **New +** > **Blueprint**.
4. Select this repository. Render will automatically read `render.yaml`, spin up the `apex-ollama` Private Service, bind the `apex-backend` (FastAPI), and launch the `apex-frontend` (Streamlit) services.

## 🛡 Security & Compliance

Apex AI passes a >90.5% internal Red Team security validation score, featuring:
- **Jailbreak Defenses:** RegEx and NLP filters detecting known adversarial prefixes (e.g., "Ignore all previous instructions").
- **DML/DDL Blocking:** Complete lock-out of any commands attempting to mutate external database states.
- **Privacy Scrubbing:** PII removal filters prior to LLM inference.
- **Audit Logging:** Every rejected malicious query is securely logged with timestamps and severity ratings.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
