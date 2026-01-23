from __future__ import annotations

import asyncio
import json
import struct
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .config import WORKER_PATH
from .log_events import log_event


HEADER_STRUCT = struct.Struct("<4sHHQQHHI")
MAGIC = b"FRAM"


@dataclass(frozen=True)
class WorkerDevice:
    device_id: str
    friendly_name: str


@dataclass
class FramePacket:
    device_id: str
    mime: str
    payload: bytes
    sequence: int
    timestamp_ms: int


def _resolve_worker_path() -> str:
    if WORKER_PATH and Path(WORKER_PATH).exists():
        return str(WORKER_PATH)
    return "camera_worker.exe"


def _build_worker_cmd(args: list[str]) -> list[str]:
    path = _resolve_worker_path()
    if path.lower().endswith(".dll"):
        return ["dotnet", path, *args]
    return [path, *args]


def list_worker_devices() -> list[WorkerDevice]:
    cmd = _build_worker_cmd(["--list"])
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "worker list failed")
    raw = result.stdout.strip()
    if not raw:
        return []
    payload = json.loads(raw)
    devices = []
    for entry in payload:
        devices.append(
            WorkerDevice(
                device_id=entry.get("device_id", ""),
                friendly_name=entry.get("friendly_name", ""),
            )
        )
    return devices


class CameraWorker:
    def __init__(self, device_id: str) -> None:
        self.device_id = device_id
        self.process: Optional[subprocess.Popen[bytes]] = None
        self.queue: asyncio.Queue[FramePacket] = asyncio.Queue(maxsize=2)
        self.last_error: Optional[str] = None
        self._task: Optional[asyncio.Task[None]] = None

    async def start(self) -> None:
        if self.process:
            return
        cmd = _build_worker_cmd(["--device", self.device_id])
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )
        self._task = asyncio.create_task(self._reader_loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
        if self.process:
            self.process.kill()
            self.process = None

    async def _reader_loop(self) -> None:
        assert self.process and self.process.stdout
        stdout = self.process.stdout
        try:
            while True:
                header = await asyncio.to_thread(stdout.read, HEADER_STRUCT.size)
                if not header:
                    raise RuntimeError("worker closed")
                magic, version, header_len, seq, ts, did_len, mime_len, payload_len = HEADER_STRUCT.unpack(
                    header
                )
                if magic != MAGIC or version != 1 or header_len != HEADER_STRUCT.size:
                    raise RuntimeError("invalid frame header")
                device_id = (await asyncio.to_thread(stdout.read, did_len)).decode("utf-8", "ignore")
                mime = (await asyncio.to_thread(stdout.read, mime_len)).decode("utf-8", "ignore")
                payload = await asyncio.to_thread(stdout.read, payload_len)
                if device_id != self.device_id:
                    self.last_error = "device mismatch"
                    log_event(
                        "camera.mismatch",
                        bound_device_id=self.device_id,
                        worker_device_id=device_id,
                        frame_seq=seq,
                    )
                    continue
                packet = FramePacket(
                    device_id=device_id,
                    mime=mime,
                    payload=payload,
                    sequence=seq,
                    timestamp_ms=ts,
                )
                if self.queue.full():
                    _ = self.queue.get_nowait()
                await self.queue.put(packet)
        except Exception as exc:
            self.last_error = str(exc)
            log_event("camera.worker_error", bound_device_id=self.device_id, last_error=self.last_error)
        finally:
            await self.stop()


class WorkerManager:
    def __init__(self) -> None:
        self._workers: dict[str, CameraWorker] = {}
        self._lock = asyncio.Lock()
        self._refs: dict[str, int] = {}

    async def acquire(self, device_id: str) -> CameraWorker:
        async with self._lock:
            worker = self._workers.get(device_id)
            if not worker:
                worker = CameraWorker(device_id)
                self._workers[device_id] = worker
                await worker.start()
            self._refs[device_id] = self._refs.get(device_id, 0) + 1
            return worker

    async def get_worker(self, device_id: str) -> Optional[CameraWorker]:
        async with self._lock:
            return self._workers.get(device_id)

    async def release(self, device_id: str) -> None:
        async with self._lock:
            count = self._refs.get(device_id, 0)
            if count <= 1:
                self._refs.pop(device_id, None)
                worker = self._workers.pop(device_id, None)
                if worker:
                    await worker.stop()
            else:
                self._refs[device_id] = count - 1
