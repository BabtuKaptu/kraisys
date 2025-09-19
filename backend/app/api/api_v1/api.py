"""
API router for KRAI System v0.6
"""

from fastapi import APIRouter

from . import endpoints

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    endpoints.models.router,
    prefix="/models",
    tags=["models"]
)

api_router.include_router(
    endpoints.materials.router,
    prefix="/materials",
    tags=["materials"]
)

api_router.include_router(
    endpoints.warehouse.router,
    prefix="/warehouse",
    tags=["warehouse"]
)

api_router.include_router(
    endpoints.production.router,
    prefix="/production",
    tags=["production"]
)

api_router.include_router(
    endpoints.references.router,
    prefix="/references",
    tags=["references"]
)