from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import logging

from services.umbrel_ui_exporter import UmbrelUIExporter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/umbrel-ui", tags=["umbrel-ui"])

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Endpoint pour récupérer le dashboard HTML"""
    try:
        exporter = UmbrelUIExporter()
        dashboard_html = await exporter.generate_dashboard()
        return HTMLResponse(content=dashboard_html)
    except Exception as e:
        logger.error(f"Erreur lors de la génération du dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la génération du dashboard")

@router.get("/api/stats")
async def get_stats():
    """Endpoint pour récupérer les statistiques en JSON"""
    try:
        exporter = UmbrelUIExporter()
        network_stats = await exporter.data_source.get_network_stats()
        return JSONResponse(content=network_stats)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des statistiques")

@router.get("/api/graph")
async def get_graph():
    """Endpoint pour récupérer les données du graphe en JSON"""
    try:
        exporter = UmbrelUIExporter()
        graph_data = await exporter.visualization_exporter.generate_network_graph_dataset()
        return JSONResponse(content=graph_data)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du graphe: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du graphe") 