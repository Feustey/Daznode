from prometheus_client import Counter, Gauge, Histogram, start_http_server
import time
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MetricsExporter:
    """Service d'exportation des métriques au format Prometheus"""
    
    def __init__(self, port: int = 8000):
        self.port = port
        
        # Métriques de l'API
        self.api_requests_total = Counter(
            'daznode_api_requests_total',
            'Nombre total de requêtes API',
            ['endpoint', 'method', 'status']
        )
        
        self.api_response_time = Histogram(
            'daznode_api_response_time_seconds',
            'Temps de réponse de l\'API',
            ['endpoint', 'method'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
        )
        
        # Métriques des sources de données
        self.data_source_health = Gauge(
            'daznode_data_source_health',
            'État de santé des sources de données',
            ['source']
        )
        
        self.data_source_latency = Histogram(
            'daznode_data_source_latency_seconds',
            'Latence des sources de données',
            ['source', 'operation'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
        )
        
        # Métriques du réseau
        self.network_nodes = Gauge(
            'daznode_network_nodes_total',
            'Nombre total de nœuds dans le réseau'
        )
        
        self.network_channels = Gauge(
            'daznode_network_channels_total',
            'Nombre total de canaux dans le réseau'
        )
        
        self.network_capacity = Gauge(
            'daznode_network_capacity_satoshis',
            'Capacité totale du réseau en satoshis'
        )
        
        # Métriques du cache
        self.cache_hits = Counter(
            'daznode_cache_hits_total',
            'Nombre total de hits du cache',
            ['cache_type']
        )
        
        self.cache_misses = Counter(
            'daznode_cache_misses_total',
            'Nombre total de misses du cache',
            ['cache_type']
        )
        
        # Métriques système
        self.memory_usage = Gauge(
            'daznode_memory_usage_bytes',
            'Utilisation de la mémoire'
        )
        
        self.cpu_usage = Gauge(
            'daznode_cpu_usage_percent',
            'Utilisation du CPU'
        )
    
    def start(self):
        """Démarrer le serveur de métriques"""
        try:
            start_http_server(self.port)
            logger.info(f"Serveur de métriques démarré sur le port {self.port}")
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du serveur de métriques: {str(e)}")
            raise
    
    def record_api_request(self, endpoint: str, method: str, status: int, duration: float):
        """Enregistrer une requête API"""
        self.api_requests_total.labels(
            endpoint=endpoint,
            method=method,
            status=status
        ).inc()
        
        self.api_response_time.labels(
            endpoint=endpoint,
            method=method
        ).observe(duration)
    
    def update_data_source_health(self, source: str, healthy: bool):
        """Mettre à jour l'état de santé d'une source de données"""
        self.data_source_health.labels(source=source).set(1 if healthy else 0)
    
    def record_data_source_latency(self, source: str, operation: str, duration: float):
        """Enregistrer la latence d'une opération sur une source de données"""
        self.data_source_latency.labels(
            source=source,
            operation=operation
        ).observe(duration)
    
    def update_network_metrics(self, stats: Dict[str, Any]):
        """Mettre à jour les métriques du réseau"""
        self.network_nodes.set(stats.get('num_nodes', 0))
        self.network_channels.set(stats.get('num_channels', 0))
        self.network_capacity.set(stats.get('total_capacity', 0))
    
    def record_cache_access(self, cache_type: str, hit: bool):
        """Enregistrer un accès au cache"""
        if hit:
            self.cache_hits.labels(cache_type=cache_type).inc()
        else:
            self.cache_misses.labels(cache_type=cache_type).inc()
    
    def update_system_metrics(self, memory_bytes: int, cpu_percent: float):
        """Mettre à jour les métriques système"""
        self.memory_usage.set(memory_bytes)
        self.cpu_usage.set(cpu_percent) 