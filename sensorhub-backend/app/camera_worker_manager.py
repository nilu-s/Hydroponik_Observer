from __future__ import annotations

import asyncio
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from fastapi import HTTPException

from .config import (
    CAMERA_WORKER_CANDIDATES,
    CAMERA_WORKER_MAX_PER_DEVICE,
    CAMERA_WORKER_MAX_TOTAL,
    CAMERA_WORKER_PATH,
    log_event,
)

WORKER_MAGIC = b"FRAM"
WORKER_HEADER_LEN = 32
WORKER_VERSION = 1


@dataclass
class WorkerState:
    device_id: str
    process: subprocess.Popen[bytes]
    task: asyncio.Task[None]
    subscribers: set[asyncio.Queue[Optional[bytes]]] = field(default_factory=set)
    last_access: float = field(default_factory=time.time)
    last_error: Optional[str] = None
    frames_sent: int = 0


class CameraWorkerManager:
    """Manages one camera worker per device and shared frame distribution."""
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()
        self._workers: dict[str, WorkerState] = {}

    async def subscribe(self, device_id: str) -> asyncio.Queue[Optional[bytes]]:
        async with self._async_lock:
            with self._lock:
                state = self._workers.get(device_id)
                if not state:
                    state = self._start_worker(device_id)
                queue: asyncio.Queue[Optional[bytes]] = asyncio.Queue(maxsize=1)
                state.subscribers.add(queue)
                state.last_access = time.time()
                return queue

    async def unsubscribe(self, device_id: str, queue: asyncio.Queue[Optional[bytes]]) -> None:
        state: Optional[WorkerState] = None
        async with self._async_lock:
            with self._lock:
                state = self._workers.get(device_id)
                if not state:
                    return
                state.subscribers.discard(queue)
                state.last_access = time.time()
                if state.subscribers:
                    return
                self._workers.pop(device_id, None)
        if state:
            self._stop_worker_state(state, reason="last-subscriber-left")

    async def get_frame(self, device_id: str, timeout_sec: float = 2.5) -> Optional[bytes]:
        queue = await self.subscribe(device_id)
        try:
            frame = await asyncio.wait_for(queue.get(), timeout=timeout_sec)
            return frame
        except asyncio.TimeoutError:
            return None
        finally:
            await self.unsubscribe(device_id, queue)

    def stop_workers_for_device(self, device_id: str) -> None:
        with self._lock:
            state = self._workers.pop(device_id, None)
        if state:
            self._stop_worker_state(state, reason="stop-device")

    def reset_runtime(self) -> None:
        with self._lock:
            states = list(self._workers.values())
            self._workers.clear()
        for state in states:
            self._stop_worker_state(state, reason="reset")

    def get_health(self) -> dict:
        with self._lock:
            workers = list(self._workers.values())
        details = [
            {
                "deviceId": state.device_id,
                "subscribers": len(state.subscribers),
                "framesSent": state.frames_sent,
                "lastAccess": int(state.last_access * 1000),
                "lastError": state.last_error,
            }
            for state in workers
        ]
        return {
            "workers": details,
            "workerCount": len(details),
            "subscriberCount": sum(item["subscribers"] for item in details),
        }

    def _start_worker(self, device_id: str) -> WorkerState:
        if self._count_workers() >= CAMERA_WORKER_MAX_TOTAL:
            log_event("camera.worker_limit_total", active=self._count_workers())
            raise HTTPException(status_code=429, detail="camera worker limit reached")
        if self._count_workers_for_device(device_id) >= CAMERA_WORKER_MAX_PER_DEVICE:
            log_event("camera.worker_limit_device", device_id=device_id, active=1)
            raise HTTPException(status_code=429, detail="camera worker limit reached")
        process = self._open_worker_process(device_id)
        task = asyncio.create_task(self._pump_frames(device_id, process))
        state = WorkerState(device_id=device_id, process=process, task=task)
        self._workers[device_id] = state
        return state

    def _count_workers(self) -> int:
        return len(self._workers)

    def _count_workers_for_device(self, device_id: str) -> int:
        return 1 if device_id in self._workers else 0

    def _open_worker_process(self, device_id: str) -> subprocess.Popen[bytes]:
        if not device_id:
            raise HTTPException(status_code=404, detail="camera device id missing")
        command = _resolve_worker_command()
        if not command:
            raise HTTPException(status_code=503, detail="camera worker unavailable")
        log_event("camera.worker_start", device_id=device_id)
        try:
            return subprocess.Popen(
                command + ["--device", device_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as exc:
            log_event("camera.worker_spawn_failed", error=str(exc))
            raise HTTPException(status_code=503, detail="camera worker failed to start") from exc

    async def _pump_frames(self, device_id: str, process: subprocess.Popen[bytes]) -> None:
        try:
            while True:
                frame = await asyncio.to_thread(_read_worker_frame_bytes, process)
                if frame is None:
                    self._set_worker_error(device_id, "frame unavailable")
                    await self._notify_end(device_id)
                    return
                await self._broadcast_frame(device_id, frame)
        except asyncio.CancelledError:
            await self._notify_end(device_id)
            raise
        except Exception as exc:
            self._set_worker_error(device_id, str(exc))
            await self._notify_end(device_id)

    async def _broadcast_frame(self, device_id: str, frame: bytes) -> None:
        with self._lock:
            state = self._workers.get(device_id)
            if not state:
                return
            subscribers = list(state.subscribers)
            state.last_access = time.time()
            state.frames_sent += 1
        for queue in subscribers:
            if queue.full():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            try:
                queue.put_nowait(frame)
            except asyncio.QueueFull:
                pass

    async def _notify_end(self, device_id: str) -> None:
        with self._lock:
            state = self._workers.get(device_id)
            if not state:
                return
            subscribers = list(state.subscribers)
        for queue in subscribers:
            try:
                queue.put_nowait(None)
            except asyncio.QueueFull:
                pass

    def _set_worker_error(self, device_id: str, error: str) -> None:
        with self._lock:
            state = self._workers.get(device_id)
            if state:
                state.last_error = error

    def _stop_worker_state(self, state: WorkerState, reason: str) -> None:
        log_event("camera.worker_stop", device_id=state.device_id, reason=reason)
        if not state.task.done():
            state.task.cancel()
        process = state.process
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=1)
            except Exception:
                process.kill()


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
        return None
    if header[:4] != WORKER_MAGIC:
        log_event("camera.worker_bad_magic")
        return None
    version = int.from_bytes(header[4:6], "little")
    if version != WORKER_VERSION:
        log_event("camera.worker_bad_version", version=version)
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
        return None
    if mime and mime != b"image/jpeg":
        log_event("camera.worker_unexpected_mime", mime=mime.decode(errors="ignore"))
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


_MANAGER: Optional[CameraWorkerManager] = None


def get_camera_worker_manager() -> CameraWorkerManager:
    global _MANAGER
    if not _MANAGER:
        _MANAGER = CameraWorkerManager()
    return _MANAGER
