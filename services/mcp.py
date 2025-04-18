import httpx
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings


class MCPService:
    """Service pour interagir avec l'API MCP Network"""
    
    def __init__(self):
        self.base_url = settings.MCP_API_URL
        self.api_key = settings.MCP_API_KEY
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Any:
        """Effectue une requête à l'API MCP"""
        url = f"{self.base_url}{endpoint}"
        
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
    
    # Méthodes pour les données du réseau
    
    async def get_network_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du réseau"""
        return await self._make_request("GET", "/network/stats")
    
    async def get_network_nodes(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Récupère la liste des nœuds du réseau"""
        params = {"limit": limit, "offset": offset}
        return await self._make_request("GET", "/network/nodes", params=params)
    
    async def get_network_map(self) -> Dict[str, Any]:
        """Récupère les données pour la carte du réseau"""
        return await self._make_request("GET", "/network/map")
    
    async def get_node_details(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un nœud spécifique"""
        return await self._make_request("GET", f"/network/nodes/{node_id}")
    
    async def get_network_growth_trends(self) -> Dict[str, Any]:
        """Récupère les tendances de croissance du réseau"""
        return await self._make_request("GET", "/network/trends")
    
    # Méthodes pour les données des canaux
    
    async def get_channels_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales des canaux"""
        return await self._make_request("GET", "/channels/stats")
    
    async def get_channels_list(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Récupère la liste des canaux"""
        params = {"limit": limit, "offset": offset}
        return await self._make_request("GET", "/channels/list", params=params)
    
    async def get_channel_details(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un canal spécifique"""
        return await self._make_request("GET", f"/channels/{channel_id}")
    
    async def get_node_channels(self, node_id: str) -> List[Dict[str, Any]]:
        """Récupère les canaux d'un nœud spécifique"""
        return await self._make_request("GET", f"/network/nodes/{node_id}/channels")
    
    async def get_channels_performance(self, timeframe: str = "week") -> Dict[str, Any]:
        """Récupère les données de performance des canaux pour une période donnée"""
        params = {"timeframe": timeframe}
        return await self._make_request("GET", "/channels/performance", params=params)
    
    # Méthodes pour les analyses et contexte
    
    async def get_node_ranking(self, node_id: str) -> Dict[str, Any]:
        """Récupère le classement d'un nœud dans le réseau"""
        return await self._make_request("GET", f"/network/nodes/{node_id}/ranking")
    
    async def get_node_network_context(self, node_id: str) -> Dict[str, Any]:
        """Récupère le contexte réseau d'un nœud spécifique"""
        return await self._make_request("GET", f"/network/nodes/{node_id}/context") 