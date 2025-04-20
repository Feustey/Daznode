from fastapi import APIRouter

api_router = APIRouter()

# Ici, vous pourrez plus tard ajouter les routes comme:
# from app.api.api_v1.endpoints import items, users
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(items.router, prefix="/items", tags=["items"]) 