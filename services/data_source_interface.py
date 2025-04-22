from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime


class DataSourceInterface(ABC):
    """Interface pour les sources de données"""
    
    @abstractmethod
    async def get_node_info(self, pubkey: str) -> Dict[str, Any]:
        """Récupère les informations d'un nœud"""
        pass
    
    @abstractmethod
    async def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Récupère les informations d'un canal"""
        pass
    
    @abstractmethod
    async def get_network_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du réseau"""
        pass
    
    @abstractmethod
    async def get_network_nodes(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Récupère la liste des nœuds du réseau"""
        pass
    
    @abstractmethod
    async def get_node_details(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un nœud spécifique"""
        pass
    
    @abstractmethod
    async def get_channels_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales des canaux"""
        pass
    
    @abstractmethod
    async def get_channels_list(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Récupère la liste des canaux"""
        pass
    
    @abstractmethod
    async def get_channel_details(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un canal spécifique"""
        pass
    
    @abstractmethod
    async def get_node_channels(self, node_id: str) -> List[Dict[str, Any]]:
        """Récupère les canaux d'un nœud spécifique"""
        pass 