from __future__ import annotations

import asyncio
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import AsyncGenerator, Optional

from fastapi import HTTPException
from starlette.responses import Response, StreamingResponse

from .cameras import get_camera_device_id, refresh_camera_registry, scan_cameras_once
from .config import LIVE_MAX_FPS, LIVE_MIN_FPS, PHOTOS_DIR
STREAM_ERROR_COOLDOWN_SEC = 2.0

from .db import get_camera, get_setup, insert_photo, list_cameras, list_setups, update_setup
from .log_events import log_event
from .worker_client import FramePacket, WorkerManager


def _safe_folder_name(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in name)
    cleaned = "-".join(filter(None, cleaned.split("-")))
    return cleaned[:40] if cleaned else "setup"


def _photo_filename(setup_name: str, ts_ms: int) -> str:
    safe_name = _safe_folder_name(setup_name)
    timestamp = datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d_%H-%M-%S")
    return f"{safe_name}__{timestamp}.jpg"


def _resolve_camera_device_id(camera_id: str, scan: bool) -> Optional[str]:
    device_id = get_camera_device_id(camera_id)
    if device_id is None:
        if scan:
            scan_cameras_once()
        refresh_camera_registry()
        device_id = get_camera_device_id(camera_id)
    return device_id


def _resolve_setup_camera(setup_id: str, camera_id: str, scan: bool) -> tuple[str, str]:
    device_id = _resolve_camera_device_id(camera_id, scan=scan)
    if device_id:
        return camera_id, device_id
    stored = get_camera(camera_id)
    friendly_name = stored.get("friendly_name") if stored else None
    if not friendly_name:
        raise HTTPException(status_code=503, detail="camera offline")
    candidates = [
        row
        for row in list_cameras(online_only=True)
        if row.get("friendly_name") == friendly_name
    ]
    if len(candidates) != 1:
        raise HTTPException(status_code=503, detail="camera offline")
    new_camera_id = candidates[0].get("camera_id")
    new_device_id = candidates[0].get("device_id")
    if not new_camera_id or not new_device_id:
        raise HTTPException(status_code=503, detail="camera offline")
    update_setup(setup_id, {"cameraId": new_camera_id})
    log_event(
        "camera.remapped",
        setup_id=setup_id,
        old_camera_id=camera_id,
        new_camera_id=new_camera_id,
        friendly_name=friendly_name,
    )
    return new_camera_id, new_device_id


async def _capture_and_store_photo(
    setup_id: str, setup_name: str, camera_id: str, device_id: str
) -> dict:
    state = await CAMERA_STREAMS.acquire(camera_id, device_id)
    try:
        if state.last_jpeg and (time.time() - state.last_ts) < 2.0:
            jpg = state.last_jpeg
        else:
            jpg = await _await_frame(state, timeout_sec=3.0)
        ts = int(time.time() * 1000)
        setup_dir = PHOTOS_DIR / setup_id
        setup_dir.mkdir(parents=True, exist_ok=True)
        path = setup_dir / _photo_filename(setup_name, ts)
        await asyncio.to_thread(path.write_bytes, jpg)
        insert_photo(setup_id, camera_id, ts, str(path))
        return {"ts": ts, "path": str(path), "cameraId": camera_id}
    finally:
        await CAMERA_STREAMS.release(camera_id)


@dataclass
class CameraStreamState:
    camera_id: str
    device_id: str
    ref_count: int = 0
    last_jpeg: Optional[bytes] = None
    last_error: Optional[str] = None
    last_error_ts: float = 0.0
    last_ts: float = 0.0
    event: asyncio.Event = field(default_factory=asyncio.Event)
    task: Optional[asyncio.Task[None]] = None
    idle_task: Optional[asyncio.Task[None]] = None
    warmup_remaining: int = 10
    stop: bool = False


