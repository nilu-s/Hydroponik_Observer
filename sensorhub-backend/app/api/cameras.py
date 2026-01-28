from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..camera_devices import broadcast_camera_devices, list_camera_devices
from ..db import delete_camera, get_camera, update_camera_alias
from ..models import CameraUpdate
from ..security import ROLE_ADMIN, ROLE_OPERATOR, require_roles

router = APIRouter(prefix="/cameras")


@router.get("/devices")
async def list_camera_devices_route() -> list[dict]:
    return list_camera_devices()


@router.delete("/{camera_id}", dependencies=[Depends(require_roles(ROLE_ADMIN))])
async def delete_camera_route(camera_id: str) -> dict:
    camera = get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="camera not found")
    delete_camera(camera_id)
    await broadcast_camera_devices()
    return {"ok": True}


@router.patch("/{camera_id}", dependencies=[Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))])
async def patch_camera(camera_id: str, payload: CameraUpdate) -> dict:
    camera = get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="camera not found")
    updated = update_camera_alias(camera_id, payload.alias)
    if not updated:
        raise HTTPException(status_code=404, detail="camera not found")
    await broadcast_camera_devices()
    devices = list_camera_devices()
    for device in devices:
        if device.get("cameraId") == camera_id:
            return device
    return {"cameraId": camera_id, "alias": payload.alias}
