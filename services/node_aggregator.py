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
    """Agrégateur de données pour les nœuds LN depuis différentes sources"""
    
    def __init__(self, lnd_client: LNDClient = None, lnrouter_client: LNRouterClient = None, 
                 mcp_service: MCPService = None, feustey_service: FeusteyService = None):
        """Initialise l'agrégateur de nœuds
        
        Args:
            lnd_client: Client LND
            lnrouter_client: Client LNRouter
            mcp_service: Service MCP
            feustey_service: Service Feustey
        """
        self.lnd_client = lnd_client or LNDClient() 
        self.lnrouter_client = lnrouter_client or LNRouterClient()
        self.mcp_service = mcp_service or MCPService()
        self.feustey_service = feustey_service or FeusteyService()
        self.cache = {}  # Cache des nœuds enrichis
        self.cache_expiry = {}  # Expiration du cache par nœud
        self.cache_duration = timedelta(hours=1)  # Durée de validité du cache
        
    async def get_enriched_node(self, pubkey: str, force_refresh: bool = False) -> EnrichedNode:
        """Récupère un objet nœud enrichi avec toutes les sources de données
        
        Args:
            pubkey: Clé publique du nœud
            force_refresh: Si True, force la mise à jour du cache
            
        Returns:
            Objet EnrichedNode avec les données enrichies
        """
        now = datetime.now()
        
        # Vérifier si nous avons un cache valide
        if not force_refresh and pubkey in self.cache:
            expiry = self.cache_expiry.get(pubkey)
            if expiry and now < expiry:
                logger.debug(f"Utilisation du cache pour le nœud {pubkey}")
                return self.cache[pubkey]
        
        # Créer un nouvel objet EnrichedNode
        node = EnrichedNode(pubkey)
        
        # Enrichir le nœud avec toutes les sources
        await self.enrich_node(node)
        
        # Mettre en cache
        self.cache[pubkey] = node
        self.cache_expiry[pubkey] = now + self.cache_duration
        
        return node
    
    async def enrich_node(self, node: EnrichedNode) -> None:
        """Enrichit un nœud avec toutes les sources de données
        
        Args:
            node: Objet EnrichedNode à enrichir
        """
        # Récupérer les données de chaque source en parallèle
        tasks = [
            self._enrich_with_lnd(node),
            self._enrich_with_lnrouter(node),
            self._enrich_with_mcp(node),
            self._enrich_with_mempool(node)
        ]
        
        # Exécuter toutes les tâches en parallèle
        await asyncio.gather(*tasks)
        
        # Mettre à jour la date de dernière mise à jour
        node.last_update = datetime.now().isoformat()
    
    async def _enrich_with_lnd(self, node: EnrichedNode) -> None:
        """Enrichit un nœud avec les données LND
        
        Args:
            node: Objet EnrichedNode à enrichir
        """
        try:
            # Si c'est notre nœud, récupérer les informations complètes
            if node.pubkey == settings.NODE_PUBKEY:
                node_info = self.lnd_client.get_node_info()
                node.alias = node_info.get("alias")
                node.color = node_info.get("color")
                node.lnd_data = node_info
                
                # Récupérer les canaux
                channels = self.lnd_client.list_channels()
                
                for lnd_channel in channels:
                    channel = EnrichedChannel.from_lnd_channel(lnd_channel)
                    node.add_channel(channel)
                    
                # Récupérer l'historique des forwards pour enrichir les canaux
                forwards = self.lnd_client.get_forwarding_history(limit=1000)
                
                # Tracker des canaux vus dans les forwards
                forwarding_channels = set()
                
                # Agréger les données de forwarding par canal
                for event in forwards.get("forwarding_events", []):
                    chan_id_in = str(event.get("chan_id_in"))
                    chan_id_out = str(event.get("chan_id_out"))
                    amt_in = event.get("amt_in", 0)
                    amt_out = event.get("amt_out", 0)
                    fee = event.get("fee", 0)
                    timestamp = event.get("timestamp")
                    
                    forwarding_channels.add(chan_id_in)
                    forwarding_channels.add(chan_id_out)
                    
                    # Mettre à jour les statistiques du canal entrant
                    if chan_id_in in node.channels:
                        channel = node.channels[chan_id_in]
                        channel.forwarding_stats["total_forwards"] += 1
                        channel.forwarding_stats["total_amount_forwards"] += amt_in
                        channel.forwarding_stats["total_fees"] += fee
                        
                        # Mettre à jour la dernière date si nécessaire
                        current_last = channel.forwarding_stats.get("last_forward_time")
                        if not current_last or timestamp > current_last:
                            channel.forwarding_stats["last_forward_time"] = timestamp
                            
                        # Mettre à jour les statistiques de profitabilité
                        channel.profitability["revenue"] += fee
                    
                    # Mettre à jour les statistiques du canal sortant
                    if chan_id_out in node.channels:
                        channel = node.channels[chan_id_out]
                        channel.forwarding_stats["total_forwards"] += 1
                        channel.forwarding_stats["total_amount_forwards"] += amt_out
                        
                        # Mettre à jour la dernière date si nécessaire
                        current_last = channel.forwarding_stats.get("last_forward_time")
                        if not current_last or timestamp > current_last:
                            channel.forwarding_stats["last_forward_time"] = timestamp
                
                # Calculer la profitabilité pour tous les canaux
                for channel_id, channel in node.channels.items():
                    # Si le canal n'a jamais vu de forwarding, marquer comme potentiellement non rentable
                    if channel_id not in forwarding_channels:
                        channel.profitability["net_profit"] = -1  # Coût d'opportunité
                    else:
                        # Calculer le profit net
                        revenue = channel.profitability.get("revenue", 0)
                        costs = channel.profitability.get("costs", 0)
                        channel.profitability["net_profit"] = revenue - costs
                        
                        # Calculer le ROI si nous avons une capacité
                        if channel.capacity > 0:
                            channel.profitability["roi"] = channel.profitability["net_profit"] / channel.capacity
            else:
                # Pour les nœuds distants, on n'a pas accès directement aux données LND
                pass
                
        except Exception as e:
            logger.error(f"Erreur lors de l'enrichissement avec LND: {e}")
    
    async def _enrich_with_lnrouter(self, node: EnrichedNode) -> None:
        """Enrichit un nœud avec les données LNRouter
        
        Args:
            node: Objet EnrichedNode à enrichir
        """
        try:
            # Récupérer les informations du nœud depuis LNRouter
            node_info = await self.lnrouter_client.get_node_info(node.pubkey)
            
            if not node.alias and "alias" in node_info:
                node.alias = node_info.get("alias")
                
            if not node.color and "color" in node_info:
                node.color = node_info.get("color")
                
            # Stocker les données complètes
            node.lnrouter_data = node_info
            
            # Si ce nœud a des canaux dans LNRouter, enrichir nos données de canaux
            for channel_data in node_info.get("channels", []):
                channel_id = str(channel_data.get("channel_id"))
                
                # Si nous connaissons déjà ce canal, enrichir ses données
                if channel_id in node.channels:
                    channel = node.channels[channel_id]
                    channel.lnrouter_data = channel_data
                    
                    # Mettre à jour la capacité si elle n'est pas définie
                    if not channel.capacity and "capacity" in channel_data:
                        channel.capacity = channel_data.get("capacity")
                    
                # Sinon, créer un nouveau canal avec ces données
                else:
                    # Pour l'instant, ne pas créer de nouveaux canaux si on ne les connaît pas déjà
                    pass
                    
        except Exception as e:
            logger.error(f"Erreur lors de l'enrichissement avec LNRouter: {e}")
    
    async def _enrich_with_mcp(self, node: EnrichedNode) -> None:
        """Enrichit un nœud avec les données MCP
        
        Args:
            node: Objet EnrichedNode à enrichir
        """
        try:
            # Récupérer les informations du nœud depuis MCP
            node_info = await self.mcp_service.get_node_details(node.pubkey)
            
            if node_info:
                if not node.alias and "alias" in node_info:
                    node.alias = node_info.get("alias")
                    
                if not node.color and "color" in node_info:
                    node.color = node_info.get("color")
                    
                # Stocker les données complètes
                node.mcp_data = node_info
                
                # Si ce nœud a des canaux dans MCP, enrichir nos données de canaux
                channels = await self.mcp_service.get_node_channels(node.pubkey)
                
                for channel_data in channels:
                    channel_id = str(channel_data.get("channel_id"))
                    
                    # Si nous connaissons déjà ce canal, enrichir ses données
                    if channel_id in node.channels:
                        channel = node.channels[channel_id]
                        channel.mcp_data = channel_data
                        
                        # Mettre à jour la capacité si elle n'est pas définie
                        if not channel.capacity and "capacity" in channel_data:
                            channel.capacity = channel_data.get("capacity")
                    
                    # Sinon, créer un nouveau canal avec ces données
                    else:
                        # Pour l'instant, ne pas créer de nouveaux canaux si on ne les connaît pas déjà
                        pass
                        
        except Exception as e:
            logger.error(f"Erreur lors de l'enrichissement avec MCP: {e}")
    
    async def _enrich_with_mempool(self, node: EnrichedNode) -> None:
        """Enrichit un nœud avec les données Mempool
        
        Args:
            node: Objet EnrichedNode à enrichir
        """
        # Pour l'instant, nous n'intégrons pas directement avec Mempool
        # Mais nous pourrions à l'avenir récupérer des données sur les frais, la congestion, etc.
        pass
    
    async def get_enriched_channels(self, pubkey: str = None) -> List[EnrichedChannel]:
        """Récupère des informations enrichies sur les canaux
        
        Args:
            pubkey: Clé publique du nœud (si None, utilise le nœud local)
            
        Returns:
            Liste des canaux enrichis
        """
        node_pubkey = pubkey or settings.NODE_PUBKEY
        node = await self.get_enriched_node(node_pubkey)
        return list(node.channels.values())
    
    async def get_network_context(self) -> Dict:
        """Récupère le contexte global du réseau
        
        Returns:
            Dictionnaire avec le contexte du réseau
        """
        try:
            # Récupérer les statistiques du réseau depuis MCP
            mcp_stats = await self.mcp_service.get_network_stats()
            
            # Récupérer les statistiques du réseau depuis LNRouter
            lnrouter_stats = await self.lnrouter_client.get_network_stats()
            
            # Récupérer l'analyse de topologie depuis LNRouter
            topology = await self.lnrouter_client.analyze_network_topology()
            
            # Construire le contexte
            context = {
                "timestamp": datetime.now().isoformat(),
                "mcp": {
                    "num_nodes": mcp_stats.get("num_nodes", 0),
                    "num_channels": mcp_stats.get("num_channels", 0),
                    "total_capacity": mcp_stats.get("total_capacity", 0),
                    "avg_capacity_per_channel": mcp_stats.get("avg_capacity_per_channel", 0),
                    "avg_capacity_per_node": mcp_stats.get("avg_capacity_per_node", 0)
                },
                "lnrouter": {
                    "num_nodes": lnrouter_stats.get("num_nodes", 0),
                    "num_channels": lnrouter_stats.get("num_channels", 0),
                    "total_capacity": lnrouter_stats.get("total_capacity", 0),
                    "network_diameter": topology.get("network_diameter", -1),
                    "density": topology.get("density", 0),
                    "avg_degree": topology.get("avg_degree", 0),
                    "largest_component_ratio": topology.get("largest_component_ratio", 0)
                },
                "top_nodes": topology.get("top_betweenness_nodes", [])[:10]
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
                await self.get_enriched_node(pubkey, force_refresh=True)
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