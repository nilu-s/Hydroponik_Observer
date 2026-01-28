from __future__ import annotations

from fastapi import APIRouter, Depends

from .admin import router as admin_router
from .cameras import router as cameras_router
from .nodes import router as nodes_router
from .setups import router as setups_router
from ..security import ROLE_ADMIN, ROLE_OPERATOR, ROLE_VIEWER, require_roles

router = APIRouter(
    prefix="/api",
    dependencies=[
        Depends(require_roles(ROLE_VIEWER, ROLE_OPERATOR, ROLE_ADMIN)),
    ],
)
router.include_router(setups_router)
router.include_router(nodes_router)
router.include_router(cameras_router)
router.include_router(admin_router)
