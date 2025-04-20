from fastapi import FastAPI, Depends, HTTPException, Query, Body, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from core.config import settings
from services.lnd_client import LNDClient
from services.lnrouter_client import LNRouterClient
from services.metrics_collector import MetricsCollector
from services.node_aggregator import NodeAggregator
from services.visualization_exporter import VisualizationExporter

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("daznode-api")

# Initialisation de l'API
app = FastAPI(
    title="Daznode API",
    description="API pour la gestion et l'analyse de nœuds Lightning Network",
    version="0.1.0",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Classes pour les services partagés
class Services:
    lnd_client = LNDClient()
    lnrouter_client = LNRouterClient()
    metrics_collector = MetricsCollector(lnd_client=lnd_client)
    node_aggregator = NodeAggregator(lnd_client=lnd_client, lnrouter_client=lnrouter_client)
    visualization_exporter = VisualizationExporter(
        metrics_collector=metrics_collector, 
        node_aggregator=node_aggregator
    )

services = Services()

# Routes pour le nœud
@app.get("/api/v1/node/info", tags=["Nœud"])
async def get_node_info():
    """Récupère les informations du nœud local"""
    try:
        return services.lnd_client.get_node_info()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations du nœud: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/node/metrics", tags=["Nœud"])
async def get_node_metrics():
    """Récupère les métriques du nœud local"""
    try:
        return await services.metrics_collector.collect_node_metrics()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques du nœud: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routes pour les canaux
@app.get("/api/v1/channels", tags=["Canaux"])
async def list_channels(active: bool = Query(None, description="Filtrer les canaux actifs")):
    """Liste les canaux du nœud"""
    try:
        active_only = active if active is not None else False
        inactive_only = not active if active is not None else False
        
        return services.lnd_client.list_channels(
            active_only=active_only,
            inactive_only=inactive_only
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des canaux: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/channels/metrics", tags=["Canaux"])
async def get_channel_metrics():
    """Récupère les métriques détaillées des canaux"""
    try:
        return await services.metrics_collector.collect_channel_metrics()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques des canaux: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/channels/performance", tags=["Canaux"])
async def get_channel_performance(days: int = Query(30, description="Nombre de jours d'historique")):
    """Récupère les données de performance des canaux"""
    try:
        return await services.visualization_exporter.generate_channel_performance_dataset(days=days)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des performances des canaux: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routes pour le forwarding
@app.get("/api/v1/forwarding", tags=["Forwarding"])
async def get_forwarding_history(
    hours: int = Query(24, description="Nombre d'heures d'historique"),
    limit: int = Query(1000, description="Limite de résultats")
):
    """Récupère l'historique de forwarding"""
    try:
        end_time = int(datetime.now().timestamp())
        start_time = end_time - hours * 3600
        
        return services.lnd_client.get_forwarding_history(
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'historique de forwarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/forwarding/metrics", tags=["Forwarding"])
async def get_forwarding_metrics(hours: int = Query(24, description="Nombre d'heures d'historique")):
    """Récupère les métriques agrégées de forwarding"""
    try:
        return await services.metrics_collector.collect_forwarding_metrics(time_window_hours=hours)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques de forwarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/forwarding/heatmap", tags=["Forwarding"])
async def get_forwarding_heatmap(
    resolution: str = Query("hour", description="Résolution temporelle (hour, day, week)")
):
    """Récupère les données pour une heatmap de routage"""
    try:
        return await services.visualization_exporter.generate_routing_heatmap_dataset(time_resolution=resolution)
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routes pour l'optimisation
@app.get("/api/v1/optimization/fees", tags=["Optimisation"])
async def get_fee_optimization():
    """Récupère des suggestions d'optimisation de frais"""
    try:
        return await services.visualization_exporter.generate_fee_optimization_dataset()
    except Exception as e:
        logger.error(f"Erreur lors de la génération des optimisations de frais: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routes pour le réseau
@app.get("/api/v1/network/graph", tags=["Réseau"])
async def get_network_graph():
    """Récupère les données pour un graphe du réseau local"""
    try:
        return await services.visualization_exporter.generate_network_graph_dataset()
    except Exception as e:
        logger.error(f"Erreur lors de la génération du graphe réseau: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/network/stats", tags=["Réseau"])
async def get_network_stats():
    """Récupère les statistiques globales du réseau Lightning"""
    try:
        return await services.node_aggregator.get_network_context()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques réseau: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/network/node/{pubkey}", tags=["Réseau"])
async def get_node_details(pubkey: str = Path(..., description="Clé publique du nœud")):
    """Récupère les détails d'un nœud spécifique"""
    try:
        node = await services.node_aggregator.get_enriched_node(pubkey)
        return node.to_dict()  # Convertir l'objet en dictionnaire pour la sérialisation JSON
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des détails du nœud {pubkey}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routes pour les métriques
@app.post("/api/v1/metrics/snapshot", tags=["Métriques"])
async def create_daily_snapshot():
    """Crée un snapshot quotidien des métriques"""
    try:
        snapshot_id = await services.metrics_collector.create_daily_snapshot()
        return {"snapshot_id": snapshot_id}
    except Exception as e:
        logger.error(f"Erreur lors de la création du snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Route pour les rapports
@app.get("/api/v1/reports/{report_type}", tags=["Rapports"])
async def generate_report(
    report_type: str = Path(..., description="Type de rapport (daily, weekly, monthly)"),
    parameters: Dict = Query(None, description="Paramètres du rapport")
):
    """Génère un rapport périodique"""
    try:
        report = await services.visualization_exporter.generate_periodic_report(
            report_type=report_type,
            parameters=parameters or {}
        )
        return report
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport {report_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Route de healthcheck
@app.get("/health", tags=["Système"])
async def health_check():
    """Vérifie l'état de l'API"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Route de status du nœud
@app.get("/api/v1/status", tags=["Système"])
async def get_node_status():
    """Récupère l'état du nœud et des services associés"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "node": {"status": "unknown"},
        "lnrouter": {"status": "unknown"},
        "api": {"status": "ok", "version": "0.1.0"}
    }
    
    # Vérifier l'état du nœud LND
    try:
        node_info = services.lnd_client.get_node_info()
        status["node"] = {
            "status": "ok",
            "alias": node_info.get("alias"),
            "pubkey": node_info.get("pubkey"),
            "block_height": node_info.get("block_height"),
            "synced_to_chain": node_info.get("synced_to_chain"),
            "num_active_channels": node_info.get("num_active_channels"),
        }
    except Exception as e:
        status["node"] = {"status": "error", "error": str(e)}
    
    # Vérifier l'état de LNRouter
    try:
        # Juste une vérification basique
        graph = await services.lnrouter_client.get_graph(force_refresh=False)
        status["lnrouter"] = {
            "status": "ok",
            "last_update": services.lnrouter_client.last_graph_update.isoformat() 
                if services.lnrouter_client.last_graph_update else None
        }
    except Exception as e:
        status["lnrouter"] = {"status": "error", "error": str(e)}
    
    return status

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 