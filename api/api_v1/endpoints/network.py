from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List

from app.api.deps import get_current_user
from app.schemas.network import NetworkStats, NodeInfo
from app.services.mcp import MCPService

router = APIRouter()
mcp_service = MCPService()


@router.get("/stats", response_model=NetworkStats)
async def get_network_stats(
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère les statistiques globales du réseau Lightning.
    """
    try:
        stats = await mcp_service.get_network_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")


@router.get("/nodes", response_model=List[NodeInfo])
async def get_network_nodes(
    limit: int = 50, 
    offset: int = 0,
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère la liste des nœuds du réseau Lightning.
    """
    try:
        nodes = await mcp_service.get_network_nodes(limit=limit, offset=offset)
        return nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des nœuds: {str(e)}")


@router.get("/map", response_model=Any)
async def get_network_map(
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère les données pour la carte du réseau Lightning.
    """
    try:
        map_data = await mcp_service.get_network_map()
        return map_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la carte: {str(e)}")


@router.get("/nodes/{node_id}", response_model=NodeInfo)
async def get_node_details(
    node_id: str,
    current_user=Depends(get_current_user)
) -> Any:
    """
    Récupère les détails d'un nœud spécifique.
    """
    try:
        node = await mcp_service.get_node_details(node_id=node_id)
        if not node:
            raise HTTPException(status_code=404, detail="Nœud non trouvé")
        return node
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des détails du nœud: {str(e)}") 