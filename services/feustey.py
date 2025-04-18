import httpx
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.core.config import settings


class FeusteyService:
    """Service pour interagir avec l'API du nœud Feustey"""
    
    def __init__(self):
        self.base_url = settings.FEUSTEY_API_URL
        self.api_key = settings.FEUSTEY_API_KEY
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Any:
        """Effectue une requête à l'API Feustey"""
        if not self.base_url:
            # Retourne des données fictives pour le développement si aucune URL n'est configurée
            return self._get_mock_data(endpoint, params)
            
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
    
    def _get_mock_data(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """Génère des données fictives pour le développement"""
        mock_data = {
            "/v1/getinfo": self._mock_node_info(),
            "/v1/channel/listchannels": self._mock_channels_list(),
            "/v1/balance/channels": self._mock_channel_balance(),
            "/v1/forwards": self._mock_forwards(params.get("start_time") if params else None, 
                                               params.get("end_time") if params else None),
            "/v1/network/info": self._mock_network_info(),
        }
        
        # Trouver la clé la plus pertinente dans mock_data qui correspond à endpoint
        matching_key = next((k for k in mock_data.keys() if k in endpoint), None)
        return mock_data.get(matching_key, {"error": "Not implemented in mock data"})
    
    # Méthodes pour le nœud
    
    async def get_node_status(self) -> Dict[str, Any]:
        """Récupère le statut actuel du nœud"""
        node_info = await self._make_request("GET", "/v1/getinfo")
        
        # Transformer les données pour correspondre au format attendu
        now = datetime.now()
        return {
            "node_id": node_info.get("identity_pubkey"),
            "alias": node_info.get("alias"),
            "color": node_info.get("color"),
            "version": node_info.get("version"),
            "is_online": True,
            "uptime": node_info.get("uptime", 3600),
            "block_height": node_info.get("block_height"),
            "synced_to_chain": node_info.get("synced_to_chain"),
            "synced_to_graph": node_info.get("synced_to_graph"),
            "num_active_channels": node_info.get("num_active_channels"),
            "num_inactive_channels": node_info.get("num_inactive_channels"),
            "num_pending_channels": node_info.get("num_pending_channels"),
            "total_capacity": node_info.get("total_capacity"),
            "total_local_balance": node_info.get("total_local_balance", 0),
            "total_remote_balance": node_info.get("total_remote_balance", 0),
            "total_unsettled_balance": node_info.get("total_unsettled_balance", 0),
            "total_pending_htlcs": node_info.get("total_pending_htlcs", 0),
            "last_update": now
        }
    
    async def get_node_metrics(self, timeframe: str = "day") -> Dict[str, Any]:
        """Récupère les métriques du nœud sur une période donnée"""
        now = datetime.now()
        
        # Définir l'intervalle de temps en fonction du timeframe
        if timeframe == "hour":
            start_time = int((now - timedelta(hours=1)).timestamp())
        elif timeframe == "day":
            start_time = int((now - timedelta(days=1)).timestamp())
        elif timeframe == "week":
            start_time = int((now - timedelta(weeks=1)).timestamp())
        elif timeframe == "month":
            start_time = int((now - timedelta(days=30)).timestamp())
        elif timeframe == "year":
            start_time = int((now - timedelta(days=365)).timestamp())
        else:
            start_time = int((now - timedelta(days=1)).timestamp())
        
        end_time = int(now.timestamp())
        
        params = {
            "start_time": start_time,
            "end_time": end_time
        }
        
        forwards = await self._make_request("GET", "/v1/forwards", params=params)
        
        # Calculer les métriques
        total_forwards = len(forwards)
        total_amount = sum(fw.get("amt_out", 0) for fw in forwards)
        total_fees = sum(fw.get("fee", 0) for fw in forwards)
        
        # Agréger l'activité par canal
        channel_activity = {}
        for fw in forwards:
            chan_id_in = fw.get("chan_id_in", "unknown")
            chan_id_out = fw.get("chan_id_out", "unknown")
            
            if chan_id_in not in channel_activity:
                channel_activity[chan_id_in] = 0
            if chan_id_out not in channel_activity:
                channel_activity[chan_id_out] = 0
                
            channel_activity[chan_id_in] += 1
            channel_activity[chan_id_out] += 1
        
        # Calculer les échecs de paiement (fictifs pour la démo)
        payment_failures = {
            "no_route": 5,
            "insufficient_balance": 3,
            "timeout": 7,
            "offline_peer": 2
        }
        
        # Calculer les événements HTLC (fictifs pour la démo)
        htlc_events = {
            "forward": total_forwards,
            "forward_fail": 15,
            "settle": total_forwards - 2,
            "timeout": 2
        }
        
        # Générer les tendances (fictives pour la démo)
        fee_revenue_trend = []
        active_channels_trend = []
        
        # Diviser l'intervalle en 10 points pour les tendances
        interval = (end_time - start_time) / 10
        for i in range(10):
            point_time = datetime.fromtimestamp(start_time + i * interval)
            fee_revenue_trend.append({
                "time": point_time,
                "value": 1000 + i * 200
            })
            active_channels_trend.append({
                "time": point_time,
                "value": 10 + (i % 3)
            })
        
        return {
            "period": timeframe,
            "forwards": forwards,
            "total_forwards": total_forwards,
            "total_forwarded_amount": total_amount,
            "total_fees_earned": total_fees,
            "average_fee_rate": total_fees / total_amount * 1000000 if total_amount > 0 else 0,
            "channel_activity": channel_activity,
            "success_rate": 0.95,  # 95% fictif
            "payment_failures": payment_failures,
            "htlc_events": htlc_events,
            "fee_revenue_trend": fee_revenue_trend,
            "active_channels_trend": active_channels_trend
        }
    
    async def get_liquidity_overview(self) -> Dict[str, Any]:
        """Récupère une vue d'ensemble de la liquidité du nœud"""
        # Récupérer les informations des canaux
        channels = await self._make_request("GET", "/v1/channel/listchannels")
        
        # Créer les objets ChannelLiquidity
        channel_liquidity_list = []
        total_local = 0
        total_remote = 0
        total_capacity = 0
        
        for chan in channels.get("channels", []):
            capacity = chan.get("capacity", 0)
            local_balance = chan.get("local_balance", 0)
            remote_balance = chan.get("remote_balance", 0)
            
            local_percent = local_balance / capacity if capacity > 0 else 0
            
            channel_liquidity = {
                "channel_id": chan.get("chan_id"),
                "peer_alias": chan.get("peer_alias", "Unknown"),
                "capacity": capacity,
                "local_balance": local_balance,
                "remote_balance": remote_balance,
                "local_percent": local_percent,
                "inbound_liquidity": remote_balance,
                "outbound_liquidity": local_balance,
                "is_active": chan.get("active", True)
            }
            
            channel_liquidity_list.append(channel_liquidity)
            total_local += local_balance
            total_remote += remote_balance
            total_capacity += capacity
        
        # Trier les canaux en fonction de leur équilibre
        balanced_threshold = 0.3  # Considérer un canal comme équilibré si la distribution est de 30-70% ou mieux
        
        unbalanced_inbound = []
        unbalanced_outbound = []
        balanced_channels = []
        
        for cl in channel_liquidity_list:
            local_percent = cl["local_percent"]
            if local_percent < balanced_threshold:
                unbalanced_inbound.append(cl)
            elif local_percent > (1 - balanced_threshold):
                unbalanced_outbound.append(cl)
            else:
                balanced_channels.append(cl)
        
        return {
            "total_balance": total_local + total_remote,
            "total_capacity": total_capacity,
            "total_inbound": total_remote,
            "total_outbound": total_local,
            "liquidity_ratio": total_local / total_remote if total_remote > 0 else float('inf'),
            "balanced_threshold": balanced_threshold,
            "unbalanced_inbound": unbalanced_inbound,
            "unbalanced_outbound": unbalanced_outbound,
            "balanced_channels": balanced_channels,
            "updated_at": datetime.now()
        }
    
    async def get_node_recommendations(self) -> List[Dict[str, Any]]:
        """Récupère des recommandations pour améliorer les performances du nœud"""
        # Récupérer les données nécessaires
        liquidity_overview = await self.get_liquidity_overview()
        node_metrics = await self.get_node_metrics(timeframe="week")
        
        recommendations = []
        
        # Vérifier les canaux déséquilibrés
        if len(liquidity_overview["unbalanced_inbound"]) > 2:
            recommendations.append({
                "type": "liquidity_rebalance",
                "severity": "medium",
                "title": "Canaux avec trop de liquidité entrante",
                "description": "Plusieurs canaux ont une liquidité déséquilibrée vers l'entrée. Envisagez de les rééquilibrer pour améliorer votre capacité à envoyer des paiements.",
                "channels": [c["channel_id"] for c in liquidity_overview["unbalanced_inbound"][:3]],
                "action": "rebalance"
            })
        
        if len(liquidity_overview["unbalanced_outbound"]) > 2:
            recommendations.append({
                "type": "liquidity_rebalance",
                "severity": "medium",
                "title": "Canaux avec trop de liquidité sortante",
                "description": "Plusieurs canaux ont une liquidité déséquilibrée vers la sortie. Envisagez de les rééquilibrer pour améliorer votre capacité à recevoir des paiements.",
                "channels": [c["channel_id"] for c in liquidity_overview["unbalanced_outbound"][:3]],
                "action": "rebalance"
            })
        
        # Vérifier le taux de frais
        if node_metrics["average_fee_rate"] < 10:
            recommendations.append({
                "type": "fee_policy",
                "severity": "low",
                "title": "Taux de frais bas",
                "description": "Votre taux de frais moyen est inférieur à 10 ppm. Envisagez d'augmenter vos frais sur certains canaux pour optimiser vos revenus.",
                "action": "adjust_fees"
            })
        
        # Recommandation sur la diversification des canaux
        if len(liquidity_overview["balanced_channels"]) < 5:
            recommendations.append({
                "type": "channel_management",
                "severity": "medium",
                "title": "Diversification des canaux",
                "description": "Vous avez peu de canaux bien équilibrés. Envisagez d'ouvrir des canaux avec des nœuds bien connectés pour améliorer votre position dans le réseau.",
                "action": "open_channels"
            })
        
        return recommendations
    
    async def get_node_data(self) -> Dict[str, Any]:
        """Récupère les données complètes du nœud"""
        # Combiner différentes sources de données
        node_status = await self.get_node_status()
        liquidity = await self.get_liquidity_overview()
        
        return {
            "node_id": node_status["node_id"],
            "alias": node_status["alias"],
            "status": node_status,
            "liquidity": {
                "total_inbound": liquidity["total_inbound"],
                "total_outbound": liquidity["total_outbound"],
                "liquidity_ratio": liquidity["liquidity_ratio"]
            },
            "channels": {
                "active": node_status["num_active_channels"],
                "inactive": node_status["num_inactive_channels"],
                "pending": node_status["num_pending_channels"]
            }
        }
    
    # Méthodes pour générer des données fictives
    
    def _mock_node_info(self) -> Dict[str, Any]:
        """Génère des informations fictives sur le nœud"""
        return {
            "identity_pubkey": "03a8f58b60f9b6ea4b7f06410620731d17b873e5eb03f72733bf345332554b399c",
            "alias": "FeusteyNode",
            "color": "#3399ff",
            "version": "v0.16.0-beta",
            "uptime": 2592000,  # 30 jours en secondes
            "block_height": 810000,
            "synced_to_chain": True,
            "synced_to_graph": True,
            "num_active_channels": 15,
            "num_inactive_channels": 2,
            "num_pending_channels": 1,
            "total_capacity": 25000000,
            "total_local_balance": 12500000,
            "total_remote_balance": 12500000,
            "total_unsettled_balance": 0,
            "total_pending_htlcs": 0
        }
    
    def _mock_channels_list(self) -> Dict[str, List[Dict[str, Any]]]:
        """Génère une liste fictive de canaux"""
        channels = []
        for i in range(18):
            active = i < 15
            local_balance = 800000 if i % 3 == 0 else (200000 if i % 3 == 1 else 500000)
            capacity = 1000000
            remote_balance = capacity - local_balance
            
            channels.append({
                "chan_id": f"7619455224960{i:02d}",
                "capacity": capacity,
                "local_balance": local_balance,
                "remote_balance": remote_balance,
                "active": active,
                "peer_alias": f"Node{i:02d}",
                "peer_pubkey": f"02b67e51{'0' * 40}{i:02d}"
            })
        
        return {"channels": channels}
    
    def _mock_channel_balance(self) -> Dict[str, Any]:
        """Génère des données fictives de balance des canaux"""
        return {
            "local_balance": {
                "sat": 12500000,
                "msat": 12500000000
            },
            "remote_balance": {
                "sat": 12500000,
                "msat": 12500000000
            },
            "unsettled_local_balance": {
                "sat": 0,
                "msat": 0
            },
            "unsettled_remote_balance": {
                "sat": 0,
                "msat": 0
            },
            "pending_open_local_balance": {
                "sat": 1000000,
                "msat": 1000000000
            },
            "pending_open_remote_balance": {
                "sat": 0,
                "msat": 0
            }
        }
    
    def _mock_forwards(self, start_time: Optional[int] = None, end_time: Optional[int] = None) -> List[Dict[str, Any]]:
        """Génère des données fictives de transferts"""
        if not start_time:
            start_time = int((datetime.now() - timedelta(days=1)).timestamp())
        if not end_time:
            end_time = int(datetime.now().timestamp())
        
        # Générer des données aléatoires pour la période spécifiée
        forwards = []
        time_span = end_time - start_time
        num_forwards = min(100, time_span // 300)  # environ un forward tous les 5 minutes max
        
        for i in range(num_forwards):
            timestamp = start_time + (i * time_span // num_forwards)
            amt = 10000 + (i % 10) * 5000
            fee = int(amt * 0.0001)  # 100 ppm
            
            forwards.append({
                "timestamp": timestamp,
                "chan_id_in": f"7619455224960{i % 18:02d}",
                "chan_id_out": f"7619455224960{(i + 5) % 18:02d}",
                "amt_in": amt,
                "amt_out": amt - fee,
                "fee": fee,
                "fee_msat": fee * 1000
            })
        
        return forwards
    
    def _mock_network_info(self) -> Dict[str, Any]:
        """Génère des données fictives sur le réseau"""
        return {
            "graph_diameter": 6,
            "avg_out_degree": 8.9,
            "max_out_degree": 100,
            "num_nodes": 20000,
            "num_channels": 50000,
            "total_network_capacity": 1000000000000,
            "avg_channel_size": 20000000,
            "min_channel_size": 20000,
            "max_channel_size": 100000000
        } 