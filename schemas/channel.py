from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class ChannelStats(BaseModel):
    """Statistiques globales des canaux du réseau Lightning"""
    total_channels: int = Field(..., description="Nombre total de canaux")
    active_channels: int = Field(..., description="Nombre de canaux actifs")
    total_capacity: int = Field(..., description="Capacité totale des canaux en sats")
    avg_capacity: int = Field(..., description="Capacité moyenne par canal en sats")
    avg_fee_rate: float = Field(..., description="Taux de frais moyen")
    avg_base_fee: int = Field(..., description="Frais de base moyen")
    channel_growth_30d: Dict[str, int] = Field(..., description="Croissance des canaux sur 30 jours")
    capacity_distribution: Dict[str, int] = Field(..., description="Distribution des capacités")
    updated_at: datetime = Field(..., description="Date de mise à jour des statistiques")


class ChannelPolicy(BaseModel):
    """Politique de routage d'un côté du canal"""
    node_id: str = Field(..., description="ID du nœud")
    fee_rate: float = Field(..., description="Taux de frais en ppm")
    base_fee: int = Field(..., description="Frais de base en millisats")
    time_lock_delta: int = Field(..., description="Delta de verrouillage temporel")
    min_htlc: int = Field(..., description="Montant minimum d'HTLC en millisats")
    max_htlc: int = Field(..., description="Montant maximum d'HTLC en millisats")
    disabled: bool = Field(False, description="Canal désactivé depuis ce côté")
    last_update: Optional[datetime] = Field(None, description="Dernière mise à jour de la politique")


class ChannelInfo(BaseModel):
    """Informations détaillées sur un canal Lightning"""
    channel_id: str = Field(..., description="Identifiant unique du canal")
    short_channel_id: Optional[str] = Field(None, description="Identifiant court du canal")
    capacity: int = Field(..., description="Capacité du canal en sats")
    transaction_id: str = Field(..., description="ID de transaction d'ouverture")
    transaction_output: int = Field(..., description="Index de sortie de la transaction")
    node1_pub: str = Field(..., description="Clé publique du nœud 1")
    node2_pub: str = Field(..., description="Clé publique du nœud 2")
    node1_policy: Optional[ChannelPolicy] = Field(None, description="Politique du nœud 1")
    node2_policy: Optional[ChannelPolicy] = Field(None, description="Politique du nœud 2")
    node1_alias: Optional[str] = Field(None, description="Alias du nœud 1")
    node2_alias: Optional[str] = Field(None, description="Alias du nœud 2")
    is_active: bool = Field(False, description="État actif du canal")
    is_public: bool = Field(True, description="Canal public ou privé")
    opened_at: Optional[datetime] = Field(None, description="Date d'ouverture du canal")
    closed_at: Optional[datetime] = Field(None, description="Date de fermeture du canal si fermé")
    close_type: Optional[str] = Field(None, description="Type de fermeture si fermé")


class ChannelPerformance(BaseModel):
    """Données de performance d'un canal"""
    channel_id: str
    forwards_count: int = Field(0, description="Nombre de transferts")
    forwards_amount: int = Field(0, description="Montant total des transferts en sats")
    fees_earned: int = Field(0, description="Frais gagnés en sats")
    uptime_percentage: float = Field(0, description="Pourcentage de disponibilité")
    success_rate: float = Field(0, description="Taux de réussite des paiements")
    liquidity_score: float = Field(0, description="Score de liquidité")


class ChannelPerformanceStats(BaseModel):
    """Statistiques de performance des canaux pour une période donnée"""
    period: str
    channels: List[ChannelPerformance]
    total_forwards: int
    total_amount: int
    total_fees: int 