from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..cameras import scan_cameras_once
from ..config import log_event
from ..db import delete_camera, get_camera, list_cameras, list_setups, update_setup

router = APIRouter(prefix="/cameras")


@router.get("/devices")
def list_camera_devices() -> list[dict]:
    scan_cameras_once()
    rows = list_cameras(online_only=False)
    return [
        {
            "cameraId": row.get("camera_id"),
            "deviceId": row.get("device_id"),
            "pnpDeviceId": row.get("pnp_device_id"),
            "containerId": row.get("container_id"),
            "friendlyName": row.get("friendly_name"),
            "status": row.get("status"),
        }
        for row in rows
        if row.get("device_id")
    ]


@router.delete("/{camera_id}")
def delete_camera_route(camera_id: str) -> dict:
    camera = get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="camera not found")
    setups = [row for row in list_setups() if row.get("camera_id") == camera_id]
    for setup in setups:
        update_setup(setup["setup_id"], {"cameraId": None})
    delete_camera(camera_id)
    log_event("camera.deleted", camera_id=camera_id, affected_setups=len(setups))
    return {"ok": True, "affectedSetups": len(setups)}
