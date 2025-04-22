from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/api/v1", tags=["api"])

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Endpoint de vérification de santé"""
    try:
        return {
            "status": "ok",
            "message": "Service opérationnel"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 