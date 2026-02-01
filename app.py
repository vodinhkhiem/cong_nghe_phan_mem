from fastapi import FastAPI
from analytics import router as analytics_router
from ai import router as ai_router

app = FastAPI(
    title="Learning Analytics & AI API",
    description="Hệ thống Analytics và AI hỗ trợ học tập",
    version="1.0"
)

app.include_router(analytics_router)
app.include_router(ai_router)

@app.get("/")
def root():
    return {
        "message": "API is running successfully",
        "modules": ["Analytics", "AI"]
    }
