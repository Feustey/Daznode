from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio

from services.data_source_factory import DataSourceFactory
from api.health import router as health_router
from api.routes import router as api_router
from api.umbrel_ui import router as umbrel_ui_router
from services.health_check_manager import HealthCheckManager

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Daznode API",
    description="API pour l'analyse du réseau Lightning",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(api_router)
app.include_router(health_router)
app.include_router(umbrel_ui_router)

# Initialiser le gestionnaire de health check
health_manager = HealthCheckManager()
health_manager.start()

@app.on_event("startup")
async def startup_event():
    """Événement exécuté au démarrage de l'application"""
    logger.info("Démarrage de l'application Daznode")
    
    # Initialiser la factory de sources de données avec le health check
    await DataSourceFactory.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Événement exécuté à l'arrêt de l'application"""
    logger.info("Arrêt de l'application Daznode")
    
    # Arrêter proprement les services
    await DataSourceFactory.shutdown()

    # Arrêter le gestionnaire de health check à l'arrêt
    health_manager.stop() 