from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter()

@router.get("/node/{pubkey}")
async def get_node_info(pubkey: str) -> Dict[str, Any]:
    """
    Récupère les informations d'un nœud Lightning par sa clé publique.
    En mode développement, retourne des données simulées.
    """
    try:
        # En mode développement, retourner des données simulées
        return {
            "alias": "Feustey",
            "pubkey": pubkey,
            "customTags": ["#GSpotSuperNode"],
            "isFavorite": True,
            "stats": {
                "capacity": {
                    "total": 17965032,
                    "percentChange": 0,
                },
                "channels": {
                    "count": 12,
                    "percentChange": 0,
                    "biggest": 3000000,
                    "smallest": 500000,
                    "average": 1497086,
                    "median": 1043613,
                },
                "timeData": {
                    "lastUpdate": "1 hour ago",
                    "aot": "1h 29m",
                    "oldest": "57d 13h 20m",
                    "youngest": "7d 20h 40m",
                    "averageAge": "36d 18h 53m",
                    "medianAge": "42d 10m",
                },
                "rankings": {
                    "channels": {
                        "rank": 1148,
                        "change": 3,
                    },
                    "capacity": {
                        "rank": 1860,
                        "change": 1,
                    },
                },
            },
            "identifiers": {
                "torAddress": "02778f4a4eb3a2344b9fd8ee72e7ec5f03f803e5f5273e2e1a2af508",
                "link": f"https://amboss.space/node/{pubkey}",
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des données du nœud: {str(e)}"
        ) 