from typing import Dict, Optional
import logging
import asyncio

from core.config import settings
from services.data_source_interface import DataSourceInterface
from services.local_data_source import LocalDataSource
from services.mcp_data_source import MCPDataSource
from services.lnd_client import LNDClient
from services.lnrouter_client import LNRouterClient
from services.mcp import MCPService
from services.health_check_manager import HealthCheckManager

logger = logging.getLogger(__name__)


class DataSourceFactory:
    """Factory pour créer des sources de données"""
    
    _sources: Dict[str, DataSourceInterface] = {}
    _lnd_client = None
    _lnrouter_client = None
    _mcp_service = None
    _health_manager = None
    _initialized = False
    
    @classmethod
    async def initialize(cls):
        """Initialise la factory et le health check manager"""
        if cls._initialized:
            logger.debug("DataSourceFactory déjà initialisé")
            return
            
        # Créer les clients partagés
        cls._lnd_client = cls.get_lnd_client()
        cls._lnrouter_client = cls.get_lnrouter_client()
        cls._mcp_service = cls.get_mcp_service()
        
        # Initialiser le health check manager
        cls._health_manager = HealthCheckManager(
            check_interval_seconds=getattr(settings, "HEALTH_CHECK_INTERVAL", 60)
        )
        cls._health_manager.set_clients(
            lnd_client=cls._lnd_client,
            mcp_service=cls._mcp_service,
            lnrouter_client=cls._lnrouter_client
        )
        
        # Effectuer la première vérification d'état immédiatement
        await cls._health_manager.check_all_sources()
        
        # Démarrer les vérifications périodiques en arrière-plan
        await cls._health_manager.start_background_checks()
        
        cls._initialized = True
        logger.info("DataSourceFactory initialisé avec health checks actifs")
    
    @classmethod
    def get_lnd_client(cls):
        """Récupère ou crée le client LND partagé"""
        if cls._lnd_client is None:
            cls._lnd_client = LNDClient()
        return cls._lnd_client
    
    @classmethod
    def get_lnrouter_client(cls):
        """Récupère ou crée le client LNRouter partagé"""
        if cls._lnrouter_client is None:
            cls._lnrouter_client = LNRouterClient()
        return cls._lnrouter_client
    
    @classmethod
    def get_mcp_service(cls):
        """Récupère ou crée le service MCP partagé"""
        if cls._mcp_service is None:
            cls._mcp_service = MCPService()
        return cls._mcp_service
    
    @classmethod
    def get_health_manager(cls) -> HealthCheckManager:
        """Récupère le gestionnaire de santé des sources de données"""
        if cls._health_manager is None:
            # Créer un health manager avec les clients par défaut
            cls._health_manager = HealthCheckManager()
            cls._health_manager.set_clients(
                lnd_client=cls.get_lnd_client(),
                mcp_service=cls.get_mcp_service(),
                lnrouter_client=cls.get_lnrouter_client()
            )
        return cls._health_manager
    
    @classmethod
    def get_data_source(cls, source_type: str = None) -> DataSourceInterface:
        """Récupère une source de données
        
        Args:
            source_type: Type de source de données ('local', 'mcp', 'auto')
                         Par défaut utilise la valeur de settings.DEFAULT_DATA_SOURCE
        
        Returns:
            Une instance de DataSourceInterface
        """
        source_type = source_type or settings.DEFAULT_DATA_SOURCE or "local"
        
        # Mode auto: utiliser MCP si disponible et opérationnel, sinon local
        if source_type == "auto":
            # Si le health manager n'est pas encore initialisé
            if cls._health_manager is None:
                # Fallback sur la logique simple basée sur la configuration
                if settings.MCP_API_KEY and settings.MCP_API_URL:
                    try:
                        # Tester si MCP est disponible
                        mcp_service = cls.get_mcp_service()
                        if asyncio.iscoroutinefunction(mcp_service.get_network_stats):
                            try:
                                asyncio.get_event_loop().run_until_complete(
                                    mcp_service.get_network_stats()
                                )
                                return cls.get_data_source("mcp")
                            except Exception as e:
                                logger.warning(
                                    f"MCP indisponible: {e}, utilisation de la source locale"
                                )
                                return cls.get_data_source("local")
                        else:
                            try:
                                mcp_service.get_network_stats()
                                return cls.get_data_source("mcp")
                            except Exception as e:
                                logger.warning(
                                    f"MCP indisponible: {e}, utilisation de la source locale"
                                )
                                return cls.get_data_source("local")
                    except Exception as e:
                        logger.warning(
                            f"MCP indisponible: {e}, utilisation de la source locale"
                        )
                        return cls.get_data_source("local")
                else:
                    return cls.get_data_source("local")
            else:
                # Utiliser le health manager pour choisir la meilleure source
                if (settings.MCP_API_KEY and settings.MCP_API_URL and 
                    cls._health_manager.is_source_available("mcp")):
                    return cls.get_data_source("mcp")
                elif cls._health_manager.is_source_available("local"):
                    return cls.get_data_source("local")
                else:
                    # Fallback sur la source locale même si elle n'est pas disponible
                    # (elle utilisera son cache si disponible)
                    logger.warning(
                        "Aucune source en ligne, utilisation du cache local"
                    )
                    return cls.get_data_source("local")
        
        # Vérifier si l'instance existe déjà
        if source_type in cls._sources:
            return cls._sources[source_type]
        
        # Créer la source de données
        if source_type == "local":
            source = LocalDataSource(
                lnd_client=cls._lnd_client or cls.get_lnd_client(),
                lnrouter_client=cls._lnrouter_client or cls.get_lnrouter_client()
            )
        elif source_type == "mcp":
            source = MCPDataSource(
                mcp_service=cls._mcp_service or cls.get_mcp_service()
            )
        else:
            logger.warning(
                f"Type de source de données inconnu: {source_type}, "
                "utilisation de 'local'"
            )
            source = LocalDataSource(
                lnd_client=cls._lnd_client or cls.get_lnd_client(),
                lnrouter_client=cls._lnrouter_client or cls.get_lnrouter_client()
            )
        
        # Stocker l'instance pour réutilisation
        cls._sources[source_type] = source
        
        return source
    
    @classmethod
    async def shutdown(cls):
        """Arrête proprement les services de la factory"""
        if cls._health_manager:
            await cls._health_manager.stop_background_checks()
        
        cls._initialized = False
        logger.info("DataSourceFactory arrêté") 