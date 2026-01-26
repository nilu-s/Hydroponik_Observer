from __future__ import annotations

import asyncio
import hashlib
import threading
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

from .config import CAMERA_SCAN_INTERVAL_SEC, log_event
from .db import list_cameras, mark_cameras_offline, upsert_camera
from .worker_client import list_worker_devices


@dataclass(frozen=True)
class CameraBinding:
    device_id: str
    friendly_name: Optional[str]
    pnp_device_id: Optional[str]
    container_id: Optional[str]


CAMERA_REGISTRY: dict[str, CameraBinding] = {}
CAMERA_REGISTRY_LOCK = threading.Lock()


def _camera_id_from_device_id(device_id: str) -> str:
    digest = hashlib.md5(device_id.encode("utf-8")).hexdigest()[:12]
    return f"CAM_{digest}"


def _get_camera_binding(camera_id: str) -> Optional[CameraBinding]:
    with CAMERA_REGISTRY_LOCK:
        return CAMERA_REGISTRY.get(camera_id)


def get_camera_device_id(camera_id: str) -> Optional[str]:
    binding = _get_camera_binding(camera_id)
    return binding.device_id if binding else None


def _scan_cameras_once() -> set[str]:
    active_ids: set[str] = set()
    existing = list_cameras(online_only=False)
    by_device_id = {row.get("device_id"): row["camera_id"] for row in existing if row.get("device_id")}
    by_friendly_name: dict[str, str] = {}
    friendly_name_counts: dict[str, int] = {}
    for row in existing:
        name = row.get("friendly_name")
        if not name:
            continue
        friendly_name_counts[name] = friendly_name_counts.get(name, 0) + 1
        if name not in by_friendly_name:
            by_friendly_name[name] = row["camera_id"]

    try:
        devices = list_worker_devices()
    except Exception as exc:
        log_event("camera.discovery_failed", error=str(exc))
        refresh_camera_registry()
        return active_ids

    for device in devices:
        camera_id = by_device_id.get(device.device_id)
        if not camera_id:
            name = device.friendly_name or ""
            if name and friendly_name_counts.get(name, 0) == 1:
                camera_id = by_friendly_name.get(name)
        camera_id = camera_id or _camera_id_from_device_id(device.device_id)
        active_ids.add(camera_id)
        upsert_camera(
            camera_id=camera_id,
            device_id=device.device_id,
            friendly_name=device.friendly_name,
            pnp_device_id=None,
            container_id=None,
            status="online",
            last_error=None,
        )
        log_event(
            "camera.discovery_seen",
            camera_id=camera_id,
            device_id=device.device_id,
            friendly_name=device.friendly_name,
        )

    mark_cameras_offline(active_ids)
    refresh_camera_registry()
    return active_ids


async def camera_discovery_loop(
    on_update: Optional[Callable[[list[dict]], Awaitable[None]]] = None,
) -> None:
    last_payload: Optional[list[dict]] = None
    while True:
        await asyncio.to_thread(_scan_cameras_once)
        if on_update:
            devices = [
                {
                    "cameraId": row.get("camera_id"),
                    "deviceId": row.get("device_id"),
                    "pnpDeviceId": row.get("pnp_device_id"),
                    "containerId": row.get("container_id"),
                    "friendlyName": row.get("friendly_name"),
                    "status": row.get("status"),
                }
                for row in list_cameras(online_only=False)
                if row.get("device_id")
            ]
            if devices != last_payload:
                await on_update(devices)
                last_payload = devices
        await asyncio.sleep(CAMERA_SCAN_INTERVAL_SEC)


def scan_cameras_once() -> set[str]:
    return _scan_cameras_once()


def refresh_camera_registry() -> None:
    with CAMERA_REGISTRY_LOCK:
        CAMERA_REGISTRY.clear()
        for cam in list_cameras(online_only=True):
            device_id = cam.get("device_id")
            if not device_id:
                continue
            CAMERA_REGISTRY[cam["camera_id"]] = CameraBinding(
                device_id=device_id,
                friendly_name=cam.get("friendly_name"),
                pnp_device_id=cam.get("pnp_device_id"),
                container_id=cam.get("container_id"),
            )
