# Insights Forge Backend

Production backend for the Insights Forge AI Business Intelligence Platform.

## Tech Stack

- FastAPI
- SQLAlchemy 2.0
- PostgreSQL (Neon)
- Alembic
- Pydantic Settings
- JWT Authentication
- Redis
- Celery

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file using `.env.example`.

Run the application:

```bash
uvicorn app.main:app --reload
```

Swagger:

```
http://127.0.0.1:8000/docs
```

## Database

Generate migration:

```bash
alembic revision --autogenerate -m "message"
```

Apply migration:

```bash
alembic upgrade head
```