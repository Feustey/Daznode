import os
import json
import csv
import logging
import httpx
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path

from core.config import settings
from services.metrics_collector import MetricsCollector
from services.node_aggregator import NodeAggregator, EnrichedNode, EnrichedChannel
from services.data_source_factory import DataSourceFactory

logger = logging.getLogger(__name__)

class VisualizationExporter:
    """Exportateur de datasets pour visualisations et dashboards"""
    
    def __init__(self, metrics_collector: MetricsCollector = None, 
                 node_aggregator: NodeAggregator = None):
        """Initialise l'exportateur de visualisations
        
        Args:
            metrics_collector: Collecteur de métriques à utiliser
            node_aggregator: Agrégateur de nœuds à utiliser
        """
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.node_aggregator = node_aggregator or NodeAggregator()
        self.export_dir = Path("data/visualizations")
        self.export_dir.mkdir(exist_ok=True, parents=True)
        
        # Définir les stratégies d'export
        self._export_strategies = {
            "csv": self._export_to_csv,
            "json": self._export_to_json,
            "parquet": self._export_to_parquet,
            "api": self._export_to_api
        }
        
        # Garder une trace des datasets générés
        self._datasets = {}
        
        self.data_source = DataSourceFactory.get_data_source()
    
    # MÉTHODES DE GÉNÉRATION DE DATASETS
    
    async def generate_network_graph_dataset(self) -> Dict[str, Any]:
        """Génère les données pour un graphe du réseau local"""
        try:
            # Récupérer les informations du nœud local
            node_info = self.node_aggregator.lnd_client.get_node_info()
            pubkey = node_info.get("pubkey")
            
            # Récupérer tous les canaux du nœud local
            channels = await self.data_source.get_node_channels(pubkey)
            
            # Récupérer des détails sur les nœuds connectés
            peers = set()
            for channel in channels:
                remote_pubkey = channel.get("node2_pub")
                if remote_pubkey != pubkey:
                    peers.add(remote_pubkey)
            
            # Récupérer des détails sur chaque pair
            nodes = []
            edges = []
            
            # Ajouter le nœud local
            nodes.append({
                "id": pubkey,
                "alias": node_info.get("alias", ""),
                "color": node_info.get("color", "#000000"),
                "size": 15,  # Taille plus grande pour le nœud local
                "group": "local"
            })
            
            # Récupérer les données de chaque pair et ajouter aux graphes
            for peer_pubkey in peers:
                try:
                    peer_data = await self.node_aggregator.get_enriched_node(peer_pubkey)
                    
                    if peer_data:
                        # Ajouter le nœud
                        nodes.append({
                            "id": peer_pubkey,
                            "alias": peer_data.get("alias", peer_pubkey[:10] + "..."),
                            "color": peer_data.get("color", "#cccccc"),
                            "size": 10,
                            "group": "peer"
                        })
                        
                        # Trouver le canal entre nous et ce pair
                        for channel in channels:
                            if channel.get("node2_pub") == peer_pubkey:
                                # Ajouter une arête
                                edges.append({
                                    "id": str(channel.get("channel_id", "")),
                                    "source": pubkey,
                                    "target": peer_pubkey,
                                    "capacity": channel.get("capacity", 0),
                                    "active": channel.get("active", True),
                                    "value": 1 + channel.get("capacity", 0) / 1000000  # Épaisseur proportionnelle à la capacité
                                })
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération des détails du pair {peer_pubkey}: {e}")
            
            return {
                "timestamp": datetime.now().isoformat(),
                "nodes": nodes,
                "edges": edges,
                "source": "mixed"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du dataset pour le graphe réseau: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "nodes": [],
                "edges": []
            }
    
    async def generate_channel_performance_dataset(self, days: int = 30) -> Dict[str, Any]:
        """Génère les données pour analyser la performance des canaux
        
        Args:
            days: Nombre de jours d'historique à inclure
        """
        try:
            # Vérifier que le collecteur de métriques est disponible
            if not self.metrics_collector:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "error": "Collecteur de métriques non disponible",
                    "channels": []
                }
            
            # Récupérer les métriques des canaux
            channels = await self.metrics_collector.collect_channel_metrics()
            
            # Si disponible, récupérer l'historique des métriques
            historical_metrics = []
            try:
                # Récupérer les tendances historiques
                historical_metrics = await self.metrics_collector.generate_historical_trends("channel_balance", days=days)
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des tendances historiques: {e}")
            
            # Agréger les données par canal
            channel_performance = []
            
            for channel in channels:
                channel_id = channel.get("channel_id")
                
                # Chercher ce canal dans l'historique
                historical_data = []
                for entry in historical_metrics:
                    for ch in entry.get("channels", []):
                        if ch.get("channel_id") == channel_id:
                            historical_data.append({
                                "timestamp": entry.get("timestamp"),
                                "local_balance": ch.get("local_balance", 0),
                                "remote_balance": ch.get("remote_balance", 0),
                                "local_ratio": ch.get("local_ratio", 0)
                            })
                
                # Inclure les détails du pair
                peer_alias = "Inconnu"
                peer_pubkey = channel.get("remote_pubkey")
                
                try:
                    peer = await self.node_aggregator.get_enriched_node(peer_pubkey)
                    if peer:
                        peer_alias = peer.get("alias", "Inconnu")
                except Exception:
                    pass
                
                channel_performance.append({
                    "channel_id": channel_id,
                    "peer_pubkey": peer_pubkey,
                    "peer_alias": peer_alias,
                    "capacity": channel.get("capacity", 0),
                    "local_balance": channel.get("local_balance", 0),
                    "remote_balance": channel.get("remote_balance", 0),
                    "active": channel.get("active", False),
                    "local_ratio": channel.get("local_ratio", 0),
                    "balance_score": channel.get("balance_score", 0),
                    "total_satoshis_sent": channel.get("total_satoshis_sent", 0),
                    "total_satoshis_received": channel.get("total_satoshis_received", 0),
                    "history": historical_data
                })
            
            return {
                "timestamp": datetime.now().isoformat(),
                "channels": channel_performance,
                "days_history": days,
                "source": "local"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du dataset de performance des canaux: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "channels": []
            }
    
    async def generate_routing_heatmap_dataset(self, time_resolution: str = "hour") -> Dict[str, Any]:
        """Génère les données pour une heatmap de routage
        
        Args:
            time_resolution: Résolution temporelle ('hour', 'day', 'week')
        """
        try:
            # Vérifier la validité de la résolution
            valid_resolutions = ["hour", "day", "week"]
            if time_resolution not in valid_resolutions:
                time_resolution = "hour"
            
            # Déterminer la période et l'intervalle
            now = datetime.now()
            
            if time_resolution == "hour":
                start_time = now - timedelta(days=2)
                interval_seconds = 3600  # 1 heure
            elif time_resolution == "day":
                start_time = now - timedelta(days=30)
                interval_seconds = 86400  # 1 jour
            else:  # semaine
                start_time = now - timedelta(days=365)
                interval_seconds = 604800  # 1 semaine
            
            # Récupérer l'historique de forwarding
            forwarding_history = self.node_aggregator.lnd_client.get_forwarding_history(
                start_time=int(start_time.timestamp()),
                end_time=int(now.timestamp()),
                limit=10000
            )
            
            # Organiser les données pour la heatmap
            events = forwarding_history.get("forwarding_events", [])
            
            # Grouper par intervalle de temps
            time_buckets = {}
            
            for event in events:
                timestamp = event.get("timestamp", 0)
                if not timestamp:
                    continue
                    
                # Calculer l'intervalle de temps
                bucket_timestamp = timestamp - (timestamp % interval_seconds)
                bucket_key = str(bucket_timestamp)
                
                # Initialiser le bucket si nécessaire
                if bucket_key not in time_buckets:
                    time_buckets[bucket_key] = {
                        "timestamp": bucket_key,
                        "count": 0,
                        "total_amount": 0,
                        "total_fees": 0
                    }
                
                # Mettre à jour les statistiques
                time_buckets[bucket_key]["count"] += 1
                time_buckets[bucket_key]["total_amount"] += event.get("amt_out", 0)
                time_buckets[bucket_key]["total_fees"] += event.get("fee", 0)
            
            # Convertir en liste pour la sortie
            heatmap_data = list(time_buckets.values())
            
            # Trier par timestamp
            heatmap_data.sort(key=lambda x: int(x["timestamp"]))
            
            return {
                "timestamp": datetime.now().isoformat(),
                "data": heatmap_data,
                "resolution": time_resolution,
                "source": "local"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du dataset pour la heatmap: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "data": []
            }
    
    async def generate_fee_optimization_dataset(self) -> Dict[str, Any]:
        """Génère des suggestions d'optimisation de frais"""
        try:
            # Récupérer les métriques détaillées des canaux
            if self.metrics_collector:
                channels = await self.metrics_collector.collect_channel_metrics()
            else:
                # Si metrics_collector n'est pas disponible, récupérer les canaux depuis le client LND
                channels_raw = self.node_aggregator.lnd_client.list_channels()
                channels = []
                
                for c in channels_raw:
                    capacity = c.get("capacity", 0)
                    local_balance = c.get("local_balance", 0)
                    remote_balance = c.get("remote_balance", 0)
                    
                    local_ratio = local_balance / capacity if capacity > 0 else 0
                    remote_ratio = remote_balance / capacity if capacity > 0 else 0
                    balance_score = 1 - abs(0.5 - local_ratio) * 2
                    
                    channels.append({
                        "channel_id": c.get("channel_id"),
                        "remote_pubkey": c.get("remote_pubkey"),
                        "capacity": capacity,
                        "local_balance": local_balance,
                        "remote_balance": remote_balance,
                        "local_ratio": local_ratio,
                        "remote_ratio": remote_ratio,
                        "balance_score": balance_score,
                        "active": c.get("active", False),
                        "fee_per_kw": c.get("fee_per_kw", 0)
                    })
            
            # Récupérer les statistiques de forwarding pour identifier les canaux actifs
            end_time = int(datetime.now().timestamp())
            start_time = end_time - 30 * 24 * 3600  # 30 jours
            
            forwards = self.node_aggregator.lnd_client.get_forwarding_history(
                start_time=start_time,
                end_time=end_time,
                limit=10000
            )
            
            # Compter les forwards par canal
            channel_forwards = {}
            for event in forwards.get("forwarding_events", []):
                chan_id_in = str(event.get("chan_id_in"))
                chan_id_out = str(event.get("chan_id_out"))
                
                if chan_id_in not in channel_forwards:
                    channel_forwards[chan_id_in] = {"in": 0, "out": 0, "fees": 0}
                if chan_id_out not in channel_forwards:
                    channel_forwards[chan_id_out] = {"in": 0, "out": 0, "fees": 0}
                
                channel_forwards[chan_id_in]["in"] += 1
                channel_forwards[chan_id_in]["fees"] += event.get("fee", 0)
                channel_forwards[chan_id_out]["out"] += 1
            
            # Générer des suggestions d'optimisation
            suggestions = []
            
            for channel in channels:
                channel_id = str(channel.get("channel_id"))
                remote_pubkey = channel.get("remote_pubkey")
                
                # Récupérer les détails du pair
                peer_alias = "Inconnu"
                try:
                    peer = await self.node_aggregator.get_enriched_node(remote_pubkey)
                    if peer:
                        peer_alias = peer.get("alias", "Inconnu")
                except Exception:
                    pass
                
                # Analyser le canal pour des suggestions
                current_fee = channel.get("fee_per_kw", 0)
                balance_score = channel.get("balance_score", 0)
                local_ratio = channel.get("local_ratio", 0)
                
                # Statistiques de forwarding
                forwards_stats = channel_forwards.get(channel_id, {"in": 0, "out": 0, "fees": 0})
                
                # Générer des suggestions basées sur différents critères
                suggestion = {
                    "channel_id": channel_id,
                    "peer_pubkey": remote_pubkey,
                    "peer_alias": peer_alias,
                    "current_fee": current_fee,
                    "balance_score": balance_score,
                    "local_ratio": local_ratio,
                    "forwarding_in": forwards_stats.get("in", 0),
                    "forwarding_out": forwards_stats.get("out", 0),
                    "fees_earned": forwards_stats.get("fees", 0),
                    "recommendations": []
                }
                
                # 1. Canal inactif en forwarding
                if forwards_stats.get("in", 0) == 0 and forwards_stats.get("out", 0) == 0:
                    suggestion["recommendations"].append({
                        "type": "inactive",
                        "message": "Canal inactif, envisager d'ajuster les frais pour attirer du trafic",
                        "suggested_fee": max(1, current_fee // 2),
                        "confidence": "medium"
                    })
                
                # 2. Canal déséquilibré avec trafic entrant
                if local_ratio > 0.7 and forwards_stats.get("in", 0) > 0:
                    suggestion["recommendations"].append({
                        "type": "balance_in",
                        "message": "Canal déséquilibré avec trafic entrant, augmenter les frais",
                        "suggested_fee": current_fee * 2,
                        "confidence": "high"
                    })
                
                # 3. Canal déséquilibré avec trafic sortant
                if local_ratio < 0.3 and forwards_stats.get("out", 0) > 0:
                    suggestion["recommendations"].append({
                        "type": "balance_out",
                        "message": "Canal déséquilibré avec trafic sortant, réduire les frais",
                        "suggested_fee": max(1, current_fee // 2),
                        "confidence": "high"
                    })
                
                # 4. Canal bien équilibré mais peu actif
                if balance_score > 0.7 and forwards_stats.get("in", 0) + forwards_stats.get("out", 0) < 10:
                    suggestion["recommendations"].append({
                        "type": "balanced_inactive",
                        "message": "Canal bien équilibré mais peu actif, réduire légèrement les frais",
                        "suggested_fee": max(1, int(current_fee * 0.8)),
                        "confidence": "medium"
                    })
                
                suggestions.append(suggestion)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "suggestions": suggestions,
                "source": "local"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des suggestions d'optimisation: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "suggestions": []
            }
    
    async def generate_periodic_report(self, report_type: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Génère un rapport périodique
        
        Args:
            report_type: Type de rapport ('daily', 'weekly', 'monthly')
            parameters: Paramètres spécifiques au rapport
        """
        parameters = parameters or {}
        
        try:
            # Déterminer la période
            now = datetime.now()
            
            if report_type == "daily":
                start_time = now - timedelta(days=1)
                period_name = "Quotidien"
            elif report_type == "weekly":
                start_time = now - timedelta(days=7)
                period_name = "Hebdomadaire"
            elif report_type == "monthly":
                start_time = now - timedelta(days=30)
                period_name = "Mensuel"
            else:
                return {
                    "error": f"Type de rapport non reconnu: {report_type}"
                }
            
            # Structure du rapport
            report = {
                "report_type": report_type,
                "period_name": period_name,
                "timestamp": now.isoformat(),
                "start_time": start_time.isoformat(),
                "end_time": now.isoformat(),
                "node_metrics": {},
                "channels_metrics": {},
                "routing_metrics": {},
                "recommendations": [],
                "source": "local"
            }
            
            # 1. Récupérer les métriques du nœud
            if self.metrics_collector:
                node_metrics = await self.metrics_collector.collect_node_metrics()
                report["node_metrics"] = node_metrics
            
            # 2. Récupérer les métriques des canaux
            if self.metrics_collector:
                channels_metrics = await self.metrics_collector.collect_channel_metrics()
                
                # Agréger les métriques des canaux
                total_capacity = sum(c.get("capacity", 0) for c in channels_metrics)
                total_local_balance = sum(c.get("local_balance", 0) for c in channels_metrics)
                active_channels = [c for c in channels_metrics if c.get("active", False)]
                
                report["channels_metrics"] = {
                    "total_channels": len(channels_metrics),
                    "active_channels": len(active_channels),
                    "total_capacity": total_capacity,
                    "local_balance": total_local_balance,
                    "local_ratio": total_local_balance / total_capacity if total_capacity > 0 else 0,
                    "channels": channels_metrics
                }
            
            # 3. Récupérer les métriques de routage
            start_time_unix = int(start_time.timestamp())
            end_time_unix = int(now.timestamp())
            
            forwarding_history = self.node_aggregator.lnd_client.get_forwarding_history(
                start_time=start_time_unix,
                end_time=end_time_unix,
                limit=10000
            )
            
            events = forwarding_history.get("forwarding_events", [])
            
            # Agréger les statistiques de routage
            total_forwards = len(events)
            total_amount = sum(event.get("amt_out", 0) for event in events)
            total_fees = sum(event.get("fee", 0) for event in events)
            
            # Identifier les canaux les plus actifs
            channel_stats = {}
            for event in events:
                chan_id_in = str(event.get("chan_id_in"))
                chan_id_out = str(event.get("chan_id_out"))
                
                for chan_id in [chan_id_in, chan_id_out]:
                    if chan_id not in channel_stats:
                        channel_stats[chan_id] = {
                            "count": 0,
                            "amount": 0,
                            "fees": 0
                        }
                
                channel_stats[chan_id_in]["count"] += 1
                channel_stats[chan_id_in]["amount"] += event.get("amt_in", 0)
                channel_stats[chan_id_in]["fees"] += event.get("fee", 0)
                
                channel_stats[chan_id_out]["count"] += 1
                channel_stats[chan_id_out]["amount"] += event.get("amt_out", 0)
            
            # Trier les canaux par nombre de forwards
            top_channels = []
            for chan_id, stats in channel_stats.items():
                for channel in report["channels_metrics"].get("channels", []):
                    if str(channel.get("channel_id")) == chan_id:
                        top_channels.append({
                            "channel_id": chan_id,
                            "remote_pubkey": channel.get("remote_pubkey"),
                            "count": stats["count"],
                            "amount": stats["amount"],
                            "fees": stats["fees"]
                        })
                        break
            
            # Trier et limiter
            top_channels.sort(key=lambda x: x["count"], reverse=True)
            top_channels = top_channels[:10]
            
            report["routing_metrics"] = {
                "total_forwards": total_forwards,
                "total_amount": total_amount,
                "total_fees": total_fees,
                "avg_fee_rate": total_fees / total_amount * 1000000 if total_amount > 0 else 0,
                "top_channels": top_channels
            }
            
            # 4. Générer des recommandations
            fee_optimization = await self.generate_fee_optimization_dataset()
            suggestions = fee_optimization.get("suggestions", [])
            
            # Ne garder que les recommandations avec au moins une suggestion
            suggestions_with_recs = [s for s in suggestions if s.get("recommendations")]
            
            # Trier par nombre de recommendations et limiter
            suggestions_with_recs.sort(key=lambda x: len(x.get("recommendations", [])), reverse=True)
            report["recommendations"] = suggestions_with_recs[:5]
            
            return report
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport {report_type}: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "report_type": report_type
            }
    
    # MÉTHODES D'EXPORT
    
    def export_to_csv(self, dataset_name: str, file_path: str = None) -> bool:
        """Exporte un dataset au format CSV
        
        Args:
            dataset_name: Nom du dataset à exporter
            file_path: Chemin du fichier de sortie (optionnel)
            
        Returns:
            True si l'exportation a réussi
        """
        return self._export_dataset(dataset_name, "csv", file_path)
    
    def export_to_json(self, dataset_name: str, file_path: str = None) -> bool:
        """Exporte un dataset au format JSON
        
        Args:
            dataset_name: Nom du dataset à exporter
            file_path: Chemin du fichier de sortie (optionnel)
            
        Returns:
            True si l'exportation a réussi
        """
        return self._export_dataset(dataset_name, "json", file_path)
    
    def export_to_parquet(self, dataset_name: str, file_path: str = None) -> bool:
        """Exporte un dataset au format Parquet
        
        Args:
            dataset_name: Nom du dataset à exporter
            file_path: Chemin du fichier de sortie (optionnel)
            
        Returns:
            True si l'exportation a réussi
        """
        return self._export_dataset(dataset_name, "parquet", file_path)
    
    async def export_to_dashboard_api(self, dataset_name: str, api_endpoint: str) -> bool:
        """Pousse un dataset vers une API de dashboard
        
        Args:
            dataset_name: Nom du dataset à exporter
            api_endpoint: URL de l'API
            
        Returns:
            True si l'exportation a réussi
        """
        return await self._export_dataset(dataset_name, "api", api_endpoint)
    
    def _export_dataset(self, dataset_name: str, format_type: str, target: str = None) -> bool:
        """Exporte un dataset dans le format spécifié
        
        Args:
            dataset_name: Nom du dataset à exporter
            format_type: Format d'export ('csv', 'json', 'parquet', 'api')
            target: Cible de l'export (fichier ou endpoint API)
            
        Returns:
            True si l'exportation a réussi
        """
        if dataset_name not in self._datasets:
            logger.error(f"Dataset non trouvé: {dataset_name}")
            return False
            
        if format_type not in self._export_strategies:
            logger.error(f"Format d'export non supporté: {format_type}")
            return False
            
        dataset = self._datasets[dataset_name]
        
        # Utiliser la stratégie d'export appropriée
        export_function = self._export_strategies[format_type]
        return export_function(dataset, dataset_name, target)
    
    def _export_to_csv(self, dataset: Dict, dataset_name: str, file_path: str = None) -> bool:
        """Exporte un dataset au format CSV
        
        Args:
            dataset: Données à exporter
            dataset_name: Nom du dataset
            file_path: Chemin du fichier de sortie (optionnel)
            
        Returns:
            True si l'exportation a réussi
        """
        try:
            # Déterminer le fichier de sortie
            if not file_path:
                file_path = self.export_dir / f"{dataset_name}_{datetime.now().strftime('%Y%m%d')}.csv"
            
            # Identifier la partie à exporter en CSV (généralement, une liste de dictionnaires)
            if "channels" in dataset and isinstance(dataset["channels"], list):
                export_data = dataset["channels"]
            elif "heatmap_data" in dataset and isinstance(dataset["heatmap_data"], list):
                export_data = dataset["heatmap_data"]
            elif "nodes" in dataset and isinstance(dataset["nodes"], list):
                export_data = dataset["nodes"]
            else:
                # Si on ne trouve pas de données structurées, aplatir le dictionnaire
                export_data = self._flatten_dict(dataset)
            
            # Écrire le fichier CSV
            with open(file_path, 'w', newline='') as csvfile:
                if export_data:
                    fieldnames = export_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for row in export_data:
                        writer.writerow(row)
            
            logger.info(f"Dataset {dataset_name} exporté au format CSV: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'export CSV: {e}")
            return False
    
    def _export_to_json(self, dataset: Dict, dataset_name: str, file_path: str = None) -> bool:
        """Exporte un dataset au format JSON
        
        Args:
            dataset: Données à exporter
            dataset_name: Nom du dataset
            file_path: Chemin du fichier de sortie (optionnel)
            
        Returns:
            True si l'exportation a réussi
        """
        try:
            # Déterminer le fichier de sortie
            if not file_path:
                file_path = self.export_dir / f"{dataset_name}_{datetime.now().strftime('%Y%m%d')}.json"
            
            # Écrire le fichier JSON
            with open(file_path, 'w') as jsonfile:
                json.dump(dataset, jsonfile, indent=2)
            
            logger.info(f"Dataset {dataset_name} exporté au format JSON: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'export JSON: {e}")
            return False
    
    def _export_to_parquet(self, dataset: Dict, dataset_name: str, file_path: str = None) -> bool:
        """Exporte un dataset au format Parquet
        
        Args:
            dataset: Données à exporter
            dataset_name: Nom du dataset
            file_path: Chemin du fichier de sortie (optionnel)
            
        Returns:
            True si l'exportation a réussi
        """
        try:
            # Déterminer le fichier de sortie
            if not file_path:
                file_path = self.export_dir / f"{dataset_name}_{datetime.now().strftime('%Y%m%d')}.parquet"
            
            # Identifier la partie à exporter en Parquet (généralement, une liste de dictionnaires)
            if "channels" in dataset and isinstance(dataset["channels"], list):
                export_data = pd.DataFrame(dataset["channels"])
            elif "heatmap_data" in dataset and isinstance(dataset["heatmap_data"], list):
                export_data = pd.DataFrame(dataset["heatmap_data"])
            elif "nodes" in dataset and isinstance(dataset["nodes"], list):
                export_data = pd.DataFrame(dataset["nodes"])
            else:
                # Si on ne trouve pas de données structurées, aplatir le dictionnaire
                export_data = pd.DataFrame([self._flatten_dict(dataset)])
            
            # Écrire le fichier Parquet
            export_data.to_parquet(file_path, index=False)
            
            logger.info(f"Dataset {dataset_name} exporté au format Parquet: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'export Parquet: {e}")
            return False
    
    async def _export_to_api(self, dataset: Dict, dataset_name: str, api_endpoint: str = None) -> bool:
        """Pousse un dataset vers une API
        
        Args:
            dataset: Données à exporter
            dataset_name: Nom du dataset
            api_endpoint: URL de l'API (requis)
            
        Returns:
            True si l'exportation a réussi
        """
        if not api_endpoint:
            logger.error("Endpoint API requis pour l'export")
            return False
            
        try:
            # Envoyer les données à l'API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    api_endpoint,
                    json=dataset,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                
                response.raise_for_status()
                
                logger.info(f"Dataset {dataset_name} exporté vers l'API: {api_endpoint}")
                return True
        except Exception as e:
            logger.error(f"Erreur lors de l'export API: {e}")
            return False
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Aplatit un dictionnaire imbriqué
        
        Args:
            d: Dictionnaire à aplatir
            parent_key: Préfixe pour les clés (utilisé dans la récursion)
            sep: Séparateur entre les clés parentes et les sous-clés
            
        Returns:
            Dictionnaire aplati
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list) and all(isinstance(x, dict) for x in v):
                # Pour les listes de dictionnaires, ignorer pour l'aplatissement
                pass
            else:
                items.append((new_key, v))
        return dict(items) 