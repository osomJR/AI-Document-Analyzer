from fastapi import FastAPI
from backend.route import router as ai_router

app = FastAPI(
    title="AI Document Analyzer",
    description="Privacy-first, contract-enforced document processing API",
    version="1.0.0"
)

# Register routes
app.include_router(
    ai_router,
    prefix="/api/v1",
    tags=["v1"]
)

# Health check (important for deployment)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "AI Document Analyzer"
    }
