import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from core.config import settings
from services.lnd_client import LNDClient
from services.mcp import MCPService
from services.lnrouter_client import LNRouterClient

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collecteur de métriques pour le nœud LN et le réseau"""
    
    def __init__(self, db_connection_string: str = None, lnd_client: LNDClient = None):
        """Initialise le collecteur de métriques
        
        Args:
            db_connection_string: Chaîne de connexion à la base de données
            lnd_client: Client LND à utiliser
        """
        self.db_connection_string = db_connection_string or settings.DATABASE_URL
        self.lnd_client = lnd_client or LNDClient()
        self.mcp_service = MCPService()
        self.lnrouter_client = LNRouterClient()
        self.db = self._init_database()
        
    def _init_database(self) -> Optional[Database]:
        """Initialise la connexion à la base de données"""
        if not self.db_connection_string:
            logger.warning("Chaîne de connexion à la base de données non configurée. Les métriques ne seront pas stockées.")
            return None
            
        try:
            client = MongoClient(self.db_connection_string)
            db = client.get_database()
            
            # Créer les collections si elles n'existent pas
            if "daily_snapshots" not in db.list_collection_names():
                db.create_collection("daily_snapshots")
                db["daily_snapshots"].create_index([("timestamp", 1)], unique=True)
                
            if "channel_metrics" not in db.list_collection_names():
                db.create_collection("channel_metrics")
                db["channel_metrics"].create_index([("timestamp", 1), ("channel_id", 1)], unique=True)
                
            if "forwarding_events" not in db.list_collection_names():
                db.create_collection("forwarding_events")
                db["forwarding_events"].create_index([("timestamp", 1), ("chan_id_in", 1), ("chan_id_out", 1)], unique=True)
                
            return db
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
            return None
    
    async def collect_node_metrics(self) -> Dict[str, Any]:
        """Collecte les métriques du nœud local
        
        Returns:
            Dictionnaire des métriques du nœud
        """
        try:
            # Récupérer les informations du nœud
            node_info = self.lnd_client.get_node_info()
            
            # Récupérer les informations de balance
            channels = self.lnd_client.list_channels()
            
            total_capacity = sum(c["capacity"] for c in channels)
            total_local_balance = sum(c["local_balance"] for c in channels)
            total_remote_balance = sum(c["remote_balance"] for c in channels)
            total_unsettled_balance = sum(c["unsettled_balance"] for c in channels)
            
            active_channels = [c for c in channels if c["active"]]
            inactive_channels = [c for c in channels if not c["active"]]
            
            # Calculer la répartition des fonds
            local_ratio = total_local_balance / total_capacity if total_capacity > 0 else 0
            
            # Compter les canaux par état
            channels_by_state = {
                "active": len(active_channels),
                "inactive": len(inactive_channels),
                "private": len([c for c in channels if c["private"]]),
                "public": len([c for c in channels if not c["private"]]),
                "initiated_by_us": len([c for c in channels if c["initiator"]]),
                "initiated_by_peer": len([c for c in channels if not c["initiator"]])
            }
            
            # Calcul des statistiques de base
            metrics = {
                "node_pubkey": node_info["pubkey"],
                "timestamp": datetime.now().isoformat(),
                "num_active_channels": node_info["num_active_channels"],
                "num_inactive_channels": node_info["num_inactive_channels"],
                "num_pending_channels": node_info["num_pending_channels"],
                "total_channels": len(channels),
                "channels_by_state": channels_by_state,
                "block_height": node_info["block_height"],
                "synced_to_chain": node_info["synced_to_chain"],
                "synced_to_graph": node_info["synced_to_graph"],
                "total_capacity": total_capacity,
                "total_local_balance": total_local_balance,
                "total_remote_balance": total_remote_balance,
                "total_unsettled_balance": total_unsettled_balance,
                "local_ratio": local_ratio,
                "version": node_info["version"]
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des métriques du nœud: {e}")
            # Retourner un dictionnaire minimal en cas d'erreur
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def collect_channel_metrics(self) -> List[Dict[str, Any]]:
        """Collecte les métriques de tous les canaux
        
        Returns:
            Liste des métriques des canaux
        """
        try:
            channels = self.lnd_client.list_channels()
            channel_metrics = []
            
            for channel in channels:
                # Calculer des métriques additionnelles
                capacity = channel["capacity"]
                local_balance = channel["local_balance"]
                remote_balance = channel["remote_balance"]
                
                local_ratio = local_balance / capacity if capacity > 0 else 0
                remote_ratio = remote_balance / capacity if capacity > 0 else 0
                balance_score = 1 - abs(0.5 - local_ratio) * 2  # Score plus élevé si équilibré
                
                # Récupérer les informations de politique
                channel_point = f"{channel['channel_point']['funding_txid_str']}:{channel['channel_point']['output_index']}" if "channel_point" in channel else "unknown"
                
                # Ajouter les métriques du canal
                channel_metrics.append({
                    "timestamp": datetime.now().isoformat(),
                    "channel_id": channel["channel_id"],
                    "remote_pubkey": channel["remote_pubkey"],
                    "capacity": capacity,
                    "local_balance": local_balance,
                    "remote_balance": remote_balance,
                    "unsettled_balance": channel["unsettled_balance"],
                    "local_ratio": local_ratio,
                    "remote_ratio": remote_ratio,
                    "balance_score": balance_score,
                    "active": channel["active"],
                    "private": channel["private"],
                    "initiator": channel["initiator"],
                    "total_satoshis_sent": channel["total_satoshis_sent"],
                    "total_satoshis_received": channel["total_satoshis_received"],
                    "num_updates": channel["num_updates"],
                    "commit_fee": channel["commit_fee"],
                    "commit_weight": channel["commit_weight"],
                    "fee_per_kw": channel["fee_per_kw"],
                    "chan_status_flags": channel["chan_status_flags"],
                    "local_chan_reserve_sat": channel["local_chan_reserve_sat"],
                    "remote_chan_reserve_sat": channel["remote_chan_reserve_sat"],
                    "channel_point": channel_point
                })
            
            return channel_metrics
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des métriques des canaux: {e}")
            return []
    
    async def collect_forwarding_metrics(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Collecte les métriques de routage sur une période donnée
        
        Args:
            time_window_hours: Nombre d'heures à considérer
            
        Returns:
            Métriques de routage agrégées
        """
        try:
            # Calculer la période
            end_time = int(datetime.now().timestamp())
            start_time = end_time - time_window_hours * 3600
            
            # Récupérer l'historique des forwards
            forwards = self.lnd_client.get_forwarding_history(start_time=start_time, end_time=end_time, limit=1000)
            
            forwarding_events = forwards.get("forwarding_events", [])
            
            # Stocker les événements si la base de données est configurée
            if self.db:
                collection = self.db["forwarding_events"]
                for event in forwarding_events:
                    try:
                        collection.update_one(
                            {"timestamp": event["timestamp"], "chan_id_in": event["chan_id_in"], "chan_id_out": event["chan_id_out"]},
                            {"$set": event},
                            upsert=True
                        )
                    except Exception as e:
                        logger.error(f"Erreur lors du stockage de l'événement de forwarding: {e}")
            
            # Agréger les données
            total_forwards = len(forwarding_events)
            total_amount_forwarded = sum(event["amt_out"] for event in forwarding_events)
            total_fees_earned = sum(event["fee"] for event in forwarding_events)
            
            # Agréger par canal
            channels_in = {}
            channels_out = {}
            
            for event in forwarding_events:
                chan_id_in = event["chan_id_in"]
                chan_id_out = event["chan_id_out"]
                amt_in = event["amt_in"]
                amt_out = event["amt_out"]
                fee = event["fee"]
                
                # Canal entrant
                if chan_id_in not in channels_in:
                    channels_in[chan_id_in] = {"count": 0, "amount": 0, "fees": 0}
                channels_in[chan_id_in]["count"] += 1
                channels_in[chan_id_in]["amount"] += amt_in
                channels_in[chan_id_in]["fees"] += fee
                
                # Canal sortant
                if chan_id_out not in channels_out:
                    channels_out[chan_id_out] = {"count": 0, "amount": 0}
                channels_out[chan_id_out]["count"] += 1
                channels_out[chan_id_out]["amount"] += amt_out
            
            # Calculer le taux moyen de frais
            avg_fee_rate = total_fees_earned / total_amount_forwarded * 1000000 if total_amount_forwarded > 0 else 0
            
            # Construire le rapport
            forwarding_metrics = {
                "timestamp": datetime.now().isoformat(),
                "time_window_hours": time_window_hours,
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "end_time": datetime.fromtimestamp(end_time).isoformat(),
                "total_forwards": total_forwards,
                "total_amount_forwarded": total_amount_forwarded,
                "total_fees_earned": total_fees_earned,
                "avg_fee_rate_ppm": avg_fee_rate,
                "channels_in": channels_in,
                "channels_out": channels_out,
                "forwards_per_hour": total_forwards / time_window_hours if time_window_hours > 0 else 0,
                "amount_per_hour": total_amount_forwarded / time_window_hours if time_window_hours > 0 else 0,
                "fees_per_hour": total_fees_earned / time_window_hours if time_window_hours > 0 else 0
            }
            
            return forwarding_metrics
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des métriques de forwarding: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "time_window_hours": time_window_hours,
                "error": str(e)
            }
    
    async def collect_network_context(self) -> Dict[str, Any]:
        """Collecte le contexte global du réseau Lightning
        
        Returns:
            Contexte du réseau
        """
        try:
            # Récupérer les informations MCP
            network_stats = await self.mcp_service.get_network_stats()
            
            # Récupérer les informations LNRouter
            lnrouter_stats = await self.lnrouter_client.get_network_stats()
            
            # Combiner les données
            network_context = {
                "timestamp": datetime.now().isoformat(),
                "mcp": {
                    "num_nodes": network_stats.get("num_nodes", 0),
                    "num_channels": network_stats.get("num_channels", 0),
                    "total_capacity": network_stats.get("total_capacity", 0),
                    "avg_node_capacity": network_stats.get("avg_node_capacity", 0),
                    "avg_channel_size": network_stats.get("avg_channel_size", 0),
                },
                "lnrouter": {
                    "num_nodes": lnrouter_stats.get("num_nodes", 0),
                    "num_channels": lnrouter_stats.get("num_channels", 0),
                    "total_capacity": lnrouter_stats.get("total_capacity", 0),
                    "avg_channel_size": lnrouter_stats.get("avg_channel_size", 0),
                    "avg_node_degree": lnrouter_stats.get("avg_node_degree", 0),
                }
            }
            
            return network_context
        except Exception as e:
            logger.error(f"Erreur lors de la collecte du contexte du réseau: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def create_daily_snapshot(self) -> str:
        """Crée un snapshot complet des métriques du jour
        
        Returns:
            ID du snapshot créé
        """
        try:
            # Collecter toutes les métriques
            node_metrics = await self.collect_node_metrics()
            channel_metrics = await self.collect_channel_metrics()
            forwarding_metrics = await self.collect_forwarding_metrics(time_window_hours=24)
            network_context = await self.collect_network_context()
            
            # Construire le snapshot
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "node_metrics": node_metrics,
                "channel_metrics": channel_metrics,
                "forwarding_metrics": forwarding_metrics,
                "network_context": network_context
            }
            
            # Stocker dans la base de données si configurée
            snapshot_id = None
            if self.db:
                collection = self.db["daily_snapshots"]
                result = collection.insert_one(snapshot)
                snapshot_id = str(result.inserted_id)
                logger.info(f"Snapshot quotidien créé avec ID: {snapshot_id}")
            
            # Sauvegarder dans un fichier JSON aussi
            snapshot_dir = "data/snapshots"
            os.makedirs(snapshot_dir, exist_ok=True)
            
            snapshot_file = os.path.join(snapshot_dir, f"snapshot_{datetime.now().strftime('%Y-%m-%d')}.json")
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot, f, indent=2)
            
            logger.info(f"Snapshot quotidien sauvegardé dans: {snapshot_file}")
            
            return snapshot_id or snapshot_file
        except Exception as e:
            logger.error(f"Erreur lors de la création du snapshot quotidien: {e}")
            return f"Erreur: {str(e)}"
    
    async def export_metrics_to_prometheus(self) -> bool:
        """Exporte les métriques au format Prometheus
        
        Returns:
            True si l'exportation a réussi
        """
        try:
            # Cette méthode nécessiterait une intégration avec Prometheus
            # Soit via l'exposition d'un endpoint HTTP, soit via l'écriture dans un fichier
            # Pour le moment, elle est juste un placeholder
            logger.info("Export Prometheus non implémenté")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'export Prometheus: {e}")
            return False
    
    async def generate_historical_trends(self, metric_name: str, days: int = 30) -> List[Dict]:
        """Génère des données de tendance pour une métrique spécifique
        
        Args:
            metric_name: Nom de la métrique à analyser
            days: Nombre de jours d'historique à considérer
            
        Returns:
            Liste de points de données pour la tendance
        """
        if not self.db:
            logger.warning("Base de données non configurée, impossible de générer des tendances historiques")
            return []
            
        try:
            # Calculer la période
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Mapper les noms de métriques aux chemins dans le document
            metric_paths = {
                "total_capacity": "node_metrics.total_capacity",
                "num_active_channels": "node_metrics.num_active_channels",
                "local_balance": "node_metrics.total_local_balance",
                "remote_balance": "node_metrics.total_remote_balance",
                "total_forwards": "forwarding_metrics.total_forwards",
                "total_fees": "forwarding_metrics.total_fees_earned",
                "avg_fee_rate": "forwarding_metrics.avg_fee_rate_ppm"
            }
            
            if metric_name not in metric_paths:
                logger.error(f"Métrique inconnue: {metric_name}")
                return []
                
            metric_path = metric_paths[metric_name]
            
            # Agréger par jour
            collection = self.db["daily_snapshots"]
            pipeline = [
                {
                    "$match": {
                        "timestamp": {
                            "$gte": start_date.isoformat(),
                            "$lte": end_date.isoformat()
                        }
                    }
                },
                {
                    "$project": {
                        "date": {"$substr": ["$timestamp", 0, 10]},
                        "value": f"${metric_path}"
                    }
                },
                {
                    "$group": {
                        "_id": "$date",
                        "value": {"$avg": "$value"}
                    }
                },
                {
                    "$sort": {"_id": 1}
                }
            ]
            
            results = list(collection.aggregate(pipeline))
            
            # Formater les résultats
            trend_data = [{"date": item["_id"], "value": item["value"]} for item in results]
            
            return trend_data
        except Exception as e:
            logger.error(f"Erreur lors de la génération des tendances historiques: {e}")
            return []
    
    async def run_periodic_collection(self, interval_hours: int = None):
        """Exécute la collecte périodique des métriques
        
        Args:
            interval_hours: Intervalle en heures entre les collectes
        """
        interval = interval_hours or settings.METRICS_COLLECTION_INTERVAL_HOURS or 24
        
        while True:
            try:
                logger.info(f"Démarrage de la collecte périodique des métriques (intervalle: {interval}h)")
                await self.create_daily_snapshot()
                logger.info(f"Collecte terminée, prochaine exécution dans {interval} heures")
                
                # Attendre l'intervalle spécifié
                await asyncio.sleep(interval * 3600)
            except Exception as e:
                logger.error(f"Erreur lors de la collecte périodique: {e}")
                # Attendre 10 minutes avant de réessayer en cas d'erreur
                await asyncio.sleep(600) 