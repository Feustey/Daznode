# services/health_check_manager.py

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
import time

from core.config import settings
from services.lnd_client import LNDClient
from services.lnrouter_client import LNRouterClient
from services.mcp import MCPService

logger = logging.getLogger(__name__)

class HealthCheckManager:
    """Gestionnaire de vérification d'état des sources de données"""
    
    def __init__(self, check_interval_seconds: int = 60):
        """
        Initialise le gestionnaire de vérification d'état
        
        Args:
            check_interval_seconds: Intervalle en secondes entre les vérifications
        """
        self.check_interval = check_interval_seconds
        self.health_status = {
            "lnd": {"status": "unknown", "last_check": None, "error": None, "details": {}},
            "mcp": {"status": "unknown", "last_check": None, "error": None, "details": {}},
            "lnrouter": {"status": "unknown", "last_check": None, "error": None, "details": {}},
        }
        self._background_task = None
        self._running = False
        
        # Référence aux clients (seront injectés depuis DataSourceFactory)
        self._lnd_client = None
        self._mcp_service = None
        self._lnrouter_client = None
        
        # Délai de grâce pour considérer une source comme inactive
        self.failure_threshold = getattr(settings, "HEALTH_CHECK_FAILURE_THRESHOLD", 3)
        self.failure_counts = {"lnd": 0, "mcp": 0, "lnrouter": 0}
        
    def set_clients(self, lnd_client: LNDClient = None, mcp_service: MCPService = None, 
                   lnrouter_client: LNRouterClient = None):
        """
        Configure les clients à utiliser pour les vérifications
        
        Args:
            lnd_client: Client LND à utiliser
            mcp_service: Service MCP à utiliser
            lnrouter_client: Client LNRouter à utiliser
        """
        self._lnd_client = lnd_client
        self._mcp_service = mcp_service
        self._lnrouter_client = lnrouter_client
        
    async def start_background_checks(self):
        """Démarre les vérifications d'état en arrière-plan"""
        if self._background_task is not None:
            logger.warning("Les vérifications d'état sont déjà en cours")
            return
        
        self._running = True
        self._background_task = asyncio.create_task(self._run_periodic_checks())
        logger.info(f"Démarrage des vérifications d'état (intervalle: {self.check_interval}s)")
        
    async def stop_background_checks(self):
        """Arrête les vérifications d'état en arrière-plan"""
        if self._background_task is None:
            logger.warning("Aucune vérification d'état en cours")
            return
        
        self._running = False
        self._background_task.cancel()
        try:
            await self._background_task
        except asyncio.CancelledError:
            pass
        self._background_task = None
        logger.info("Arrêt des vérifications d'état")
        
    async def _run_periodic_checks(self):
        """Exécute les vérifications d'état périodiquement"""
        while self._running:
            try:
                await self.check_all_sources()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur lors des vérifications d'état périodiques: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def check_all_sources(self):
        """Vérifie l'état de toutes les sources de données"""
        tasks = []
        
        if self._lnd_client:
            tasks.append(self.check_lnd_health())
        if self._mcp_service:
            tasks.append(self.check_mcp_health())
        if self._lnrouter_client:
            tasks.append(self.check_lnrouter_health())
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        else:
            logger.warning("Aucun client configuré pour les vérifications d'état")
        
    async def check_lnd_health(self):
        """Vérifie l'état de LND"""
        source_name = "lnd"
        current_time = datetime.now().isoformat()
        
        try:
            if not self._lnd_client:
                self.health_status[source_name] = {
                    "status": "unavailable",
                    "last_check": current_time,
                    "error": "LND client not configured",
                    "details": {}
                }
                return
                
            # Essai de récupération des informations du nœud
            start_time = time.time()
            node_info = self._lnd_client.get_node_info()
            response_time = (time.time() - start_time) * 1000  # en ms
            
            # Réinitialiser le compteur d'échecs
            self.failure_counts[source_name] = 0
            
            self.health_status[source_name] = {
                "status": "ok",
                "last_check": current_time,
                "error": None,
                "details": {
                    "alias": node_info.get("alias"),
                    "pubkey": node_info.get("pubkey"),
                    "block_height": node_info.get("block_height"),
                    "synced": node_info.get("synced_to_chain", False),
                    "response_time_ms": round(response_time, 2)
                }
            }
            logger.debug(f"Vérification LND réussie, temps de réponse: {round(response_time, 2)}ms")
        except Exception as e:
            # Incrémenter le compteur d'échecs
            self.failure_counts[source_name] += 1
            
            # Déterminer le statut en fonction du seuil d'échecs
            status = "degraded" if self.failure_counts[source_name] < self.failure_threshold else "error"
            
            self.health_status[source_name] = {
                "status": status,
                "last_check": current_time,
                "error": str(e),
                "failure_count": self.failure_counts[source_name],
                "details": {}
            }
            logger.warning(f"Échec de la vérification LND ({self.failure_counts[source_name]}/{self.failure_threshold}): {e}")
    
    async def check_mcp_health(self):
        """Vérifie l'état de MCP"""
        source_name = "mcp"
        current_time = datetime.now().isoformat()
        
        try:
            if not self._mcp_service:
                self.health_status[source_name] = {
                    "status": "unavailable",
                    "last_check": current_time,
                    "error": "MCP service not configured",
                    "details": {}
                }
                return
                
            # Essai de récupération des statistiques réseau (opération légère)
            start_time = time.time()
            network_stats = await self._mcp_service.get_network_stats()
            response_time = (time.time() - start_time) * 1000  # en ms
            
            # Réinitialiser le compteur d'échecs
            self.failure_counts[source_name] = 0
            
            self.health_status[source_name] = {
                "status": "ok",
                "last_check": current_time,
                "error": None,
                "details": {
                    "api_url": self._mcp_service.base_url,
                    "has_api_key": bool(self._mcp_service.api_key),
                    "network_stats": {
                        "nodes_count": network_stats.get("num_nodes", 0),
                        "channels_count": network_stats.get("num_channels", 0)
                    },
                    "response_time_ms": round(response_time, 2)
                }
            }
            logger.debug(f"Vérification MCP réussie, temps de réponse: {round(response_time, 2)}ms")
        except Exception as e:
            # Incrémenter le compteur d'échecs
            self.failure_counts[source_name] += 1
            
            # Déterminer le statut en fonction du seuil d'échecs
            status = "degraded" if self.failure_counts[source_name] < self.failure_threshold else "error"
            
            self.health_status[source_name] = {
                "status": status,
                "last_check": current_time,
                "error": str(e),
                "failure_count": self.failure_counts[source_name],
                "details": {
                    "api_url": getattr(self._mcp_service, "base_url", "unknown"),
                    "has_api_key": bool(getattr(self._mcp_service, "api_key", None))
                }
            }
            logger.warning(f"Échec de la vérification MCP ({self.failure_counts[source_name]}/{self.failure_threshold}): {e}")
    
    async def check_lnrouter_health(self):
        """Vérifie l'état de LNRouter"""
        source_name = "lnrouter"
        current_time = datetime.now().isoformat()
        
        try:
            if not self._lnrouter_client:
                self.health_status[source_name] = {
                    "status": "unavailable",
                    "last_check": current_time,
                    "error": "LNRouter client not configured",
                    "details": {}
                }
                return
            
            # Vérifier si nous avons un graphe en cache
            cache_valid = False
            if self._lnrouter_client.graph is not None and self._lnrouter_client.last_graph_update is not None:
                # Le graphe est en cache, vérifier s'il est récent
                cache_age = datetime.now() - self._lnrouter_client.last_graph_update
                cache_valid = cache_age <= self._lnrouter_client.graph_cache_duration
            
            # Vérifier le cache uniquement (pas d'appel API)
            details = {
                "api_url": self._lnrouter_client.base_url,
                "has_api_key": bool(self._lnrouter_client.api_key),
                "cache_status": "valid" if cache_valid else "stale or missing",
                "cache_details": {}
            }
            
            if cache_valid and self._lnrouter_client.graph:
                nodes_count = len(self._lnrouter_client.graph.get("nodes", []))
                channels_count = len(self._lnrouter_client.graph.get("channels", []))
                cache_age_hours = (datetime.now() - self._lnrouter_client.last_graph_update).total_seconds() / 3600
                
                details["cache_details"] = {
                    "nodes_count": nodes_count,
                    "channels_count": channels_count,
                    "cache_age_hours": round(cache_age_hours, 2),
                    "last_update": self._lnrouter_client.last_graph_update.isoformat()
                }
            
            # Si le cache est valide, on considère le service comme fonctionnel
            if cache_valid:
                # Réinitialiser le compteur d'échecs
                self.failure_counts[source_name] = 0
                
                self.health_status[source_name] = {
                    "status": "ok",
                    "last_check": current_time,
                    "error": None,
                    "details": details
                }
                logger.debug(f"Vérification LNRouter réussie (cache valide)")
                return
            
            # Sinon, faire un léger appel API pour vérifier la disponibilité
            start_time = time.time()
            # Utiliser une méthode légère comme get_network_stats plutôt que get_graph complet
            try:
                # Vérifier si la méthode get_network_stats existe, sinon fallback sur get_graph
                if hasattr(self._lnrouter_client, "get_network_stats"):
                    stats = await self._lnrouter_client.get_network_stats()
                else:
                    # Utiliser force_refresh=False pour éviter de recharger le graphe complet
                    graph = await self._lnrouter_client.get_graph(force_refresh=False)
                    stats = {"nodes_count": len(graph.get("nodes", [])), 
                             "channels_count": len(graph.get("channels", []))}
                
                response_time = (time.time() - start_time) * 1000  # en ms
                
                # Réinitialiser le compteur d'échecs
                self.failure_counts[source_name] = 0
                
                details["response_time_ms"] = round(response_time, 2)
                details["network_stats"] = stats
                
                self.health_status[source_name] = {
                    "status": "ok",
                    "last_check": current_time,
                    "error": None,
                    "details": details
                }
                logger.debug(f"Vérification LNRouter réussie, temps de réponse: {round(response_time, 2)}ms")
                
            except Exception as e:
                # En cas d'échec de l'API mais cache disponible (même périmé), 
                # on considère le service comme dégradé mais utilisable
                if self._lnrouter_client.graph is not None:
                    status = "degraded"
                    error_msg = f"API inaccessible mais cache disponible: {e}"
                else:
                    # Incrémenter le compteur d'échecs
                    self.failure_counts[source_name] += 1
                    
                    # Déterminer le statut en fonction du seuil d'échecs
                    status = "degraded" if self.failure_counts[source_name] < self.failure_threshold else "error"
                    error_msg = str(e)
                
                self.health_status[source_name] = {
                    "status": status,
                    "last_check": current_time,
                    "error": error_msg,
                    "failure_count": self.failure_counts[source_name],
                    "details": details
                }
                logger.warning(f"Échec de la vérification LNRouter ({self.failure_counts[source_name]}/{self.failure_threshold}): {e}")
        except Exception as e:
            # Incrémenter le compteur d'échecs
            self.failure_counts[source_name] += 1
            
            # Déterminer le statut en fonction du seuil d'échecs
            status = "degraded" if self.failure_counts[source_name] < self.failure_threshold else "error"
            
            self.health_status[source_name] = {
                "status": status,
                "last_check": current_time,
                "error": str(e),
                "failure_count": self.failure_counts[source_name],
                "details": {
                    "api_url": getattr(self._lnrouter_client, "base_url", "unknown"),
                    "has_api_key": bool(getattr(self._lnrouter_client, "api_key", None))
                }
            }
            logger.warning(f"Erreur lors de la vérification de LNRouter: {e}")
    
    def is_source_available(self, source_type: str) -> bool:
        """
        Vérifie si une source de données est disponible
        
        Args:
            source_type: Type de source ('local', 'mcp', 'lnrouter')
            
        Returns:
            True si la source est disponible, False sinon
        """
        if source_type == "local":
            return self.health_status["lnd"]["status"] in ["ok", "degraded"]
        elif source_type == "mcp":
            return self.health_status["mcp"]["status"] in ["ok", "degraded"]
        elif source_type == "lnrouter":
            return self.health_status["lnrouter"]["status"] in ["ok", "degraded"]
        
        return False
    
    def get_source_status(self, source_type: str) -> Dict[str, Any]:
        """
        Récupère l'état détaillé d'une source de données
        
        Args:
            source_type: Type de source ('lnd', 'mcp', 'lnrouter')
            
        Returns:
            Dictionnaire contenant l'état de la source
        """
        if source_type in self.health_status:
            return self.health_status[source_type]
        return {"status": "unknown", "error": f"Source inconnue: {source_type}"}
    
    def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """
        Récupère l'état de toutes les sources de données
        
        Returns:
            Dictionnaire contenant l'état de toutes les sources
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "sources": self.health_status,
            "global_status": self._calculate_global_status()
        }
    
    def _calculate_global_status(self) -> str:
        """
        Calcule l'état global du système en fonction de l'état des sources
        
        Returns:
            État global ('ok', 'degraded', 'error')
        """
        # Compter les sources dans chaque état
        status_counts = {"ok": 0, "degraded": 0, "error": 0, "unavailable": 0, "unknown": 0}
        
        for source, status in self.health_status.items():
            source_status = status.get("status", "unknown")
            status_counts[source_status] = status_counts.get(source_status, 0) + 1
        
        # Déterminer l'état global en fonction des compteurs
        if status_counts["error"] > 0:
            return "error"
        elif status_counts["degraded"] > 0:
            return "degraded"
        elif status_counts["ok"] > 0:
            return "ok"
        else:
            return "unknown"