from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
from datetime import datetime


class NodeStatus(BaseModel):
    """Statut actuel du nœud Lightning"""
    node_id: str = Field(..., description="Identifiant du nœud")
    alias: str = Field(..., description="Alias du nœud")
    color: str = Field(..., description="Couleur du nœud")
    version: str = Field(..., description="Version du logiciel")
    is_online: bool = Field(..., description="Statut en ligne")
    uptime: int = Field(..., description="Durée de fonctionnement en secondes")
    block_height: int = Field(..., description="Hauteur du bloc actuel")
    synced_to_chain: bool = Field(..., description="Synchronisation avec la blockchain")
    synced_to_graph: bool = Field(..., description="Synchronisation avec le graphe du réseau")
    num_active_channels: int = Field(..., description="Nombre de canaux actifs")
    num_inactive_channels: int = Field(..., description="Nombre de canaux inactifs")
    num_pending_channels: int = Field(..., description="Nombre de canaux en attente")
    total_capacity: int = Field(..., description="Capacité totale en sats")
    total_local_balance: int = Field(..., description="Balance locale totale en sats")
    total_remote_balance: int = Field(..., description="Balance distante totale en sats")
    total_unsettled_balance: int = Field(..., description="Balance non réglée en sats")
    total_pending_htlcs: int = Field(..., description="Nombre total de HTLCs en attente")
    last_update: datetime = Field(..., description="Dernière mise à jour des données")


class NodeMetrics(BaseModel):
    """Métriques de performance du nœud sur une période donnée"""
    period: str = Field(..., description="Période de temps des métriques")
    forwards: List[Dict[str, Union[datetime, int]]] = Field(..., description="Historique des transferts")
    total_forwards: int = Field(..., description="Nombre total de transferts")
    total_forwarded_amount: int = Field(..., description="Montant total des transferts en sats")
    total_fees_earned: int = Field(..., description="Total des frais gagnés en sats")
    average_fee_rate: float = Field(..., description="Taux de frais moyen en ppm")
    channel_activity: Dict[str, int] = Field(..., description="Activité par canal")
    success_rate: float = Field(..., description="Taux de réussite des paiements")
    payment_failures: Dict[str, int] = Field(..., description="Échecs de paiements par type")
    htlc_events: Dict[str, int] = Field(..., description="Événements HTLC par type")
    fee_revenue_trend: List[Dict[str, Union[datetime, int]]] = Field(..., description="Tendance des revenus de frais")
    active_channels_trend: List[Dict[str, Union[datetime, int]]] = Field(..., description="Tendance des canaux actifs")


class ChannelLiquidity(BaseModel):
    """Information de liquidité pour un canal"""
    channel_id: str
    peer_alias: str
    capacity: int
    local_balance: int
    remote_balance: int
    local_percent: float
    inbound_liquidity: int
    outbound_liquidity: int
    is_active: bool


class LiquidityOverview(BaseModel):
    """Vue d'ensemble de la liquidité du nœud"""
    total_balance: int = Field(..., description="Balance totale en sats")
    total_capacity: int = Field(..., description="Capacité totale en sats")
    total_inbound: int = Field(..., description="Liquidité entrante totale en sats")
    total_outbound: int = Field(..., description="Liquidité sortante totale en sats")
    liquidity_ratio: float = Field(..., description="Ratio de liquidité sortante/entrante")
    balanced_threshold: float = Field(0.3, description="Seuil pour considérer un canal comme équilibré")
    unbalanced_inbound: List[ChannelLiquidity] = Field(..., description="Canaux déséquilibrés avec trop de liquidité entrante")
    unbalanced_outbound: List[ChannelLiquidity] = Field(..., description="Canaux déséquilibrés avec trop de liquidité sortante")
    balanced_channels: List[ChannelLiquidity] = Field(..., description="Canaux bien équilibrés")
    updated_at: datetime = Field(..., description="Dernière mise à jour des données") 