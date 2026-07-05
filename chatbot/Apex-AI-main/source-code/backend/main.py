from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.upload import router as upload_router
from api.dashboard import router as dashboard_router
from api.chat import router as chat_router
from api.datasets import router as datasets_router
from api.middleware import ApexSecurityMiddleware

app = FastAPI(title="Apex AI Enterprise Backend", version="1.0.0")

app.add_middleware(ApexSecurityMiddleware)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api/v1/ingest")
app.include_router(datasets_router, prefix="/api/v1/datasets")
app.include_router(dashboard_router, prefix="/api/v1/analytics")
app.include_router(chat_router, prefix="/api/v1/chat")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "DecisIQ API Gateway"}
