from fastapi import APIRouter

from app.api.api_v1.endpoints import network, channels, dashboard, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentification"])
api_router.include_router(network.router, prefix="/network", tags=["réseau"])
api_router.include_router(channels.router, prefix="/channels", tags=["canaux"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["tableau de bord"]) 