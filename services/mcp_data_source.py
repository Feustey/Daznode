from typing import Dict, List, Any, Optional
import logging

from services.data_source_interface import DataSourceInterface
from services.mcp import MCPService

logger = logging.getLogger(__name__)

class MCPDataSource(DataSourceInterface):
    """Source de données utilisant l'API MCP"""
    
    def __init__(self, mcp_service: MCPService = None):
        """Initialise la source de données MCP
        
        Args:
            mcp_service: Service MCP à utiliser
        """
        self.mcp_service = mcp_service or MCPService()
    
    async def get_node_info(self, pubkey: str) -> Dict[str, Any]:
        """Récupère les informations d'un nœud via MCP"""
        try:
            return await self.mcp_service.get_node_info(pubkey)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos du nœud depuis MCP: {str(e)}")
            raise
    
    async def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Récupère les informations d'un canal via MCP"""
        try:
            return await self.mcp_service.get_channel_info(channel_id)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos du canal depuis MCP: {str(e)}")
            raise
    
    async def get_network_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du réseau via MCP"""
        try:
            return await self.mcp_service.get_network_stats()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques réseau depuis MCP: {str(e)}")
            raise
    
    async def get_network_nodes(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Récupère la liste des nœuds du réseau depuis MCP"""
        try:
            nodes = await self.mcp_service.get_network_nodes(limit=limit, offset=offset)
            # Ajouter la source aux données
            for node in nodes:
                node["source"] = "mcp"
            return nodes
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des nœuds du réseau depuis MCP: {e}")
            return []
    
    async def get_node_details(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un nœud spécifique depuis MCP"""
        try:
            node = await self.mcp_service.get_node_details(node_id)
            if node:
                return {**node, "source": "mcp"}
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails du nœud {node_id} depuis MCP: {e}")
            return None
    
    async def get_channels_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales des canaux depuis MCP"""
        try:
            stats = await self.mcp_service.get_channels_stats()
            return {**stats, "source": "mcp"}
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques des canaux depuis MCP: {e}")
            return {"error": str(e), "source": "mcp"}
    
    async def get_channels_list(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Récupère la liste des canaux depuis MCP"""
        try:
            channels = await self.mcp_service.get_channels_list(limit=limit, offset=offset)
            # Ajouter la source aux données
            for channel in channels:
                channel["source"] = "mcp"
            return channels
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la liste des canaux depuis MCP: {e}")
            return []
    
    async def get_channel_details(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un canal spécifique depuis MCP"""
        try:
            channel = await self.mcp_service.get_channel_details(channel_id)
            if channel:
                return {**channel, "source": "mcp"}
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des détails du canal {channel_id} depuis MCP: {e}")
            return None
    
    async def get_node_channels(self, node_id: str) -> List[Dict[str, Any]]:
        """Récupère les canaux d'un nœud spécifique depuis MCP"""
        try:
            channels = await self.mcp_service.get_node_channels(node_id)
            # Ajouter la source aux données
            for channel in channels:
                channel["source"] = "mcp"
            return channels
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des canaux du nœud {node_id} depuis MCP: {e}")
            return [] 