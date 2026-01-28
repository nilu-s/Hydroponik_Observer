from __future__ import annotations

from fastapi import APIRouter

from .admin import router as admin_router
from .cameras import router as cameras_router
from .nodes import router as nodes_router
from .setups import router as setups_router
router = APIRouter(prefix="/api")
router.include_router(setups_router)
router.include_router(nodes_router)
router.include_router(cameras_router)
router.include_router(admin_router)
