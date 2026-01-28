from __future__ import annotations

import asyncio
import subprocess
import time
from pathlib import Path
from typing import Optional

from fastapi import HTTPException
from starlette.responses import Response, StreamingResponse

from .config import (
    CAMERA_WORKER_CANDIDATES,
    CAMERA_WORKER_PATH,
    DEFAULT_PHOTO_INTERVAL_MINUTES,
    PHOTOS_DIR,
    log_event,
)
from .db import get_camera, get_setup, list_setups

WORKER_MAGIC = b"FRAM"
WORKER_HEADER_LEN = 32
WORKER_VERSION = 1
ACTIVE_WORKERS: dict[str, set[subprocess.Popen[bytes]]] = {}


async def stream_camera(setup_id: str) -> StreamingResponse:
    camera = _get_camera_for_setup(setup_id)
    process = _open_worker_process(camera)

    async def frame_generator():
        try:
            while True:
                frame_bytes = await asyncio.to_thread(_read_worker_frame_bytes, process)
                if frame_bytes is None:
                    break
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame_bytes
                    + b"\r\n"
                )
        finally:
            _stop_worker_process(process)

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


async def snapshot_camera(setup_id: str) -> Response:
    camera = _get_camera_for_setup(setup_id)
    frame_bytes = await asyncio.to_thread(_capture_single_frame, camera)
    if frame_bytes is None:
        raise HTTPException(status_code=502, detail="camera frame unavailable")
    return Response(content=frame_bytes, media_type="image/jpeg")


async def capture_photo_now(setup_id: str, reason: str = "manual") -> dict:
    camera = _get_camera_for_setup(setup_id)
    result = await asyncio.to_thread(_capture_and_save, setup_id, camera)
    if not result:
        raise HTTPException(status_code=502, detail="camera capture failed")
    log_event("camera.capture", setup_id=setup_id, camera_id=camera["camera_id"], reason=reason)
    return {"ok": True, "photo": result}


async def photo_capture_loop() -> None:
    last_capture_by_setup: dict[str, int] = {}
    while True:
        now_ms = int(time.time() * 1000)
        for setup in list_setups():
            setup_id = setup["setup_id"]
            camera_id = setup.get("camera_id")
            if not camera_id:
                continue
            interval_minutes = setup.get("photo_interval_sec") or DEFAULT_PHOTO_INTERVAL_MINUTES
            last_capture_ts = last_capture_by_setup.get(setup_id, 0)
            if (now_ms - last_capture_ts) < interval_minutes * 60 * 1000:
                continue
            try:
                await capture_photo_now(setup_id, reason="interval")
                last_capture_by_setup[setup_id] = now_ms
            except HTTPException:
                continue
        await asyncio.sleep(1)


def _get_camera_for_setup(setup_id: str) -> dict:
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


def _open_worker_process(camera: dict) -> subprocess.Popen[bytes]:
    device_id = camera.get("pnp_device_id")
    if not device_id:
        raise HTTPException(status_code=404, detail="camera device id missing")
    command = _resolve_worker_command()
    if not command:
        raise HTTPException(status_code=503, detail="camera worker unavailable")
    log_event("camera.worker_start", device_id=device_id)
    print(f"camera.worker_start: device_id={device_id}")
    try:
        process = subprocess.Popen(
            command + ["--device", device_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        ACTIVE_WORKERS.setdefault(device_id, set()).add(process)
        return process
    except Exception as exc:
        log_event("camera.worker_spawn_failed", error=str(exc))
        raise HTTPException(status_code=503, detail="camera worker failed to start") from exc


def _stop_worker_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=1)
        except Exception:
            process.kill()
    for device_id, processes in list(ACTIVE_WORKERS.items()):
        if process in processes:
            processes.discard(process)
            if not processes:
                ACTIVE_WORKERS.pop(device_id, None)
            break


def reset_runtime() -> None:
    for device_id in list(ACTIVE_WORKERS.keys()):
        stop_workers_for_device(device_id)


def stop_workers_for_device(device_id: str) -> None:
    processes = ACTIVE_WORKERS.get(device_id, set())
    for process in list(processes):
        try:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=1)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass
        processes.discard(process)
    if not processes:
        ACTIVE_WORKERS.pop(device_id, None)


