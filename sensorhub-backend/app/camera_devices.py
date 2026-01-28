from __future__ import annotations

import asyncio
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

from .config import (
    CAMERA_WORKER_CANDIDATES,
    CAMERA_WORKER_PATH,
    CAMERA_WORKER_TIMEOUT_SEC,
    POLL_INTERVALS,
    log_event,
)
from .db import list_cameras, mark_cameras_offline, upsert_camera
from .realtime_updates import LiveManager
from .scheduler import run_periodic

CAMERA_CACHE: dict[str, dict[str, Any]] = {}
LIVE_MANAGER: Optional[LiveManager] = None


def register_live_manager(manager: LiveManager) -> None:
    global LIVE_MANAGER
    LIVE_MANAGER = manager


def reset_runtime() -> None:
    CAMERA_CACHE.clear()


def list_camera_devices() -> list[dict[str, Any]]:
    return [_build_camera_payload(row) for row in list_cameras()]


def get_camera_runtime(camera_id: str) -> Optional[dict[str, Any]]:
    return CAMERA_CACHE.get(camera_id)


async def broadcast_camera_devices() -> None:
    if not LIVE_MANAGER:
        return
    payload = {"t": "cameraDevices", "devices": list_camera_devices()}
    await LIVE_MANAGER.broadcast_all(payload)


async def camera_discovery_loop() -> None:
    last_payload: Optional[str] = None

    async def work() -> None:
        nonlocal last_payload
        devices = await asyncio.to_thread(_scan_camera_devices)
        active_ids: set[str] = set()
        for device in devices:
            active_ids.add(device["camera_id"])
            upsert_camera(
                camera_id=device["camera_id"],
                port=device["port"],
                alias=device["alias"],
                friendly_name=device.get("friendly_name"),
                pnp_device_id=device.get("pnp_device_id"),
                container_id=device.get("container_id"),
                status="online",
            )
        mark_cameras_offline(active_ids)
        _refresh_cache(devices)
        if LIVE_MANAGER:
            payload = {"t": "cameraDevices", "devices": list_camera_devices()}
            payload_json = json.dumps(payload, sort_keys=True)
            if payload_json != last_payload:
                await LIVE_MANAGER.broadcast_all(payload)
                last_payload = payload_json

    await run_periodic(
        "camera_discovery",
        lambda: POLL_INTERVALS.camera_scan_sec,
        work,
        min_sleep_sec=1,
    )


def _refresh_cache(devices: list[dict[str, Any]]) -> None:
    now = int(time.time() * 1000)
    CAMERA_CACHE.clear()
    for device in devices:
        cached = dict(device)
        cached["last_seen_at"] = now
        CAMERA_CACHE[device["camera_id"]] = cached


def _build_camera_payload(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "cameraId": row.get("camera_id"),
        "deviceId": row.get("camera_id"),
        "alias": row.get("alias"),
        "pnpDeviceId": row.get("pnp_device_id"),
        "containerId": row.get("container_id"),
        "friendlyName": row.get("friendly_name"),
        "status": row.get("status"),
    }


def _scan_camera_devices() -> list[dict[str, Any]]:
    devices = _scan_camera_devices_worker()
    usb_count = sum(1 for device in devices if device.get("port"))
    internal_count = len(devices) - usb_count
    log_event(
        "cameras.scan_result",
        source="worker",
        total=len(devices),
        usb=usb_count,
        internal=internal_count,
    )
    if not devices:
        log_event("cameras.scan_empty", source="worker")
    else:
        log_event(
            "cameras.scan_summary",
            source="worker",
            total=len(devices),
            usb=usb_count,
            internal=internal_count,
        )
    return devices


