import networkx as nx
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from services.data_source_interface import DataSourceInterface
from services.lnd_client import LNDClient
from services.lnrouter_client import LNRouterClient

logger = logging.getLogger(__name__)

class LocalDataSource(DataSourceInterface):
    """Source de données locale utilisant directement LND et d'autres services locaux"""
    
    def __init__(self, lnd_client: LNDClient = None, lnrouter_client: LNRouterClient = None):
        """Initialise la source de données locale
        
        Args:
            lnd_client: Client LND
            lnrouter_client: Client LNRouter optionnel pour enrichir les données
        """
        self.lnd_client = lnd_client or LNDClient()
        self.lnrouter_client = lnrouter_client or LNRouterClient()
        self.graph = None
        
    async def _ensure_graph_loaded(self):
        """S'assure que le graphe est chargé"""
        if self.graph is None:
            self.graph = await self.lnrouter_client.convert_to_networkx()
    
    async def get_network_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du réseau"""
        try:
            # Obtenir les statistiques basiques du nœud
            node_info = self.lnd_client.get_node_info()
            
            # Obtenir des informations du graphe via LNRouter (qui peut être en cache local)
            graph_stats = await self.lnrouter_client.analyze_network_topology()
            
            # Combiner les informations
            return {
                "timestamp": datetime.now().isoformat(),
                "node_stats": {
                    "alias": node_info.get("alias"),
                    "pubkey": node_info.get("pubkey"),
                    "num_active_channels": node_info.get("num_active_channels"),
                    "num_inactive_channels": node_info.get("num_inactive_channels")
                },
                "network_stats": graph_stats,
                "source": "local"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques réseau: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "source": "local"
            }
    
    async def get_network_nodes(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Récupère la liste des nœuds du réseau"""
        try:
            await self._ensure_graph_loaded()
            
            # Récupérer tous les nœuds du graphe
            nodes = list(self.graph.nodes(data=True))
            
            # Appliquer limit et offset
            paginated_nodes = nodes[offset:offset+limit]
            
            return [
                {
                    "pubkey": node_id,
                    "alias": node_data.get("alias", ""),
                    "last_update": node_data.get("last_update", 0),
                    "color": node_data.get("color", "#000000"),
                    "degree": self.graph.degree(node_id),
                    "source": "local"
                }
                for node_id, node_data in paginated_nodes
            ]
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des nœuds du réseau: {e}")
            return []
    
    async def get_node_details(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un nœud spécifique"""
        try:
            # Vérifier si c'est notre propre nœud
            node_info = self.lnd_client.get_node_info()
            if node_info.get("pubkey") == node_id:
                return {**node_info, "source": "local"}
            
            # Sinon, essayer de récupérer depuis LNRouter/cache local
            try:
                node_data = await self.lnrouter_client.get_node_info(node_id)
                return {**node_data, "source": "local_cache"}
            except Exception:
                # Si pas trouvé dans le cache, récupérer depuis le graphe
                await self._ensure_graph_loaded()
                
                if node_id in self.graph.nodes:
                    node_data = self.graph.nodes[node_id]
                    channels = self.graph.edges(node_id, data=True)
                    
                    return {
                        "pubkey": node_id,
                        "alias": node_data.get("alias", ""),
                        "color": node_data.get("color", ""),
                        "last_update": node_data.get("last_update", 0),
                        "num_channels": len(list(channels)),
                        "source": "local_graph"
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails du nœud {node_id}: {e}")
            return None
    
    async def get_channels_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales des canaux"""
        try:
            # Récupérer tous les canaux de notre nœud
            channels = self.lnd_client.list_channels()
            
            # Calculer des statistiques
            total_capacity = sum(c["capacity"] for c in channels)
            active_channels = [c for c in channels if c["active"]]
            inactive_channels = [c for c in channels if not c["active"]]
            
            # Obtenir des statistiques globales via le graphe
            await self._ensure_graph_loaded()
            all_edges = self.graph.edges(data=True)
            network_capacity = sum(edge_data.get("capacity", 0) for _, _, edge_data in all_edges)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "local_stats": {
                    "total_channels": len(channels),
                    "active_channels": len(active_channels),
                    "inactive_channels": len(inactive_channels),
                    "total_capacity": total_capacity,
                    "avg_capacity": total_capacity / len(channels) if channels else 0
                },
                "network_stats": {
                    "total_channels": len(list(all_edges)),
                    "total_capacity": network_capacity,
                    "avg_capacity": network_capacity / len(list(all_edges)) if all_edges else 0
                },
                "source": "local"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques des canaux: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "source": "local"
            }
    
    async def get_channels_list(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Récupère la liste des canaux"""
        try:
            # Récupérer les canaux de notre nœud
            channels = self.lnd_client.list_channels()
            
            # Appliquer limit et offset
            paginated_channels = channels[offset:offset+limit]
            
            return [
                {
                    "channel_id": str(c["channel_id"]),
                    "node1_pub": self.lnd_client.get_node_info().get("pubkey", ""),
                    "node2_pub": c["remote_pubkey"],
                    "capacity": c["capacity"],
                    "active": c["active"],
                    "local_balance": c["local_balance"],
                    "remote_balance": c["remote_balance"],
                    "source": "local"
                }
                for c in paginated_channels
            ]
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la liste des canaux: {e}")
            return []
    
    async def get_channel_details(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un canal spécifique"""
        try:
            # Récupérer tous les canaux
            channels = self.lnd_client.list_channels()
            
            # Chercher le canal spécifique
            for channel in channels:
                if str(channel["channel_id"]) == channel_id:
                    return {**channel, "source": "local"}
            
            # Si pas trouvé localement, essayer via LNRouter
            try:
                channel_data = await self.lnrouter_client.get_channel_info(channel_id)
                return {**channel_data, "source": "local_cache"}
            except Exception:
                pass
                
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails du canal {channel_id}: {e}")
            return None
    
    async def get_node_channels(self, node_id: str) -> List[Dict[str, Any]]:
        """Récupère les canaux d'un nœud spécifique"""
        try:
            # Vérifier si c'est notre propre nœud
            node_info = self.lnd_client.get_node_info()
            
            if node_info.get("pubkey") == node_id:
                # C'est notre nœud, récupérer nos canaux
                channels = self.lnd_client.list_channels()
                return [
                    {
                        "channel_id": str(c["channel_id"]),
                        "node1_pub": node_id,
                        "node2_pub": c["remote_pubkey"],
                        "capacity": c["capacity"],
                        "active": c["active"],
                        "local_balance": c["local_balance"],
                        "remote_balance": c["remote_balance"],
                        "source": "local"
                    }
                    for c in channels
                ]
            
            # Sinon, essayer de récupérer depuis le graphe
            await self._ensure_graph_loaded()
            
            if node_id in self.graph.nodes:
                channels = self.graph.edges(node_id, data=True)
                return [
                    {
                        "channel_id": str(edge_data.get("channel_id", "")),
                        "node1_pub": u,
                        "node2_pub": v,
                        "capacity": edge_data.get("capacity", 0),
                        "source": "local_graph"
                    }
                    for u, v, edge_data in channels
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des canaux du nœud {node_id}: {e}")
            return []
    
    async def get_node_info(self, pubkey: str) -> Dict[str, Any]:
        """Récupère les informations d'un nœud
        
        Args:
            pubkey: Clé publique du nœud
            
        Returns:
            Dictionnaire contenant les informations du nœud
        """
        try:
            # Essayer d'abord via LND
            try:
                node_info = self.lnd_client.get_node_info()
                if node_info.get("pubkey") == pubkey:
                    return {
                        "node": {
                            "pubkey": node_info.get("pubkey"),
                            "alias": node_info.get("alias"),
                            "color": node_info.get("color", "#000000"),
                            "addresses": node_info.get("addresses", []),
                            "last_update": node_info.get("last_update", 0)
                        },
                        "source": "local"
                    }
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération des infos du nœud depuis LND: {e}")
            
            # Fallback sur LNRouter
            try:
                node_data = await self.lnrouter_client.get_node_info(pubkey)
                return {
                    "node": {
                        "pubkey": node_data.get("pub_key"),
                        "alias": node_data.get("alias"),
                        "color": node_data.get("color", "#000000"),
                        "last_update": node_data.get("last_update", 0)
                    },
                    "source": "local_cache"
                }
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération des infos du nœud depuis LNRouter: {e}")
                
            # Si toujours pas trouvé, essayer via le graphe
            await self._ensure_graph_loaded()
            if pubkey in self.graph.nodes:
                node_data = self.graph.nodes[pubkey]
                return {
                    "node": {
                        "pubkey": pubkey,
                        "alias": node_data.get("alias", ""),
                        "color": node_data.get("color", "#000000"),
                        "last_update": node_data.get("last_update", 0)
                    },
                    "source": "local_graph"
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos du nœud {pubkey}: {e}")
            return None
            
    async def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Récupère les informations d'un canal
        
        Args:
            channel_id: Identifiant du canal
            
        Returns:
            Dictionnaire contenant les informations du canal
        """
        try:
            # Essayer d'abord via LND
            channels = self.lnd_client.list_channels()
            for channel in channels:
                if str(channel["channel_id"]) == channel_id:
                    return {
                        "channel": {
                            "channel_id": str(channel["channel_id"]),
                            "node1_pub": self.lnd_client.get_node_info().get("pubkey", ""),
                            "node2_pub": channel["remote_pubkey"],
                            "capacity": channel["capacity"],
                            "local_balance": channel["local_balance"],
                            "remote_balance": channel["remote_balance"],
                            "active": channel["active"],
                            "private": channel.get("private", False)
                        },
                        "source": "local"
                    }
                    
            # Si pas trouvé dans LND, essayer via LNRouter
            try:
                channel_data = await self.lnrouter_client.get_channel_info(channel_id)
                return {
                    "channel": {
                        "channel_id": channel_id,
                        "node1_pub": channel_data.get("node1_pub"),
                        "node2_pub": channel_data.get("node2_pub"),
                        "capacity": channel_data.get("capacity"),
                        "last_update": channel_data.get("last_update", 0)
                    },
                    "source": "local_cache"
                }
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération des infos du canal depuis LNRouter: {e}")
                
            # Si toujours pas trouvé, essayer via le graphe
            await self._ensure_graph_loaded()
            for u, v, edge_data in self.graph.edges(data=True):
                if str(edge_data.get("channel_id")) == channel_id:
                    return {
                        "channel": {
                            "channel_id": channel_id,
                            "node1_pub": u,
                            "node2_pub": v,
                            "capacity": edge_data.get("capacity", 0),
                            "last_update": edge_data.get("last_update", 0)
                        },
                        "source": "local_graph"
                    }
                    
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos du canal {channel_id}: {e}")
            return None 