def _resolve_worker_command() -> Optional[list[str]]:
    if CAMERA_WORKER_PATH:
        path = Path(CAMERA_WORKER_PATH)
        if path.exists():
            return [str(path)]
        log_event("camera.worker_missing", path=str(path))
        return None
    for candidate in CAMERA_WORKER_CANDIDATES:
        if candidate.exists():
            return [str(candidate)]
        alt = candidate.with_name("camera_worker.exe")
        if alt.exists():
            return [str(alt)]
    log_event(
        "camera.worker_missing",
        path=";".join(str(candidate) for candidate in CAMERA_WORKER_CANDIDATES),
    )
    return None


def _read_worker_frame_bytes(process: subprocess.Popen[bytes]) -> Optional[bytes]:
    if process.stdout is None:
        return None
    header = _read_exact(process, WORKER_HEADER_LEN)
    if not header:
        _log_worker_stderr(process, event="camera.worker_stream_ended")
        print("camera.worker_stream_ended")
        return None
    if header[:4] != WORKER_MAGIC:
        log_event("camera.worker_bad_magic")
        print("camera.worker_bad_magic")
        return None
    version = int.from_bytes(header[4:6], "little")
    if version != WORKER_VERSION:
        log_event("camera.worker_bad_version", version=version)
        print(f"camera.worker_bad_version: {version}")
        return None
    header_len = int.from_bytes(header[6:8], "little")
    if header_len > WORKER_HEADER_LEN:
        _read_exact(process, header_len - WORKER_HEADER_LEN)
    device_len = int.from_bytes(header[24:26], "little")
    mime_len = int.from_bytes(header[26:28], "little")
    payload_len = int.from_bytes(header[28:32], "little")
    _read_exact(process, device_len)
    mime = _read_exact(process, mime_len)
    payload = _read_exact(process, payload_len)
    if not payload:
        _log_worker_stderr(process, event="camera.worker_empty_frame")
        print("camera.worker_empty_frame")
        return None
    if mime and mime != b"image/jpeg":
        log_event("camera.worker_unexpected_mime", mime=mime.decode(errors="ignore"))
        print(f"camera.worker_unexpected_mime: {mime.decode(errors='ignore')}")
    return payload


def _read_exact(process: subprocess.Popen[bytes], size: int) -> bytes:
    if size <= 0 or process.stdout is None:
        return b""
    buffer = bytearray()
    while len(buffer) < size:
        chunk = process.stdout.read(size - len(buffer))
        if not chunk:
            break
        buffer.extend(chunk)
    return bytes(buffer)


def _log_worker_stderr(process: subprocess.Popen[bytes], event: str) -> None:
    if process.stderr is None:
        log_event(event)
        return
    try:
        error = process.stderr.read().decode(errors="ignore").strip()
    except Exception:
        error = ""
    log_event(event, stderr=error)
    if error:
        print(f"{event}: {error}")


def _capture_single_frame(camera: dict) -> Optional[bytes]:
    process = _open_worker_process(camera)
    try:
        deadline = time.monotonic() + 2.5
        while time.monotonic() < deadline:
            frame = _read_worker_frame_bytes(process)
            if frame:
                return frame
            time.sleep(0.2)
        return None
    finally:
        _stop_worker_process(process)


def _capture_and_save(setup_id: str, camera: dict) -> Optional[dict]:
    frame_bytes = _capture_single_frame(camera)
    if frame_bytes is None:
        return None
    ts = int(time.time() * 1000)
    folder = PHOTOS_DIR / setup_id
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{setup_id}_{ts}.jpg"
    path = folder / filename
    path.write_bytes(frame_bytes)
    return {
        "ts": ts,
        "path": f"/data/photos/{setup_id}/{filename}",
        "cameraId": camera.get("camera_id"),
    }
