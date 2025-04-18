from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, List

from app.api.deps import get_current_user
from app.schemas.dashboard import NodeStatus, NodeMetrics, LiquidityOverview
from app.services.feustey import FeusteyService
from app.services.mcp import MCPService

router = APIRouter()
feustey_service = FeusteyService()
mcp_service = MCPService()


@router.get("/status", response_model=NodeStatus)
async def get_node_status(
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère le statut actuel du nœud de l'utilisateur.
    """
    try:
        status = await feustey_service.get_node_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du statut: {str(e)}")


@router.get("/metrics", response_model=NodeMetrics)
async def get_node_metrics(
    timeframe: str = "day",
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère les métriques du nœud sur une période donnée.
    """
    valid_timeframes = ["hour", "day", "week", "month", "year"]
    if timeframe not in valid_timeframes:
        raise HTTPException(status_code=400, detail=f"Timeframe invalide. Valeurs acceptées: {valid_timeframes}")
    
    try:
        metrics = await feustey_service.get_node_metrics(timeframe=timeframe)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des métriques: {str(e)}")


@router.get("/liquidity", response_model=LiquidityOverview)
async def get_liquidity_overview(
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère une vue d'ensemble de la liquidité du nœud.
    """
    try:
        liquidity = await feustey_service.get_liquidity_overview()
        return liquidity
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données de liquidité: {str(e)}")


@router.get("/recommendations", response_model=List[Dict[str, Any]])
async def get_node_recommendations(
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère des recommandations pour améliorer les performances du nœud.
    """
    try:
        recommendations = await feustey_service.get_node_recommendations()
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des recommandations: {str(e)}")


@router.get("/insights", response_model=Dict[str, Any])
async def get_network_insights(
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère des insights sur le positionnement du nœud dans le réseau.
    """
    try:
        # Combine des données du nœud local et des données MCP
        node_data = await feustey_service.get_node_data()
        network_context = await mcp_service.get_node_network_context(node_data["node_id"])
        
        insights = {
            "node_data": node_data,
            "network_context": network_context,
            "ranking": await mcp_service.get_node_ranking(node_data["node_id"]),
            "growth_trends": await mcp_service.get_network_growth_trends()
        }
        
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des insights: {str(e)}") 