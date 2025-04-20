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
    
    # MÉTHODES DE GÉNÉRATION DE DATASETS
    
    async def generate_network_graph_dataset(self) -> Dict:
        """Génère un dataset pour visualisation de graphe réseau
        
        Returns:
            Dataset au format adaptée pour les visualisations de graphe
        """
        try:
            # Récupérer le nœud local enrichi
            local_node = await self.node_aggregator.get_enriched_node(settings.NODE_PUBKEY)
            
            # Récupérer tous les nœuds connectés
            peer_pubkeys = [channel.node2_pub for channel in local_node.channels.values()]
            
            # Nœuds du graphe
            nodes = [{
                "id": local_node.pubkey,
                "label": local_node.alias or local_node.pubkey[:8],
                "color": local_node.color or "#3498db",
                "size": 15,  # Plus grand pour le nœud local
                "isLocal": True,
                "totalCapacity": local_node.total_capacity
            }]
            
            # Arêtes du graphe (canaux)
            edges = []
            
            # Ajouter les nœuds pairs et les canaux
            for channel in local_node.channels.values():
                peer_pubkey = channel.node2_pub
                
                # Récupérer les informations du pair (de façon asynce idéalement)
                try:
                    peer_node = await self.node_aggregator.get_enriched_node(peer_pubkey)
                    peer_alias = peer_node.alias
                    peer_color = peer_node.color
                except Exception:
                    peer_alias = peer_pubkey[:8]
                    peer_color = "#7f8c8d"  # Gris par défaut
                
                # Ajouter le nœud pair s'il n'est pas déjà dans le graphe
                if not any(node["id"] == peer_pubkey for node in nodes):
                    nodes.append({
                        "id": peer_pubkey,
                        "label": peer_alias or peer_pubkey[:8],
                        "color": peer_color or "#7f8c8d",
                        "size": 10,
                        "isLocal": False,
                        "capacityWithLocal": channel.capacity
                    })
                
                # Ajouter le canal comme arête
                edge_id = f"{local_node.pubkey}-{peer_pubkey}"
                
                # Calculer la largeur de l'arête basée sur la capacité
                capacity_normalized = np.log1p(channel.capacity / 1000000) * 2  # log1p pour éviter log(0)
                width = max(1, min(10, capacity_normalized))  # Limiter entre 1 et 10
                
                # Déterminer la couleur en fonction de l'équilibre
                if channel.local_ratio > 0.7:
                    color = "#e74c3c"  # Rouge pour déséquilibré sortant
                elif channel.local_ratio < 0.3:
                    color = "#2ecc71"  # Vert pour déséquilibré entrant 
                else:
                    color = "#3498db"  # Bleu pour équilibré
                
                edges.append({
                    "id": edge_id,
                    "source": local_node.pubkey,
                    "target": peer_pubkey,
                    "label": f"{channel.capacity:,} sats",
                    "size": width,
                    "color": color,
                    "active": channel.active,
                    "localRatio": channel.local_ratio,
                    "capacity": channel.capacity,
                    "stuckIndex": channel.stuck_index,
                    "profitable": channel.is_profitable
                })
            
            # Compiler le dataset
            dataset = {
                "timestamp": datetime.now().isoformat(),
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "totalNodes": len(nodes),
                    "totalEdges": len(edges),
                    "totalCapacity": local_node.total_capacity
                }
            }
            
            # Stocker le dataset
            self._datasets["network_graph"] = dataset
            
            return dataset
        except Exception as e:
            logger.error(f"Erreur lors de la génération du dataset de graphe réseau: {e}")
            return {"error": str(e)}
    
    async def generate_channel_performance_dataset(self, days: int = 30) -> Dict:
        """Génère un dataset pour tableau de bord de performance des canaux
        
        Args:
            days: Nombre de jours d'historique à considérer
            
        Returns:
            Dataset avec les performances des canaux
        """
        try:
            # Récupérer le nœud local enrichi
            local_node = await self.node_aggregator.get_enriched_node(settings.NODE_PUBKEY)
            
            # Préparer les données de canaux
            channels_data = []
            
            for channel in local_node.channels.values():
                # Calculer des métriques de performance
                forwarding_stats = channel.forwarding_stats
                rebalancing_stats = channel.rebalancing_stats
                profitability = channel.profitability
                
                # Calculer des métriques dérivées
                total_volume = forwarding_stats.get("total_amount_forwards", 0)
                total_fees = forwarding_stats.get("total_fees", 0)
                
                effective_fee_rate = (total_fees / total_volume * 1000000) if total_volume > 0 else 0
                volume_per_capacity = total_volume / channel.capacity if channel.capacity > 0 else 0
                
                # Estimer le potentiel de routage basé sur les forwarding passés et l'équilibre
                routing_potential = 0
                if channel.active:
                    # Un canal bien équilibré a plus de potentiel
                    balance_factor = 1 - abs(channel.local_ratio - 0.5) * 2
                    # Canal avec historique de routage a plus de potentiel
                    historical_factor = min(1, total_volume / (channel.capacity * 2))
                    routing_potential = balance_factor * 0.7 + historical_factor * 0.3
                
                # Ajouter les données du canal
                channels_data.append({
                    "channel_id": channel.channel_id,
                    "peer_pubkey": channel.node2_pub,
                    "peer_alias": None,  # À enrichir
                    "capacity": channel.capacity,
                    "local_balance": channel.local_balance,
                    "remote_balance": channel.remote_balance,
                    "local_ratio": channel.local_ratio,
                    "active": channel.active,
                    "private": channel.private,
                    "initiator": channel.initiator,
                    "age_days": None,  # À calculer si les données sont disponibles
                    "forwards_count": forwarding_stats.get("total_forwards", 0),
                    "forwards_volume": total_volume,
                    "fees_earned": total_fees,
                    "effective_fee_rate": effective_fee_rate,
                    "volume_per_capacity": volume_per_capacity,
                    "routing_potential": routing_potential,
                    "stuck_index": channel.stuck_index,
                    "last_forward_time": forwarding_stats.get("last_forward_time"),
                    "net_profit": profitability.get("net_profit", 0),
                    "roi": profitability.get("roi", 0),
                    "profitable": channel.is_profitable
                })
            
            # Trier les canaux par différents critères pour faciliter l'analyse
            sorted_by_profit = sorted(channels_data, key=lambda x: x["net_profit"], reverse=True)
            sorted_by_volume = sorted(channels_data, key=lambda x: x["forwards_volume"], reverse=True)
            sorted_by_stuck = sorted(channels_data, key=lambda x: x["stuck_index"], reverse=True)
            sorted_by_potential = sorted(channels_data, key=lambda x: x["routing_potential"], reverse=True)
            
            # Compiler le dataset
            dataset = {
                "timestamp": datetime.now().isoformat(),
                "days_considered": days,
                "channels": channels_data,
                "sorted_views": {
                    "by_profit": [c["channel_id"] for c in sorted_by_profit],
                    "by_volume": [c["channel_id"] for c in sorted_by_volume],
                    "by_stuck": [c["channel_id"] for c in sorted_by_stuck],
                    "by_potential": [c["channel_id"] for c in sorted_by_potential]
                },
                "summary": {
                    "total_channels": len(channels_data),
                    "active_channels": sum(1 for c in channels_data if c["active"]),
                    "profitable_channels": sum(1 for c in channels_data if c["profitable"]),
                    "stuck_channels": sum(1 for c in channels_data if c["stuck_index"] > 70),
                    "total_capacity": sum(c["capacity"] for c in channels_data),
                    "total_local_balance": sum(c["local_balance"] for c in channels_data),
                    "total_volume": sum(c["forwards_volume"] for c in channels_data),
                    "total_fees": sum(c["fees_earned"] for c in channels_data)
                }
            }
            
            # Stocker le dataset
            self._datasets["channel_performance"] = dataset
            
            return dataset
        except Exception as e:
            logger.error(f"Erreur lors de la génération du dataset de performance des canaux: {e}")
            return {"error": str(e)}
    
    async def generate_routing_heatmap_dataset(self, time_resolution: str = "hour") -> Dict:
        """Génère un dataset pour carte de chaleur des activités de routage
        
        Args:
            time_resolution: Résolution temporelle ('hour', 'day', 'week')
            
        Returns:
            Dataset pour carte de chaleur des activités de routage
        """
        try:
            # Récupérer l'historique des forwards
            forwards = self.metrics_collector.lnd_client.get_forwarding_history(limit=10000)
            forwarding_events = forwards.get("forwarding_events", [])
            
            if not forwarding_events:
                logger.warning("Aucun événement de forwarding trouvé")
                return {"error": "Aucun événement de forwarding trouvé"}
            
            # Convertir les timestamps en objets datetime
            for event in forwarding_events:
                if isinstance(event["timestamp"], str):
                    event["timestamp"] = datetime.fromisoformat(event["timestamp"])
            
            # Trier par timestamp
            forwarding_events.sort(key=lambda x: x["timestamp"])
            
            # Déterminer la période couverte
            start_time = forwarding_events[0]["timestamp"]
            end_time = forwarding_events[-1]["timestamp"]
            
            # Convertir en dataframe pour faciliter l'analyse
            df = pd.DataFrame(forwarding_events)
            
            # Convertir les timestamps en datetime si ce n'est pas déjà fait
            if not pd.api.types.is_datetime64_dtype(df["timestamp"]):
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            
            # Définir les buckets temporels en fonction de la résolution
            if time_resolution == "hour":
                df["time_bucket"] = df["timestamp"].dt.floor("H")
                bucket_format = "%Y-%m-%d %H:00"
            elif time_resolution == "day":
                df["time_bucket"] = df["timestamp"].dt.floor("D")
                bucket_format = "%Y-%m-%d"
            elif time_resolution == "week":
                df["time_bucket"] = df["timestamp"].dt.to_period("W").dt.start_time
                bucket_format = "%Y-%m-%d"
            else:
                logger.warning(f"Résolution temporelle non reconnue: {time_resolution}, utilisation de 'hour'")
                df["time_bucket"] = df["timestamp"].dt.floor("H")
                bucket_format = "%Y-%m-%d %H:00"
            
            # Agréger par bucket temporel et canal
            heatmap_data = df.groupby(["time_bucket", "chan_id_out"]).agg({
                "amt_out": "sum",
                "fee": "sum",
                "chan_id_out": "count"
            }).rename(columns={"chan_id_out": "count"}).reset_index()
            
            # Créer une liste de tous les buckets temporels pour une visualisation complète
            all_buckets = pd.date_range(start=start_time.floor("H"), end=end_time.ceil("H"), freq=time_resolution[0].upper())
            
            # Obtenir la liste unique des canaux
            unique_channels = df["chan_id_out"].unique()
            
            # Créer des entrées pour toutes les combinaisons (pour une heatmap complète)
            full_heatmap_data = []
            
            for time_bucket in all_buckets:
                bucket_str = time_bucket.strftime(bucket_format)
                
                # Chercher les données existantes pour ce bucket
                bucket_data = heatmap_data[heatmap_data["time_bucket"] == time_bucket]
                
                if not bucket_data.empty:
                    # Il y a des données pour ce bucket
                    for _, row in bucket_data.iterrows():
                        full_heatmap_data.append({
                            "time_bucket": bucket_str,
                            "channel_id": str(row["chan_id_out"]),
                            "amount": int(row["amt_out"]),
                            "fee": int(row["fee"]),
                            "count": int(row["count"])
                        })
                    
                    # Ajouter des entrées avec zéro pour les canaux sans activité
                    active_channels = set(bucket_data["chan_id_out"])
                    for channel in unique_channels:
                        if channel not in active_channels:
                            full_heatmap_data.append({
                                "time_bucket": bucket_str,
                                "channel_id": str(channel),
                                "amount": 0,
                                "fee": 0,
                                "count": 0
                            })
                else:
                    # Aucune donnée pour ce bucket, ajouter des zéros pour tous les canaux
                    for channel in unique_channels:
                        full_heatmap_data.append({
                            "time_bucket": bucket_str,
                            "channel_id": str(channel),
                            "amount": 0,
                            "fee": 0,
                            "count": 0
                        })
            
            # Compiler le dataset
            dataset = {
                "timestamp": datetime.now().isoformat(),
                "time_resolution": time_resolution,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "channels": [str(c) for c in unique_channels],
                "heatmap_data": full_heatmap_data,
                "metadata": {
                    "total_forwards": len(forwarding_events),
                    "total_amount": int(df["amt_out"].sum()),
                    "total_fees": int(df["fee"].sum()),
                    "active_channels": len(unique_channels)
                }
            }
            
            # Stocker le dataset
            self._datasets["routing_heatmap"] = dataset
            
            return dataset
        except Exception as e:
            logger.error(f"Erreur lors de la génération du dataset de heatmap: {e}")
            return {"error": str(e)}
    
    async def generate_fee_optimization_dataset(self) -> Dict:
        """Génère un dataset pour optimisation des frais
        
        Returns:
            Dataset pour optimisation des frais
        """
        try:
            # Récupérer le nœud local enrichi
            local_node = await self.node_aggregator.get_enriched_node(settings.NODE_PUBKEY)
            
            # Récupérer les données de forwarding
            forwards = self.metrics_collector.lnd_client.get_forwarding_history(limit=5000)
            forwarding_events = forwards.get("forwarding_events", [])
            
            # Agréger les données par canal
            channel_stats = {}
            
            for event in forwarding_events:
                chan_id_out = str(event.get("chan_id_out"))
                
                if chan_id_out not in channel_stats:
                    channel_stats[chan_id_out] = {
                        "total_forwards": 0,
                        "total_amount": 0,
                        "total_fees": 0,
                        "fee_rate_sum": 0,  # Pour calculer la moyenne
                    }
                
                stats = channel_stats[chan_id_out]
                stats["total_forwards"] += 1
                stats["total_amount"] += event.get("amt_out", 0)
                stats["total_fees"] += event.get("fee", 0)
                
                # Calculer le taux de frais pour cet événement
                amt_out = event.get("amt_out", 0)
                fee = event.get("fee", 0)
                if amt_out > 0:
                    fee_rate = fee / amt_out * 1000000  # En ppm
                    stats["fee_rate_sum"] += fee_rate
            
            # Calculer des métriques supplémentaires
            for chan_id, stats in channel_stats.items():
                if stats["total_forwards"] > 0:
                    stats["avg_fee_rate"] = stats["fee_rate_sum"] / stats["total_forwards"]
                else:
                    stats["avg_fee_rate"] = 0
                
                if stats["total_amount"] > 0:
                    stats["effective_fee_rate"] = stats["total_fees"] / stats["total_amount"] * 1000000
                else:
                    stats["effective_fee_rate"] = 0
            
            # Récupérer les données de canaux pour compléter
            channels_data = []
            
            for channel in local_node.channels.values():
                channel_id = channel.channel_id
                
                # Récupérer les statistiques de forwarding si disponibles
                stats = channel_stats.get(channel_id, {
                    "total_forwards": 0,
                    "total_amount": 0,
                    "total_fees": 0,
                    "avg_fee_rate": 0,
                    "effective_fee_rate": 0
                })
                
                # Récupérer la politique de frais actuelle
                fee_rate = None
                base_fee = None
                
                if "lnd_data" in channel and "policy" in channel.lnd_data:
                    policy = channel.lnd_data["policy"]
                    fee_rate = policy.get("fee_rate_milli_msat", 0) / 1000  # Convertir en ppm
                    base_fee = policy.get("fee_base_msat", 0) / 1000  # Convertir en sats
                
                # Calculer des suggestions de frais basées sur la performance
                suggested_fee_rate = None
                
                if stats["total_forwards"] > 0:
                    # Si le canal est actif, suggérer en fonction de l'utilisation
                    if stats["total_forwards"] > 10:
                        # Canal très utilisé, optimiser pour le revenu
                        suggested_fee_rate = stats["effective_fee_rate"] * 1.2  # +20%
                    else:
                        # Canal peu utilisé, optimiser pour l'attractivité
                        suggested_fee_rate = stats["effective_fee_rate"] * 0.8  # -20%
                else:
                    # Si le canal n'est pas utilisé, suggérer un taux plus bas ou celui des pairs
                    suggested_fee_rate = 10  # Valeur par défaut basse
                
                # Limiter les suggestions à des valeurs raisonnables
                if suggested_fee_rate is not None:
                    suggested_fee_rate = max(1, min(5000, round(suggested_fee_rate)))
                
                # Ajouter les données du canal
                channels_data.append({
                    "channel_id": channel_id,
                    "peer_pubkey": channel.node2_pub,
                    "capacity": channel.capacity,
                    "local_ratio": channel.local_ratio,
                    "active": channel.active,
                    "private": channel.private,
                    "current_fee_rate": fee_rate,
                    "current_base_fee": base_fee,
                    "total_forwards": stats["total_forwards"],
                    "total_amount": stats["total_amount"],
                    "total_fees": stats["total_fees"],
                    "avg_fee_rate": stats["avg_fee_rate"],
                    "effective_fee_rate": stats["effective_fee_rate"],
                    "suggested_fee_rate": suggested_fee_rate,
                    "suggested_base_fee": 1,  # Base fee standard
                    "revenue_impact": None  # À calculer
                })
            
            # Compiler le dataset
            dataset = {
                "timestamp": datetime.now().isoformat(),
                "channels": channels_data,
                "metadata": {
                    "total_channels": len(channels_data),
                    "active_forwarding_channels": sum(1 for c in channels_data if c["total_forwards"] > 0),
                    "total_forwards": sum(c["total_forwards"] for c in channels_data),
                    "total_fees": sum(c["total_fees"] for c in channels_data),
                    "avg_effective_fee_rate": sum(c["effective_fee_rate"] for c in channels_data if c["total_forwards"] > 0) / 
                                             max(1, sum(1 for c in channels_data if c["total_forwards"] > 0))
                }
            }
            
            # Stocker le dataset
            self._datasets["fee_optimization"] = dataset
            
            return dataset
        except Exception as e:
            logger.error(f"Erreur lors de la génération du dataset d'optimisation des frais: {e}")
            return {"error": str(e)}
    
    async def generate_periodic_report(self, report_type: str, parameters: Dict = None) -> Union[str, Dict]:
        """Génère un rapport périodique basé sur les données collectées
        
        Args:
            report_type: Type de rapport ('daily', 'weekly', 'monthly')
            parameters: Paramètres spécifiques au rapport
            
        Returns:
            Chemin du rapport généré ou données du rapport
        """
        parameters = parameters or {}
        
        try:
            if report_type == "daily":
                # Rapport quotidien standard
                return await self._generate_daily_report(parameters)
            elif report_type == "weekly":
                # Rapport hebdomadaire plus détaillé
                return await self._generate_weekly_report(parameters)
            elif report_type == "monthly":
                # Rapport mensuel avec analyse approfondie
                return await self._generate_monthly_report(parameters)
            else:
                logger.warning(f"Type de rapport non reconnu: {report_type}")
                return {"error": f"Type de rapport non reconnu: {report_type}"}
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport périodique: {e}")
            return {"error": str(e)}
    
    async def _generate_daily_report(self, parameters: Dict) -> Dict:
        """Génère un rapport quotidien
        
        Args:
            parameters: Paramètres spécifiques au rapport
            
        Returns:
            Données du rapport
        """
        # Récupérer les données nécessaires
        node_metrics = await self.metrics_collector.collect_node_metrics()
        forwarding_metrics = await self.metrics_collector.collect_forwarding_metrics(time_window_hours=24)
        
        # Compiler le rapport
        report = {
            "timestamp": datetime.now().isoformat(),
            "report_type": "daily",
            "node_metrics": {
                "total_capacity": node_metrics.get("total_capacity", 0),
                "active_channels": node_metrics.get("num_active_channels", 0),
                "local_balance_ratio": node_metrics.get("local_ratio", 0),
            },
            "forwarding_metrics": {
                "total_forwards": forwarding_metrics.get("total_forwards", 0),
                "total_amount_forwarded": forwarding_metrics.get("total_amount_forwarded", 0),
                "total_fees_earned": forwarding_metrics.get("total_fees_earned", 0),
                "avg_fee_rate_ppm": forwarding_metrics.get("avg_fee_rate_ppm", 0),
                "top_channels_in": dict(sorted(forwarding_metrics.get("channels_in", {}).items(), 
                                              key=lambda x: x[1]["amount"], reverse=True)[:5]),
                "top_channels_out": dict(sorted(forwarding_metrics.get("channels_out", {}).items(), 
                                               key=lambda x: x[1]["amount"], reverse=True)[:5])
            }
        }
        
        return report
    
    async def _generate_weekly_report(self, parameters: Dict) -> Dict:
        """Génère un rapport hebdomadaire
        
        Args:
            parameters: Paramètres spécifiques au rapport
            
        Returns:
            Données du rapport
        """
        # Implémenter le rapport hebdomadaire
        # C'est un placeholder pour le moment
        return {"message": "Rapport hebdomadaire non implémenté"}
    
    async def _generate_monthly_report(self, parameters: Dict) -> Dict:
        """Génère un rapport mensuel
        
        Args:
            parameters: Paramètres spécifiques au rapport
            
        Returns:
            Données du rapport
        """
        # Implémenter le rapport mensuel
        # C'est un placeholder pour le moment
        return {"message": "Rapport mensuel non implémenté"}
    
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