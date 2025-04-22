import logging
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import json

from core.config import settings
from services.lnd_client import LNDClient
from services.lnrouter_client import LNRouterClient
from services.mcp import MCPService
from services.feustey import FeusteyService
from services.data_source_factory import DataSourceFactory

logger = logging.getLogger(__name__)

class EnrichedChannel:
    """Classe représentant un canal LN enrichi avec des données de multiples sources"""
    
    def __init__(self, channel_id: str):
        self.channel_id = channel_id
        self.node1_pub = None
        self.node2_pub = None
        self.capacity = 0
        self.local_balance = 0
        self.remote_balance = 0
        self.local_ratio = 0.0
        self.active = False
        self.private = False
        self.initiator = False
        self.lnd_data = {}
        self.lnrouter_data = {}
        self.amboss_data = {}
        self.mcp_data = {}
        self.forwarding_stats = {
            "total_forwards": 0,
            "total_amount_forwards": 0,
            "total_fees": 0,
            "last_forward_time": None
        }
        self.rebalancing_stats = {
            "total_rebalances": 0,
            "total_amount_rebalanced": 0,
            "total_fees_paid": 0,
            "last_rebalance_time": None
        }
        self.profitability = {
            "revenue": 0,
            "costs": 0,
            "net_profit": 0,
            "roi": 0.0
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire"""
        return {
            "channel_id": self.channel_id,
            "node1_pub": self.node1_pub,
            "node2_pub": self.node2_pub,
            "capacity": self.capacity,
            "local_balance": self.local_balance,
            "remote_balance": self.remote_balance,
            "local_ratio": self.local_ratio,
            "active": self.active,
            "private": self.private,
            "initiator": self.initiator,
            "lnd_data": self.lnd_data,
            "lnrouter_data": self.lnrouter_data,
            "amboss_data": self.amboss_data,
            "mcp_data": self.mcp_data,
            "forwarding_stats": self.forwarding_stats,
            "rebalancing_stats": self.rebalancing_stats,
            "profitability": self.profitability
        }
        
    @property
    def stuck_index(self) -> float:
        """Calcule un index de blocage pour le canal
        
        Un index plus élevé indique un canal plus susceptible d'être bloqué.
        Facteurs: ratio de balance, temps depuis le dernier forward, volume de forwarding
        """
        # Facteur 1: Déséquilibre (0 = parfaitement équilibré, 1 = complètement déséquilibré)
        balance_factor = abs(self.local_ratio - 0.5) * 2
        
        # Facteur 2: Temps depuis le dernier forward (normalisé sur 30 jours)
        last_forward_time = self.forwarding_stats.get("last_forward_time")
        time_factor = 0.0
        if last_forward_time:
            last_forward = datetime.fromisoformat(last_forward_time)
            days_since_forward = (datetime.now() - last_forward).days
            time_factor = min(1.0, days_since_forward / 30.0)
        else:
            time_factor = 1.0  # Jamais utilisé = maximum
            
        # Facteur 3: Volume de forwarding (inverse, normalisé)
        volume_factor = 0.0
        total_forwards = self.forwarding_stats.get("total_forwards", 0)
        if total_forwards < 10:
            volume_factor = 1.0 - (total_forwards / 10.0)
        
        # Combiner les facteurs (moyenne pondérée)
        stuck_index = (balance_factor * 0.3) + (time_factor * 0.5) + (volume_factor * 0.2)
        return round(stuck_index * 100)  # Score sur 100
    
    @property
    def is_profitable(self) -> bool:
        """Détermine si le canal est rentable"""
        return self.profitability["net_profit"] > 0
    
    @classmethod
    def from_lnd_channel(cls, lnd_channel: Dict[str, Any]) -> 'EnrichedChannel':
        """Crée un objet EnrichedChannel à partir des données d'un canal LND"""
        channel_id = str(lnd_channel.get("channel_id", "unknown"))
        channel = cls(channel_id)
        
        channel.node1_pub = settings.NODE_PUBKEY
        channel.node2_pub = lnd_channel.get("remote_pubkey")
        channel.capacity = lnd_channel.get("capacity", 0)
        channel.local_balance = lnd_channel.get("local_balance", 0)
        channel.remote_balance = lnd_channel.get("remote_balance", 0)
        
        if channel.capacity > 0:
            channel.local_ratio = channel.local_balance / channel.capacity
            
        channel.active = lnd_channel.get("active", False)
        channel.private = lnd_channel.get("private", False)
        channel.initiator = lnd_channel.get("initiator", False)
        
        # Stocker les données complètes
        channel.lnd_data = lnd_channel
        
        return channel


class EnrichedNode:
    """Classe représentant un nœud LN enrichi avec des données de multiples sources"""
    
    def __init__(self, pubkey: str):
        self.pubkey = pubkey
        self.alias = None
        self.color = None
        self.channels = {}  # channel_id -> EnrichedChannel
        self.amboss_data = {}  # Uptime, scoring, etc.
        self.lnrouter_data = {}  # Connectivité, potentiel de routage
        self.lnd_data = {}  # Canaux ouverts, politique de frais
        self.mempool_data = {}  # Contexte chaîne
        self.performance_metrics = {}  # Agrégation de métriques de performance
        self.last_update = datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire"""
        return {
            "pubkey": self.pubkey,
            "alias": self.alias,
            "color": self.color,
            "channels": {cid: channel.to_dict() for cid, channel in self.channels.items()},
            "amboss_data": self.amboss_data,
            "lnrouter_data": self.lnrouter_data,
            "lnd_data": self.lnd_data,
            "mempool_data": self.mempool_data,
            "performance_metrics": self.performance_metrics,
            "last_update": self.last_update
        }
        
    def add_channel(self, channel: EnrichedChannel) -> None:
        """Ajoute un canal à ce nœud"""
        self.channels[channel.channel_id] = channel
        
    def get_stuck_channels(self, threshold: int = 70) -> List[EnrichedChannel]:
        """Récupère les canaux potentiellement bloqués
        
        Args:
            threshold: Seuil d'index de blocage (0-100) au-dessus duquel un canal est considéré comme bloqué
            
        Returns:
            Liste des canaux considérés comme bloqués
        """
        return [c for c in self.channels.values() if c.stuck_index >= threshold]
    
    def get_unprofitable_channels(self) -> List[EnrichedChannel]:
        """Récupère les canaux non rentables
        
        Returns:
            Liste des canaux considérés comme non rentables
        """
        return [c for c in self.channels.values() if not c.is_profitable]
    
    @property
    def total_capacity(self) -> int:
        """Calcule la capacité totale des canaux du nœud"""
        return sum(c.capacity for c in self.channels.values())
    
    @property
    def total_local_balance(self) -> int:
        """Calcule la balance locale totale des canaux du nœud"""
        return sum(c.local_balance for c in self.channels.values())
    
    @property
    def total_remote_balance(self) -> int:
        """Calcule la balance distante totale des canaux du nœud"""
        return sum(c.remote_balance for c in self.channels.values())
    
    @classmethod
    def from_all_sources(cls, pubkey: str, node_aggregator: 'NodeAggregator') -> 'EnrichedNode':
        """Crée un objet EnrichedNode à partir de toutes les sources disponibles"""
        node = cls(pubkey)
        
        # Récupérer les données de toutes les sources
        node_aggregator.enrich_node(node)
        
        return node


class NodeAggregator:
    """Agrégateur de données de nœuds et canaux"""
    
    def __init__(self, lnd_client: LNDClient = None, lnrouter_client: LNRouterClient = None):
        """Initialise l'agrégateur de données
        
        Args:
            lnd_client: Client LND
            lnrouter_client: Client LNRouter
        """
        self.lnd_client = lnd_client or DataSourceFactory.get_lnd_client()
        self.lnrouter_client = lnrouter_client or DataSourceFactory.get_lnrouter_client()
        self.data_source = DataSourceFactory.get_data_source()
    
    async def get_enriched_node(self, pubkey: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations enrichies d'un nœud"""
        try:
            # Essayer d'abord la source de données par défaut
            node = await self.data_source.get_node_details(pubkey)
            
            if node is None:
                # Essayer la source locale si la première tentative échoue
                local_source = DataSourceFactory.get_data_source("local")
                if local_source != self.data_source:
                    node = await local_source.get_node_details(pubkey)
            
            if node is None:
                # Essayer MCP en dernier recours
                mcp_source = DataSourceFactory.get_data_source("mcp")
                if mcp_source != self.data_source and mcp_source != local_source:
                    node = await mcp_source.get_node_details(pubkey)
            
            if node is None:
                logger.warning(f"Nœud non trouvé pour pubkey {pubkey}")
                return None
            
            # Récupérer les canaux liés au nœud
            channels = await self.data_source.get_node_channels(pubkey)
            
            # Enrichir les données
            node["channels"] = channels
            node["num_channels"] = len(channels)
            node["total_capacity"] = sum(c.get("capacity", 0) for c in channels)
            node["last_updated"] = datetime.now().isoformat()
            
            return node
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations enrichies du nœud {pubkey}: {e}")
            return None
    
    async def get_enriched_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations enrichies d'un canal"""
        try:
            # Essayer d'abord la source de données par défaut
            channel = await self.data_source.get_channel_details(channel_id)
            
            if channel is None:
                # Essayer la source locale si la première tentative échoue
                local_source = DataSourceFactory.get_data_source("local")
                if local_source != self.data_source:
                    channel = await local_source.get_channel_details(channel_id)
            
            if channel is None:
                # Essayer MCP en dernier recours
                mcp_source = DataSourceFactory.get_data_source("mcp")
                if mcp_source != self.data_source and mcp_source != local_source:
                    channel = await mcp_source.get_channel_details(channel_id)
            
            if channel is None:
                logger.warning(f"Canal non trouvé pour ID {channel_id}")
                return None
            
            # Récupérer les informations des nœuds aux extrémités
            node1_pub = channel.get("node1_pub")
            node2_pub = channel.get("node2_pub")
            
            if node1_pub:
                try:
                    node1 = await self.data_source.get_node_details(node1_pub)
                    if node1:
                        channel["node1_alias"] = node1.get("alias", "")
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération des informations du nœud {node1_pub}: {e}")
            
            if node2_pub:
                try:
                    node2 = await self.data_source.get_node_details(node2_pub)
                    if node2:
                        channel["node2_alias"] = node2.get("alias", "")
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération des informations du nœud {node2_pub}: {e}")
            
            # Ajouter des informations supplémentaires
            channel["last_updated"] = datetime.now().isoformat()
            
            return channel
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations enrichies du canal {channel_id}: {e}")
            return None
    
    async def get_network_context(self) -> Dict[str, Any]:
        """Récupère le contexte réseau global"""
        try:
            # Récupérer les statistiques du réseau
            network_stats = await self.data_source.get_network_stats()
            
            # Récupérer les statistiques des canaux
            channels_stats = await self.data_source.get_channels_stats()
            
            # Récupérer les informations du nœud local
            node_info = self.lnd_client.get_node_info()
            
            # Agréger les informations
            context = {
                "timestamp": datetime.now().isoformat(),
                "network": network_stats,
                "channels": channels_stats,
                "local_node": {
                    "pubkey": node_info.get("pubkey"),
                    "alias": node_info.get("alias"),
                    "num_active_channels": node_info.get("num_active_channels"),
                    "num_inactive_channels": node_info.get("num_inactive_channels"),
                    "block_height": node_info.get("block_height"),
                    "synced_to_chain": node_info.get("synced_to_chain")
                },
                "source": network_stats.get("source") or "mixed"
            }
            
            return context
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du contexte réseau: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def synchronize_data(self, pubkeys: List[str] = None) -> Dict:
        """Synchronise les données pour les nœuds spécifiés ou tous les nœuds connus
        
        Args:
            pubkeys: Liste des pubkeys à synchroniser (si None, utilise le nœud local)
            
        Returns:
            Rapport de synchronisation
        """
        if not pubkeys:
            pubkeys = [settings.NODE_PUBKEY]
            
        results = {
            "timestamp": datetime.now().isoformat(),
            "total": len(pubkeys),
            "successful": 0,
            "failed": 0,
            "failures": {}
        }
        
        for pubkey in pubkeys:
            try:
                # Forcer la mise à jour du cache
                await self.get_enriched_node(pubkey)
                results["successful"] += 1
            except Exception as e:
                logger.error(f"Erreur lors de la synchronisation du nœud {pubkey}: {e}")
                results["failed"] += 1
                results["failures"][pubkey] = str(e)
                
        return results
    
    async def export_to_vector_store(self, vector_store_client) -> int:
        """Exporte les données enrichies vers un vector store pour RAG
        
        Args:
            vector_store_client: Client pour le vector store
            
        Returns:
            Nombre d'enregistrements exportés
        """
        # Ce code est un placeholder - l'implémentation réelle dépendrait du vector store spécifique
        logger.info("Export vers vector store non implémenté")
        return 0
    
    def get_channel_recommendations(self, node: EnrichedNode) -> List[Dict]:
        """Génère des recommandations pour les canaux du nœud
        
        Args:
            node: Nœud enrichi
            
        Returns:
            Liste de recommandations
        """
        recommendations = []
        
        # Recommandations pour les canaux bloqués
        stuck_channels = node.get_stuck_channels(threshold=70)
        for channel in stuck_channels:
            recommendations.append({
                "type": "stuck_channel",
                "channel_id": channel.channel_id,
                "peer_pubkey": channel.node2_pub,
                "peer_alias": None,  # À enrichir
                "severity": "high" if channel.stuck_index > 85 else "medium",
                "local_ratio": channel.local_ratio,
                "suggestion": "rebalance" if channel.local_ratio > 0.7 else "wait_for_payments" if channel.local_ratio < 0.3 else "consider_closing",
                "details": f"Canal potentiellement bloqué (indice: {channel.stuck_index}/100). "
                           f"Balance locale: {channel.local_ratio:.1%}."
            })
            
        # Recommandations pour les canaux non rentables
        unprofitable_channels = node.get_unprofitable_channels()
        for channel in unprofitable_channels:
            if channel not in stuck_channels:  # Éviter les doublons
                recommendations.append({
                    "type": "unprofitable_channel",
                    "channel_id": channel.channel_id,
                    "peer_pubkey": channel.node2_pub,
                    "peer_alias": None,  # À enrichir
                    "severity": "medium",
                    "net_profit": channel.profitability["net_profit"],
                    "suggestion": "adjust_fees" if channel.forwarding_stats["total_forwards"] > 0 else "close_channel",
                    "details": f"Canal non rentable. Profit net: {channel.profitability['net_profit']} sats. "
                               f"Forwards: {channel.forwarding_stats['total_forwards']}."
                })
                
        # Recommandations pour l'équilibrage global du nœud
        local_balance_ratio = node.total_local_balance / node.total_capacity if node.total_capacity > 0 else 0
        if local_balance_ratio < 0.3:
            recommendations.append({
                "type": "node_balance",
                "severity": "medium",
                "local_ratio": local_balance_ratio,
                "suggestion": "add_inbound_liquidity",
                "details": f"Balance globale déséquilibrée vers l'inbound ({local_balance_ratio:.1%} local). "
                           f"Envisagez d'ajouter de la liquidité sortante."
            })
        elif local_balance_ratio > 0.7:
            recommendations.append({
                "type": "node_balance",
                "severity": "medium",
                "local_ratio": local_balance_ratio,
                "suggestion": "add_outbound_liquidity",
                "details": f"Balance globale déséquilibrée vers l'outbound ({local_balance_ratio:.1%} local). "
                           f"Envisagez d'ajouter de la liquidité entrante ou d'ouvrir plus de canaux."
            })
            
        return recommendations 