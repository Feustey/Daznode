from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class NetworkStats(BaseModel):
    """Statistiques du réseau Lightning"""
    total_nodes: int = Field(..., description="Nombre total de nœuds")
    total_channels: int = Field(..., description="Nombre total de canaux")
    total_capacity: int = Field(..., description="Capacité totale du réseau en sats")
    avg_node_capacity: int = Field(..., description="Capacité moyenne par nœud en sats")
    avg_channel_capacity: int = Field(..., description="Capacité moyenne par canal en sats")
    avg_node_channels: float = Field(..., description="Nombre moyen de canaux par nœud")
    active_nodes_24h: int = Field(..., description="Nœuds actifs dans les dernières 24h")
    network_growth_30d: Dict[str, int] = Field(..., description="Croissance du réseau sur 30 jours")
    updated_at: datetime = Field(..., description="Date de mise à jour des statistiques")


class NodeInfo(BaseModel):
    """Informations sur un nœud Lightning"""
    node_id: str = Field(..., description="Identifiant du nœud (clé publique)")
    alias: Optional[str] = Field(None, description="Alias du nœud")
    color: Optional[str] = Field(None, description="Couleur du nœud")
    last_update: Optional[datetime] = Field(None, description="Dernière mise à jour du nœud")
    addresses: List[str] = Field(default=[], description="Adresses du nœud")
    features: Dict[str, bool] = Field(default={}, description="Fonctionnalités supportées par le nœud")
    capacity: int = Field(0, description="Capacité totale du nœud en sats")
    channel_count: int = Field(0, description="Nombre de canaux")
    is_online: bool = Field(False, description="Statut en ligne du nœud")
    uptime_percentage: Optional[float] = Field(None, description="Pourcentage de disponibilité")
    location: Optional[Dict[str, float]] = Field(None, description="Localisation géographique")
    country: Optional[str] = Field(None, description="Pays du nœud")
    ranking: Optional[int] = Field(None, description="Classement dans le réseau")
    first_seen: Optional[datetime] = Field(None, description="Date de première apparition")


class NetworkNode(BaseModel):
    """Version simplifiée des informations sur un nœud pour la carte du réseau"""
    node_id: str
    alias: Optional[str] = None
    capacity: int = 0
    channel_count: int = 0
    lat: Optional[float] = None
    lon: Optional[float] = None
    country: Optional[str] = None


class NetworkConnection(BaseModel):
    """Connection entre deux nœuds pour la carte du réseau"""
    source: str
    target: str
    capacity: int
    channel_id: str


class NetworkMapData(BaseModel):
    """Données pour la carte du réseau"""
    nodes: List[NetworkNode]
    connections: List[NetworkConnection] 