class CameraStreamRegistry:
    def __init__(self, worker_manager: WorkerManager) -> None:
        self._states: dict[str, CameraStreamState] = {}
        self._lock = asyncio.Lock()
        self._worker_manager = worker_manager
        self._idle_seconds = 10.0

    async def acquire(self, camera_id: str, device_id: str) -> CameraStreamState:
        async with self._lock:
            state = self._states.get(camera_id)
            if not state:
                state = CameraStreamState(camera_id=camera_id, device_id=device_id)
                self._states[camera_id] = state
            if state.idle_task:
                state.idle_task.cancel()
                state.idle_task = None
            state.ref_count += 1
            if not state.task:
                state.stop = False
                state.warmup_remaining = 10
                state.task = asyncio.create_task(self._capture_loop(state))
            return state

    async def release(self, camera_id: str) -> None:
        async with self._lock:
            state = self._states.get(camera_id)
            if not state:
                return
            state.ref_count = max(0, state.ref_count - 1)
            if state.ref_count == 0:
                if not state.idle_task:
                    state.idle_task = asyncio.create_task(self._shutdown_after_idle(camera_id))

    async def get_state(self, camera_id: str) -> Optional[CameraStreamState]:
        async with self._lock:
            return self._states.get(camera_id)

    async def _shutdown_after_idle(self, camera_id: str) -> None:
        try:
            await asyncio.sleep(self._idle_seconds)
            async with self._lock:
                state = self._states.get(camera_id)
                if not state:
                    return
                if state.ref_count > 0:
                    state.idle_task = None
                    return
                state.stop = True
                if state.task:
                    state.task.cancel()
                self._states.pop(camera_id, None)
        except Exception:
            return

    async def _capture_loop(self, state: CameraStreamState) -> None:
        worker = await self._worker_manager.acquire(state.device_id)
        try:
            fps = max(LIVE_MIN_FPS, min(LIVE_MAX_FPS, 8))
            delay = 1.0 / fps
            while not state.stop:
                start = time.time()
                if worker.last_error:
                    state.last_error = worker.last_error
                    state.last_error_ts = time.time()
                    state.event.set()
                    await asyncio.sleep(0.2)
                    continue
                try:
                    packet = await asyncio.wait_for(worker.queue.get(), timeout=3.0)
                except asyncio.TimeoutError:
                    state.last_error = "camera timeout"
                    state.last_error_ts = time.time()
                    state.event.set()
                    continue
                if packet.device_id != state.device_id:
                    state.last_error = "device mismatch"
                    state.last_error_ts = time.time()
                    log_event(
                        "camera.mismatch",
                        camera_id=state.camera_id,
                        bound_device_id=state.device_id,
                        worker_device_id=packet.device_id,
                        frame_seq=packet.sequence,
                    )
                    state.event.set()
                    continue
                if state.warmup_remaining > 0:
                    state.warmup_remaining -= 1
                    continue
                state.last_error = None
                state.last_error_ts = 0.0
                state.last_jpeg = packet.payload
                state.last_ts = time.time()
                state.event.set()
                state.event = asyncio.Event()
                elapsed = time.time() - start
                if elapsed < delay:
                    await asyncio.sleep(delay - elapsed)
        except Exception as exc:
            state.last_error = f"camera error: {exc}"
            state.last_error_ts = time.time()
            state.event.set()
        finally:
            await self._worker_manager.release(state.device_id)


WORKER_MANAGER = WorkerManager()
CAMERA_STREAMS = CameraStreamRegistry(WORKER_MANAGER)


async def _await_frame(state: CameraStreamState, timeout_sec: float) -> bytes:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        wait_event = state.event
        try:
            await asyncio.wait_for(wait_event.wait(), timeout=deadline - time.time())
        except asyncio.TimeoutError:
            break
        if state.last_error:
            raise HTTPException(status_code=503, detail=state.last_error)
        if state.last_jpeg:
            return state.last_jpeg
    raise HTTPException(status_code=503, detail="camera capture failed")


