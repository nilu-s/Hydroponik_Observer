from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException

import shutil

from ..config import ADMIN_RESET_TOKEN, PHOTOS_DIR, ensure_dirs, log_event
from ..db import init_db
from ..camera_devices import reset_runtime as reset_camera_runtime
from ..camera_streaming import reset_runtime as reset_camera_streaming
from ..nodes import reset_runtime as reset_node_runtime
from ..realtime_updates import broadcast_system_reset
from ..security import ROLE_ADMIN, require_roles

router = APIRouter(prefix="/admin")


@router.post("/reset", dependencies=[Depends(require_roles(ROLE_ADMIN))])
async def reset_db(token: str = Header("", alias="X-Reset-Token")) -> dict:
    if not ADMIN_RESET_TOKEN:
        raise HTTPException(status_code=500, detail="reset token not configured")
    if token != ADMIN_RESET_TOKEN:
        raise HTTPException(status_code=401, detail="unauthorized")
    init_db(reset=True)
    reset_node_runtime()
    reset_camera_runtime()
    reset_camera_streaming()
    if PHOTOS_DIR.exists():
        shutil.rmtree(PHOTOS_DIR, ignore_errors=True)
    ensure_dirs()
    log_event("db.reset")
    await broadcast_system_reset("db-reset")
    return {"ok": True}
