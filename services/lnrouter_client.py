import httpx
import networkx as nx
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import logging
import json
from functools import lru_cache

from core.config import settings

logger = logging.getLogger(__name__)

class LNRouterClient:
    """Client pour interagir avec l'API du graphe Lightning Network via LNRouter.app"""
    
    def __init__(self):
        self.base_url = settings.LNROUTER_API_URL or "https://lnrouter.app/api/v1"
        self.api_key = settings.LNROUTER_API_KEY
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        self.graph_cache_file = "data/lnrouter_graph_cache.json"
        self.graph_cache_duration = timedelta(hours=6)  # Mettre à jour le graphe toutes les 6 heures
        self.last_graph_update = None
        self.graph = None
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Any:
        """Effectue une requête à l'API LNRouter"""
        if not method or not endpoint:
            raise ValueError("Method and endpoint are required")
            
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=self.headers,
                    timeout=60.0
                )
                
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error when calling LNRouter API: {e}")
            raise
    
    async def get_graph(self, force_refresh: bool = False) -> Dict:
        """Récupère la structure complète du graphe Lightning Network"""
        now = datetime.now()
        
        # Vérifier si nous devons recharger le graphe
        if (force_refresh or 
            self.graph is None or 
            self.last_graph_update is None or 
            (now - self.last_graph_update) > self.graph_cache_duration):
            
            try:
                logger.info("Récupération du graphe Lightning Network depuis LNRouter.app")
                graph_data = await self._make_request("GET", "/graph")
                
                # Mettre à jour le cache
                self.graph = graph_data
                self.last_graph_update = now
                
                # Sauvegarder le graphe en cache sur disque
                self._save_graph_to_cache()
                
                return graph_data
            except Exception as e:
                logger.error(f"Erreur lors de la récupération du graphe LN: {e}")
                
                # Essayer de charger depuis le cache sur disque
                if self._load_graph_from_cache():
                    logger.info("Graphe chargé depuis le cache local")
                    return self.graph
                
                raise
        else:
            logger.debug("Utilisation du graphe LN en cache")
            return self.graph
    
    def _save_graph_to_cache(self) -> None:
        """Sauvegarde le graphe en cache sur disque"""
        try:
            import os
            os.makedirs(os.path.dirname(self.graph_cache_file), exist_ok=True)
            
            with open(self.graph_cache_file, 'w') as f:
                cache_data = {
                    "timestamp": datetime.now().isoformat(),
                    "graph": self.graph
                }
                json.dump(cache_data, f)
            logger.info(f"Graphe LN sauvegardé dans {self.graph_cache_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du graphe en cache: {e}")
    
    def _load_graph_from_cache(self) -> bool:
        """Charge le graphe depuis le cache sur disque"""
        try:
            import os
            if not os.path.exists(self.graph_cache_file):
                return False
                
            with open(self.graph_cache_file, 'r') as f:
                cache_data = json.load(f)
                
            # Vérifier si le cache n'est pas trop ancien
            cache_time = datetime.fromisoformat(cache_data["timestamp"])
            if (datetime.now() - cache_time) > timedelta(days=1):
                logger.warning("Le cache du graphe LN est trop ancien")
                return False
                
            self.graph = cache_data["graph"]
            self.last_graph_update = cache_time
            return True
        except Exception as e:
            logger.error(f"Erreur lors du chargement du graphe depuis le cache: {e}")
            return False
    
    async def get_node_info(self, pubkey: str) -> Dict:
        """Récupère les informations détaillées d'un nœud"""
        if not pubkey:
            raise ValueError("Le pubkey du nœud est requis")
            
        return await self._make_request("GET", f"/nodes/{pubkey}")
    
    async def get_channel_info(self, channel_id: str) -> Dict:
        """Récupère les informations détaillées d'un canal"""
        if not channel_id:
            raise ValueError("L'ID du canal est requis")
            
        return await self._make_request("GET", f"/channels/{channel_id}")
    
    async def get_optimal_routes(self, source_pubkey: str, target_pubkey: str, amount_sats: int = 0) -> List[Dict]:
        """Calcule les routes optimales entre deux nœuds"""
        if not source_pubkey or not target_pubkey:
            raise ValueError("Les pubkeys source et destination sont requis")
            
        params = {
            "source": source_pubkey,
            "destination": target_pubkey
        }
        
        if amount_sats > 0:
            params["amount"] = str(amount_sats)
            
        return await self._make_request("GET", "/routes", params=params)
    
    @lru_cache(maxsize=100)
    async def get_key_nodes(self, limit: int = 100, metric: str = "betweenness") -> List[Dict]:
        """Identifie les nœuds clés du réseau basés sur différentes métriques de centralité
        
        Args:
            limit: Nombre maximum de nœuds à retourner
            metric: Métrique de centralité à utiliser ('betweenness', 'degree', 'eigenvector', 'closeness')
        """
        valid_metrics = ["betweenness", "degree", "eigenvector", "closeness"]
        if metric not in valid_metrics:
            raise ValueError(f"Métrique invalide. Valeurs autorisées: {', '.join(valid_metrics)}")
            
        params = {
            "limit": limit,
            "metric": metric
        }
        
        return await self._make_request("GET", "/nodes/key", params=params)
    
    async def convert_to_networkx(self) -> nx.Graph:
        """Convertit le graphe Lightning Network en graphe NetworkX pour analyse avancée"""
        graph_data = await self.get_graph()
        
        G = nx.Graph()
        
        # Ajouter les nœuds
        for node in graph_data.get("nodes", []):
            node_id = node.get("pub_key")
            if node_id:
                G.add_node(node_id, **node)
        
        # Ajouter les arêtes (canaux)
        for channel in graph_data.get("channels", []):
            channel_id = channel.get("channel_id")
            node1 = channel.get("node1_pub")
            node2 = channel.get("node2_pub")
            capacity = int(channel.get("capacity", 0))
            
            if channel_id and node1 and node2:
                G.add_edge(node1, node2, channel_id=channel_id, capacity=capacity, **channel)
        
        return G
    
    async def analyze_network_topology(self) -> Dict:
        """Analyse la topologie du réseau pour identifier les clusters et goulots d'étranglement"""
        G = await self.convert_to_networkx()
        
        # Calculer des statistiques de base
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()
        avg_degree = sum(dict(G.degree()).values()) / num_nodes if num_nodes > 0 else 0
        
        # Identifier les composantes connectées
        connected_components = list(nx.connected_components(G))
        largest_component = max(connected_components, key=len)
        largest_component_size = len(largest_component)
        
        # Calculer le diamètre du réseau (peut être coûteux en calcul)
        diameter = -1
        if len(largest_component) > 1:
            try:
                # Utiliser un sous-ensemble pour une estimation plus rapide
                largest_component_subgraph = G.subgraph(list(largest_component)[:1000])
                diameter = nx.diameter(largest_component_subgraph)
            except Exception as e:
                logger.warning(f"Impossible de calculer le diamètre: {e}")
        
        # Calculer la centralité de betweenness pour les 20 principaux nœuds
        try:
            betweenness = nx.betweenness_centrality(G, k=100, normalized=True)
            top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:20]
        except Exception:
            top_betweenness = []
            
        # Calculer la densité du graphe
        density = nx.density(G)
        
        return {
            "num_nodes": num_nodes,
            "num_channels": num_edges,
            "avg_degree": avg_degree,
            "network_diameter": diameter,
            "largest_component_size": largest_component_size,
            "largest_component_ratio": largest_component_size / num_nodes if num_nodes > 0 else 0,
            "density": density,
            "top_betweenness_nodes": [{"pubkey": node, "centrality": value} for node, value in top_betweenness],
            "timestamp": datetime.now().isoformat()
        }
    
    async def find_path(self, source_pubkey: str, target_pubkey: str, amount_sats: int = 0) -> List[Dict]:
        """Trouve un chemin optimal entre deux nœuds en utilisant l'algorithme de Dijkstra"""
        G = await self.convert_to_networkx()
        
        if source_pubkey not in G or target_pubkey not in G:
            raise ValueError("Les nœuds source ou destination n'existent pas dans le graphe")
            
        try:
            # Utiliser la capacité comme poids (inverse)
            def weight_function(u, v, edge_data):
                capacity = edge_data.get('capacity', 1)
                return 1000000000 / capacity if capacity > 0 else float('inf')
                
            path = nx.dijkstra_path(G, source_pubkey, target_pubkey, weight=weight_function)
            
            # Construire le résultat avec les détails des canaux
            result = []
            for i in range(len(path) - 1):
                node1 = path[i]
                node2 = path[i + 1]
                
                # Récupérer les détails du canal
                edge_data = G.get_edge_data(node1, node2)
                
                result.append({
                    "from_node": node1,
                    "to_node": node2,
                    "channel_id": edge_data.get("channel_id"),
                    "capacity": edge_data.get("capacity")
                })
                
            return result
        except nx.NetworkXNoPath:
            return []
    
    async def get_network_stats(self) -> Dict:
        """Récupère des statistiques globales sur le réseau Lightning"""
        return await self._make_request("GET", "/stats") 