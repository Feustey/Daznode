from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging

from services.data_source_factory import DataSourceFactory
from services.health_check_manager import HealthCheckManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/system", tags=["Système"])

@router.get("/health", response_model=Dict[str, Any])
async def get_sources_health():
    """Récupère l'état de santé des sources de données"""
    try:
        health_manager = DataSourceFactory.get_health_manager()
        
        # Force une vérification immédiate pour des données à jour
        await health_manager.check_all_sources()
        
        return health_manager.get_all_statuses()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'état de santé: {e}")
        return {
            "error": "Impossible de récupérer l'état de santé",
            "details": str(e)
        } 