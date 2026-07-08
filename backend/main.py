import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, grievances, analytics, websockets

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Multi-Agent Governance Platform & Decision Support System",
    version="1.0.0"
)

# Set up CORS middleware to allow communication with the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this down to specific domains (e.g. http://localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(grievances.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(websockets.router) # WebSocket routes don't usually use V1 prefix

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": "2026-07-08T12:00:00Z",
        "project": settings.PROJECT_NAME
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
