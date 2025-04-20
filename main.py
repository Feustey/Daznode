import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from api.v1.endpoints import node

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Daznode - Application de monitoring pour nœuds lightning",
    version="0.1.0",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routeurs
app.include_router(node.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Bienvenue sur Daznode API"}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 