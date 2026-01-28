from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from starlette.responses import Response, StreamingResponse

from .config import (
    DEFAULT_PHOTO_INTERVAL_MINUTES,
    PHOTOS_DIR,
    POLL_INTERVALS,
    log_event,
)
from .camera_worker_manager import get_camera_worker_manager
from .db import get_camera, get_setup, list_setups
from .security import resolve_under, validate_identifier
from .scheduler import run_periodic


async def stream_camera(setup_id: str) -> StreamingResponse:
    camera = _get_camera_for_setup(setup_id)
    device_id = _get_camera_device_id(camera)
    manager = get_camera_worker_manager()
    queue = await manager.subscribe(device_id)

    async def frame_generator():
        try:
            while True:
                frame_bytes = await queue.get()
                if frame_bytes is None:
                    break
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame_bytes
                    + b"\r\n"
                )
        finally:
            await manager.unsubscribe(device_id, queue)

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


async def snapshot_camera(setup_id: str) -> Response:
    camera = _get_camera_for_setup(setup_id)
    device_id = _get_camera_device_id(camera)
    frame_bytes = await get_camera_worker_manager().get_frame(device_id, timeout_sec=2.5)
    if frame_bytes is None:
        raise HTTPException(status_code=502, detail="camera frame unavailable")
    return Response(content=frame_bytes, media_type="image/jpeg")


async def capture_photo_now(setup_id: str, reason: str = "manual") -> dict:
    camera = _get_camera_for_setup(setup_id)
    device_id = _get_camera_device_id(camera)
    frame_bytes = await get_camera_worker_manager().get_frame(device_id, timeout_sec=2.5)
    if frame_bytes is None:
        raise HTTPException(status_code=502, detail="camera capture failed")
    result = _save_frame(setup_id, camera, frame_bytes)
    if not result:
        raise HTTPException(status_code=502, detail="camera capture failed")
    log_event("camera.capture", setup_id=setup_id, camera_id=camera["camera_id"], reason=reason)
    return {"ok": True, "photo": result}


async def photo_capture_loop() -> None:
    next_due_by_setup: dict[str, int] = {}

    async def work() -> None:
        now_ms = int(time.time() * 1000)
        for setup in list_setups():
            setup_id = setup["setup_id"]
            camera_id = setup.get("camera_id")
            if not camera_id:
                continue
            interval_minutes = setup.get("photo_interval_minutes")
            if interval_minutes is None:
                interval_minutes = DEFAULT_PHOTO_INTERVAL_MINUTES
            if interval_minutes <= 0:
                continue
            interval_ms = int(interval_minutes * 60 * 1000)
            if setup_id not in next_due_by_setup:
                next_due_by_setup[setup_id] = now_ms + interval_ms
                continue
            next_due = next_due_by_setup.get(setup_id, 0)
            if now_ms < next_due:
                continue
            try:
                await capture_photo_now(setup_id, reason="interval")
            except HTTPException:
                next_due = next_due + interval_ms
                if next_due <= now_ms:
                    next_due = now_ms + interval_ms
                next_due_by_setup[setup_id] = next_due
                continue
            next_due = next_due + interval_ms
            if next_due <= now_ms:
                next_due = now_ms + interval_ms
            next_due_by_setup[setup_id] = next_due

    await run_periodic(
        "photo_capture",
        lambda: POLL_INTERVALS.photo_capture_poll_sec,
        work,
        min_sleep_sec=0.2,
    )


def _get_camera_for_setup(setup_id: str) -> dict:
    validate_identifier(setup_id, "setup_id")
    setup = get_setup(setup_id)
    if not setup:
        raise HTTPException(status_code=404, detail="setup not found")
    camera_id = setup.get("camera_id")
    if not camera_id:
        raise HTTPException(status_code=404, detail="camera not assigned")
    camera = get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="camera not found")
    if camera.get("status") != "online":
        raise HTTPException(status_code=409, detail="camera offline")
    return camera


def reset_runtime() -> None:
    get_camera_worker_manager().reset_runtime()


def stop_workers_for_device(device_id: str) -> None:
    get_camera_worker_manager().stop_workers_for_device(device_id)


def _get_camera_device_id(camera: dict) -> str:
    device_id = camera.get("pnp_device_id")
    if not device_id:
        raise HTTPException(status_code=404, detail="camera device id missing")
    return device_id


def _save_frame(setup_id: str, camera: dict, frame_bytes: bytes) -> Optional[dict]:
    safe_setup_id = validate_identifier(setup_id, "setup_id")
    ts = int(time.time() * 1000)
    stamp = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d_%H-%M-%S")
    folder = resolve_under(PHOTOS_DIR, safe_setup_id)
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{safe_setup_id}_{stamp}.jpg"
    path = folder / filename
    path.write_bytes(frame_bytes)
    return {
        "ts": ts,
        "path": f"/data/photos/{safe_setup_id}/{filename}",
        "cameraId": camera.get("camera_id"),
    }
