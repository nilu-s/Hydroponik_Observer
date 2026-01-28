from __future__ import annotations

import asyncio
import platform
from typing import Any

from fastapi import Depends, FastAPI, WebSocket
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
from .config import (
    CORS_ALLOW_ORIGINS,
    CSRF_TOKEN,
    CSRF_TRUSTED_ORIGINS,
    DATA_DIR,
    ensure_dirs,
    log_event,
)
from .db import close_connections, init_db, list_setups
from .realtime_updates import LiveManager, readings_capture_loop, register_live_manager as register_ws_manager
from .nodes import node_discovery_loop
from .camera_devices import camera_discovery_loop, register_live_manager
from .camera_streaming import photo_capture_loop, snapshot_camera, stream_camera
from .security import ROLE_ADMIN, ROLE_OPERATOR, ROLE_VIEWER, authenticate_ws, require_roles


app = FastAPI(title="SensorHub Backend")
ensure_dirs()
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def csrf_protect(request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        if request.url.path.startswith("/data"):
            return await call_next(request)
        origin = request.headers.get("origin")
        if origin:
            if origin not in CSRF_TRUSTED_ORIGINS:
                return JSONResponse(status_code=403, content={"detail": "csrf origin forbidden"})
        else:
            header_token = request.headers.get("x-csrf-token", "")
            if not CSRF_TOKEN or header_token != CSRF_TOKEN:
                return JSONResponse(status_code=403, content={"detail": "csrf token required"})
    return await call_next(request)

app.include_router(api_router)
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")

live_manager = LiveManager()
register_ws_manager(live_manager)

def _set_windows_keep_awake(enable: bool) -> None:
    if platform.system() != "Windows":
        return
    try:
        import ctypes

        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_AWAYMODE_REQUIRED = 0x00000040
        if enable:
            flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED
        else:
            flags = ES_CONTINUOUS
        ctypes.windll.kernel32.SetThreadExecutionState(flags)
    except Exception:
        pass


@app.on_event("startup")
async def on_startup() -> None:
    ensure_dirs()
    init_db()
    register_live_manager(live_manager)
    _set_windows_keep_awake(True)
    app.state.node_task = asyncio.create_task(node_discovery_loop())
    app.state.readings_task = asyncio.create_task(readings_capture_loop())
    app.state.camera_task = asyncio.create_task(camera_discovery_loop())
    app.state.photo_task = asyncio.create_task(photo_capture_loop())
    setups = list_setups()
    loop_setups = [
        {
            "setup_id": setup["setup_id"],
            "name": setup.get("name"),
            "node_id": setup.get("node_id"),
            "value_interval_minutes": setup.get("value_interval_minutes"),
            "photo_interval_minutes": setup.get("photo_interval_minutes"),
        }
        for setup in setups
    ]
    log_event(
        "loops.started",
        loops=["node_discovery", "readings_capture", "camera_discovery", "photo_capture"],
        setups=loop_setups,
    )
    for setup in loop_setups:
        log_event(
            "loop.setup",
            setup_id=setup["setup_id"],
            name=setup.get("name") or "",
            node_id=setup.get("node_id") or "",
            value_interval_minutes=setup.get("value_interval_minutes"),
            photo_interval_minutes=setup.get("photo_interval_minutes"),
        )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    _set_windows_keep_awake(False)
    for task_name in ("node_task", "readings_task", "camera_task", "photo_task"):
        task = getattr(app.state, task_name, None)
        if task:
            task.cancel()
    close_connections()


@app.websocket("/api/live")
async def live_ws(ws: WebSocket) -> None:
    claims = await authenticate_ws(ws, {ROLE_VIEWER, ROLE_OPERATOR, ROLE_ADMIN})
    if not claims:
        return
    await ws.accept()
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("t")
            setup_id = data.get("setupId")
            if msg_type == "sub" and setup_id:
                await live_manager.subscribe(setup_id, ws)
            elif msg_type == "unsub" and setup_id:
                await live_manager.unsubscribe(setup_id, ws)
            else:
                await ws.send_json({"t": "error", "msg": "unknown message"})
    except Exception:
        await live_manager.remove_ws(ws)


@app.get(
    "/api/setups/{setup_id}/camera/stream",
    dependencies=[Depends(require_roles(ROLE_VIEWER, ROLE_OPERATOR, ROLE_ADMIN))],
)
async def camera_stream(setup_id: str) -> Any:
    return await stream_camera(setup_id)

@app.get(
    "/api/setups/{setup_id}/camera/snapshot",
    dependencies=[Depends(require_roles(ROLE_VIEWER, ROLE_OPERATOR, ROLE_ADMIN))],
)
async def camera_snapshot(setup_id: str) -> Any:
    return await snapshot_camera(setup_id)
