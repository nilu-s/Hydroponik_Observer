from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException

import shutil

from ..config import PHOTOS_DIR, ensure_dirs, log_event
from ..db import init_db
from ..camera_devices import reset_runtime as reset_camera_runtime
from ..camera_streaming import reset_runtime as reset_camera_streaming
from ..nodes import reset_runtime as reset_node_runtime
from ..realtime_updates import broadcast_system_reset

router = APIRouter(prefix="/admin")


@router.post("/reset")
async def reset_db(token: str = Header("", alias="X-Reset-Token")) -> dict:
    if token != "reset123":
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