async def _frame_generator(state: CameraStreamState) -> AsyncGenerator[bytes, None]:
    try:
        while True:
            wait_event = state.event
            await wait_event.wait()
            if state.last_error:
                break
            if not state.last_jpeg:
                continue
            yield b"--frame\r\n"
            yield b"Content-Type: image/jpeg\r\n\r\n"
            yield state.last_jpeg
            yield b"\r\n"
    finally:
        await CAMERA_STREAMS.release(state.camera_id)


async def stream_camera(setup_id: str) -> StreamingResponse:
    setup = get_setup(setup_id)
    if not setup:
        raise HTTPException(status_code=404, detail="setup not found")
    camera_id = setup.get("camera_id")
    if not camera_id:
        raise HTTPException(status_code=409, detail="no camera assigned")
    resolved_id, device_id = _resolve_setup_camera(setup_id, camera_id, scan=True)
    state = await CAMERA_STREAMS.acquire(resolved_id, device_id)
    if state.last_error and (time.time() - state.last_error_ts) < STREAM_ERROR_COOLDOWN_SEC:
        await CAMERA_STREAMS.release(camera_id)
        raise HTTPException(status_code=503, detail="camera cooling down")
    generator = _frame_generator(state)
    return StreamingResponse(generator, media_type="multipart/x-mixed-replace; boundary=frame")


async def snapshot_camera(setup_id: str) -> Response:
    setup = get_setup(setup_id)
    if not setup:
        raise HTTPException(status_code=404, detail="setup not found")
    camera_id = setup.get("camera_id")
    if not camera_id:
        raise HTTPException(status_code=409, detail="no camera assigned")
    resolved_id, device_id = _resolve_setup_camera(setup_id, camera_id, scan=True)
    state = await CAMERA_STREAMS.acquire(resolved_id, device_id)
    if state.last_error and (time.time() - state.last_error_ts) < STREAM_ERROR_COOLDOWN_SEC:
        await CAMERA_STREAMS.release(camera_id)
        raise HTTPException(status_code=503, detail="camera cooling down")
    try:
        if state.last_jpeg and (time.time() - state.last_ts) < 2.0:
            jpg = state.last_jpeg
        else:
            jpg = await _await_frame(state, timeout_sec=3.0)
        return Response(content=jpg, media_type="image/jpeg")
    finally:
        await CAMERA_STREAMS.release(camera_id)


async def capture_photo_now(setup_id: str) -> dict:
    setup = get_setup(setup_id)
    if not setup:
        raise HTTPException(status_code=404, detail="setup not found")
    camera_id = setup.get("camera_id")
    if not camera_id:
        raise HTTPException(status_code=409, detail="no camera assigned")
    camera_id, device_id = _resolve_setup_camera(setup_id, camera_id, scan=False)
    setup_name = setup.get("name") or setup_id
    return await _capture_and_store_photo(setup_id, setup_name, camera_id, device_id)


async def photo_capture_loop() -> None:
    last_capture: dict[str, int] = {}
    last_log_ts = 0
    while True:
        now_ms = int(time.time() * 1000)
        if now_ms - last_log_ts > 300000:
            setups = list_setups()
            active = sum(1 for setup in setups if setup.get("camera_id"))
            log_event("photo.loop_alive", total_setups=len(setups), active_setups=active)
            last_log_ts = now_ms
        for setup in list_setups():
            setup_id = setup["setup_id"]
            camera_id = setup.get("camera_id")
            if not camera_id:
                continue
            interval_sec = int(setup.get("photo_interval_sec") or 1800)
            interval_sec = max(60, min(86400, interval_sec))
            last_ts = last_capture.get(setup_id, 0)
            if (now_ms - last_ts) < interval_sec * 1000:
                continue
            try:
                camera_id, device_id = _resolve_setup_camera(setup_id, camera_id, scan=True)
                setup_name = setup.get("name") or setup_id
                await _capture_and_store_photo(setup_id, setup_name, camera_id, device_id)
                last_capture[setup_id] = now_ms
            except HTTPException:
                continue
        await asyncio.sleep(5)
