from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List

from app.api.deps import get_current_user
from app.schemas.channel import ChannelInfo, ChannelStats
from app.services.mcp import MCPService

router = APIRouter()
mcp_service = MCPService()


@router.get("/stats", response_model=ChannelStats)
async def get_channels_stats(
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère les statistiques globales des canaux du réseau Lightning.
    """
    try:
        stats = await mcp_service.get_channels_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")


@router.get("/list", response_model=List[ChannelInfo])
async def get_channels_list(
    limit: int = 50, 
    offset: int = 0,
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère la liste des canaux du réseau Lightning.
    """
    try:
        channels = await mcp_service.get_channels_list(limit=limit, offset=offset)
        return channels
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des canaux: {str(e)}")


@router.get("/{channel_id}", response_model=ChannelInfo)
async def get_channel_details(
    channel_id: str,
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère les détails d'un canal spécifique.
    """
    try:
        channel = await mcp_service.get_channel_details(channel_id=channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Canal non trouvé")
        return channel
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des détails du canal: {str(e)}")


@router.get("/node/{node_id}", response_model=List[ChannelInfo])
async def get_node_channels(
    node_id: str,
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère les canaux d'un nœud spécifique.
    """
    try:
        channels = await mcp_service.get_node_channels(node_id=node_id)
        return channels
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des canaux du nœud: {str(e)}")


@router.get("/performance", response_model=Any)
async def get_channels_performance(
    timeframe: str = "week",
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère les données de performance des canaux.
    """
    valid_timeframes = ["day", "week", "month", "year"]
    if timeframe not in valid_timeframes:
        raise HTTPException(status_code=400, detail=f"Timeframe invalide. Valeurs acceptées: {valid_timeframes}")
    
    try:
        performance = await mcp_service.get_channels_performance(timeframe=timeframe)
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des performances: {str(e)}") 