def _scan_camera_devices_worker() -> list[dict[str, Any]]:
    command = _resolve_worker_command()
    if not command:
        return []
    output = _run_worker(command + ["--list"])
    if not output:
        return []
    try:
        data = json.loads(output)
    except json.JSONDecodeError as exc:
        log_event("cameras.worker_bad_json", error=str(exc))
        return []
    if isinstance(data, dict):
        data = [data]
    devices: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in data:
        device_id = _first_value(item, "device_id", "deviceId")
        instance_id = _first_value(item, "instance_id", "instanceId")
        key = device_id or instance_id
        if not key or key in seen_ids:
            continue
        seen_ids.add(key)
        friendly_name = _first_value(item, "friendly_name", "friendlyName")
        port_id = _first_value(item, "port_id", "portId")
        is_integrated = _is_integrated_camera(friendly_name)
        port = None
        if not is_integrated:
            port = _extract_usb_port(port_id) or _extract_usb_port(instance_id)
        if port:
            camera_id = port
            auto_alias = f"Kamera {port.upper()}"
            port_value = port
        else:
            camera_id = _build_internal_id(key)
            auto_alias = f"Kamera INTERNAL {camera_id.split(':')[-1]}"
            port_value = ""
        devices.append(
            {
                "camera_id": camera_id,
                "port": port_value,
                "alias": auto_alias,
                "friendly_name": friendly_name,
                "pnp_device_id": device_id or instance_id,
                "container_id": None,
            }
        )
    return devices


def _resolve_worker_command() -> Optional[list[str]]:
    if CAMERA_WORKER_PATH:
        path = Path(CAMERA_WORKER_PATH)
        if path.exists():
            log_event("cameras.worker_path", path=str(path))
            return [str(path)]
        log_event("cameras.worker_missing", path=str(path))
        return None
    for candidate in CAMERA_WORKER_CANDIDATES:
        if candidate.exists():
            log_event("cameras.worker_found", path=str(candidate))
            return [str(candidate)]
        alt = candidate.with_name("camera_worker.exe")
        if alt.exists():
            log_event("cameras.worker_found", path=str(alt))
            return [str(alt)]
    log_event(
        "cameras.worker_missing",
        path=";".join(str(candidate) for candidate in CAMERA_WORKER_CANDIDATES),
    )
    return None


def _run_worker(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=CAMERA_WORKER_TIMEOUT_SEC,
        )
    except Exception as exc:
        log_event("cameras.worker_failed", error=str(exc))
        return ""
    if result.returncode != 0:
        log_event(
            "cameras.worker_error",
            code=result.returncode,
            stderr=result.stderr.strip(),
        )
        return ""
    if result.stderr.strip():
        log_event("cameras.worker_stderr", stderr=result.stderr.strip())
    return result.stdout.strip()


def _first_value(item: dict[str, Any], *keys: str) -> Optional[str]:
    for key in keys:
        value = item.get(key)
        if value:
            return str(value)
    return None


def _extract_usb_port(location_path: Optional[str]) -> Optional[str]:
    if not location_path:
        return None
    instance_match = re.search(r"USB\\VID_([0-9A-F]{4})&PID_([0-9A-F]{4})", location_path, flags=re.IGNORECASE)
    if instance_match:
        vid, pid = instance_match.group(1).lower(), instance_match.group(2).lower()
        return f"usb{vid}{pid}"
    match = re.search(r"Port_#(\\d+)", location_path, flags=re.IGNORECASE)
    if match:
        return f"usb{int(match.group(1))}"
    matches = re.findall(r"USB\\((\\d+)\\)", location_path, flags=re.IGNORECASE)
    if matches:
        return f"usb{matches[-1]}"
    return None


def _is_integrated_camera(friendly_name: Optional[str]) -> bool:
    if not friendly_name:
        return False
    normalized = friendly_name.lower()
    keywords = ("integrated", "integrierte", "built-in", "builtin", "internal")
    return any(keyword in normalized for keyword in keywords)


def _build_internal_id(instance_id: str) -> str:
    short_hash = hashlib.sha1(instance_id.encode("utf-8")).hexdigest()[:8]
    return f"internal:{short_hash}"
