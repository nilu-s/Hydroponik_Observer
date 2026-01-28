from __future__ import annotations

import asyncio
import platform
from typing import Any

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .api import router as api_router
from .config import DATA_DIR, ensure_dirs, log_event
from .db import init_db, list_setups
from .realtime_updates import LiveManager, readings_capture_loop, register_live_manager as register_ws_manager
from .nodes import node_discovery_loop
from .camera_devices import camera_discovery_loop, register_live_manager
from .camera_streaming import photo_capture_loop, snapshot_camera, stream_camera


app = FastAPI(title="Sensorhub Backend Prototype")
ensure_dirs()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            "value_interval_sec": setup.get("value_interval_sec"),
            "photo_interval_sec": setup.get("photo_interval_sec"),
        }
        for setup in setups
    ]
    log_event(
        "loops.started",
        loops=["node_discovery", "readings_capture", "camera_discovery", "photo_capture"],
        setups=loop_setups,
    )
    print("loops.started: node_discovery, readings_capture, camera_discovery, photo_capture")
    for setup in loop_setups:
        print(
            "loop.setup:"
            f" setup_id={setup['setup_id']}"
            f" name={setup.get('name') or ''}"
            f" node_id={setup.get('node_id') or ''}"
            f" value_interval_sec={setup.get('value_interval_sec')}"
            f" photo_interval_sec={setup.get('photo_interval_sec')}"
        )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    _set_windows_keep_awake(False)
    for task_name in ("node_task", "readings_task", "camera_task", "photo_task"):
        task = getattr(app.state, task_name, None)
        if task:
            task.cancel()


@app.websocket("/api/live")
async def live_ws(ws: WebSocket) -> None:
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


@app.get("/api/setups/{setup_id}/camera/stream")
async def camera_stream(setup_id: str) -> Any:
    return await stream_camera(setup_id)

@app.get("/api/setups/{setup_id}/camera/snapshot")
async def camera_snapshot(setup_id: str) -> Any:
    return await snapshot_camera(setup_id)


@app.get("/api/setups/{setup_id}/camera/snapshot")
async def camera_snapshot(setup_id: str) -> Any:
    return await snapshot_camera(setup_id)
