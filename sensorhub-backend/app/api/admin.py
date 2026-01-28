from __future__ import annotations

import time

from fastapi import APIRouter, Header, HTTPException

import shutil

from ..config import ADMIN_RESET_TOKEN, PHOTOS_DIR, ensure_dirs, log_event
from ..db import reset_db_contents
from ..camera_devices import list_camera_devices, reset_runtime as reset_camera_runtime
from ..camera_streaming import reset_runtime as reset_camera_streaming
from ..camera_worker_manager import get_camera_worker_manager
from ..nodes import reset_runtime as reset_node_runtime
from ..realtime_updates import broadcast_system_reset
from ..db import list_setups

router = APIRouter(prefix="/admin")


@router.post("/reset")
async def reset_db(token: str | None = Header(None, alias="X-Reset-Token")) -> dict:
    if not ADMIN_RESET_TOKEN:
        raise HTTPException(status_code=403, detail="admin reset disabled: set ADMIN_RESET_TOKEN")
    if not token:
        raise HTTPException(status_code=401, detail="reset token required")
    if token != ADMIN_RESET_TOKEN:
        raise HTTPException(status_code=401, detail="invalid reset token")
    reset_db_contents()
    reset_node_runtime()
    reset_camera_runtime()
    reset_camera_streaming()
    if PHOTOS_DIR.exists():
        shutil.rmtree(PHOTOS_DIR, ignore_errors=True)
    ensure_dirs()
    log_event("db.reset")
    await broadcast_system_reset("db-reset")
    return {"ok": True}


@router.get("/health")
async def get_health() -> dict:
    manager = get_camera_worker_manager()
    worker_health = manager.get_health()
    return {
        "ok": True,
        "ts": int(time.time() * 1000),
        "workers": worker_health,
        "setups": {"count": len(list_setups())},
        "cameras": {"count": len(list_camera_devices())},
    }
