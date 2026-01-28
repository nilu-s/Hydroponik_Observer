from __future__ import annotations

import re
import shutil
import time
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse

from ..camera_streaming import capture_photo_now, stop_workers_for_device
from ..config import DEFAULT_PHOTO_INTERVAL_MINUTES, DEFAULT_VALUE_INTERVAL_MINUTES, PHOTOS_DIR
from ..db import (
    create_setup,
    delete_setup,
    delete_readings_by_setup,
    get_camera,
    get_setup,
    insert_reading,
    iter_readings,
    list_readings,
    list_setups,
    update_setup,
)
from ..models import SetupCreate, SetupUpdate
from ..nodes import fetch_setup_reading
from ..security import ROLE_ADMIN, ROLE_OPERATOR, resolve_under, require_roles, validate_identifier
from ..utils.csv_export import write_csv_to_zip_stream
from ..utils.datetime_utils import iter_readings_with_iso

router = APIRouter()


@router.get("/setups")
def get_setups() -> list[dict]:
    return [
        {
            "setupId": row["setup_id"],
            "name": row["name"],
            "port": row["node_id"],
            "cameraPort": row.get("camera_id"),
            "valueIntervalMinutes": row.get("value_interval_minutes")
            or DEFAULT_VALUE_INTERVAL_MINUTES,
            "photoIntervalMinutes": row.get("photo_interval_minutes")
            or DEFAULT_PHOTO_INTERVAL_MINUTES,
            "createdAt": row["created_at"],
        }
        for row in list_setups()
    ]


@router.post("/setups", dependencies=[Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))])
def post_setup(payload: SetupCreate) -> dict:
    row = create_setup(payload.name)
    return {
        "setupId": row["setup_id"],
        "name": row["name"],
        "port": row["node_id"],
        "cameraPort": row.get("camera_id"),
        "valueIntervalMinutes": row.get("value_interval_minutes")
        or DEFAULT_VALUE_INTERVAL_MINUTES,
        "photoIntervalMinutes": row.get("photo_interval_minutes")
        or DEFAULT_PHOTO_INTERVAL_MINUTES,
        "createdAt": row["created_at"],
    }


@router.patch("/setups/{setup_id}", dependencies=[Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))])
def patch_setup(setup_id: str, payload: SetupUpdate) -> dict:
    updates = payload.model_dump(exclude_unset=True)
    if "cameraPort" in updates:
        camera_id = updates.get("cameraPort") or None
        updates["cameraPort"] = camera_id
        if camera_id and not get_camera(camera_id):
            raise HTTPException(status_code=400, detail="camera not found")
    row = update_setup(setup_id, updates)
    if not row:
        raise HTTPException(status_code=404, detail="setup not found")
    return {
        "setupId": row["setup_id"],
        "name": row["name"],
        "port": row["node_id"],
        "cameraPort": row.get("camera_id"),
        "valueIntervalMinutes": row.get("value_interval_minutes")
        or DEFAULT_VALUE_INTERVAL_MINUTES,
        "photoIntervalMinutes": row.get("photo_interval_minutes")
        or DEFAULT_PHOTO_INTERVAL_MINUTES,
        "createdAt": row["created_at"],
    }


@router.delete("/setups/{setup_id}", dependencies=[Depends(require_roles(ROLE_ADMIN))])
def delete_setup_route(setup_id: str) -> dict:
    setup = get_setup(setup_id)
    if not setup:
        return {"ok": True, "deleted": False}
    camera_id = setup.get("camera_id")
    if camera_id:
        still_used = any(
            row.get("camera_id") == camera_id and row.get("setup_id") != setup_id
            for row in list_setups()
        )
        if not still_used:
            camera = get_camera(camera_id)
            if camera and camera.get("pnp_device_id"):
                stop_workers_for_device(camera["pnp_device_id"])
    deleted_photos = delete_setup_assets(setup_id)
    delete_setup(setup_id)
    return {"ok": True, "deleted": True, "deletedPhotos": deleted_photos}


@router.get("/setups/{setup_id}/reading")
async def get_reading(setup_id: str) -> dict:
    _, reading = await fetch_setup_reading(setup_id)
    return reading


@router.post(
    "/setups/{setup_id}/capture-reading",
    dependencies=[Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))],
)
async def capture_reading(setup_id: str) -> dict:
    node_id, reading = await fetch_setup_reading(setup_id)
    ts = int(reading.get("ts") or time.time() * 1000)
    insert_reading(
        setup_id=setup_id,
        node_id=node_id,
        ts=ts,
        ph=reading.get("ph"),
        ec=reading.get("ec"),
        temp=reading.get("temp"),
        status=reading.get("status"),
    )
    reading["ts"] = ts
    return reading


@router.post(
    "/setups/{setup_id}/capture-photo",
    dependencies=[Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))],
)
async def capture_photo(setup_id: str) -> dict:
    return await capture_photo_now(setup_id)


@router.get("/setups/{setup_id}/history")
def get_history(setup_id: str, limit: int = 200) -> dict:
    setup = get_setup(setup_id)
    if not setup:
        raise HTTPException(status_code=404, detail="setup not found")
    readings = list_readings(setup_id, limit=limit)
    photos = _list_photos(setup_id, setup.get("camera_id"))
    return {"readings": readings, "photos": photos}


@router.get("/export/all", dependencies=[Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))])
def export_all(background_tasks: BackgroundTasks) -> FileResponse:
    setups = list_setups()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    temp_path = Path(temp.name)
    temp.close()

    with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for setup in setups:
            setup_id = setup["setup_id"]
            setup_name = setup.get("name") or setup_id
            readings = iter_readings_with_iso(iter_readings(setup_id))
            write_csv_to_zip_stream(
                zf,
                f"setups/{setup_id}/readings.csv",
                readings,
                ["id", "setup_id", "node_id", "ts_iso", "ph", "ec", "temp", "status_json"],
            )
            zf.writestr(f"setups/{setup_id}/meta.txt", f"name={setup_name}\n")

    background_tasks.add_task(temp_path.unlink, missing_ok=True)
    return FileResponse(
        temp_path,
        filename="sensorhub-export.zip",
        media_type="application/zip",
    )


def delete_setup_assets(setup_id: str) -> int:
    delete_readings_by_setup(setup_id)
    safe_setup_id = validate_identifier(setup_id, "setup_id")
    photos_dir = resolve_under(PHOTOS_DIR, safe_setup_id)
    deleted = 0
    if photos_dir.exists():
        deleted = sum(1 for entry in photos_dir.iterdir() if entry.is_file())
        shutil.rmtree(photos_dir, ignore_errors=True)
    return deleted


def _list_photos(setup_id: str, camera_id: str | None) -> list[dict]:
    safe_setup_id = validate_identifier(setup_id, "setup_id")
    folder = resolve_under(PHOTOS_DIR, safe_setup_id)
    if not folder.exists():
        return []
    pattern_new = re.compile(
        rf"^{re.escape(safe_setup_id)}_\d{{4}}-\d{{2}}-\d{{2}}_\d{{2}}-\d{{2}}-\d{{2}}\.jpg$",
        re.IGNORECASE,
    )
    pattern_old = re.compile(rf"^{re.escape(safe_setup_id)}_(\d+)\.jpg$", re.IGNORECASE)
    photos: list[dict] = []
    for entry in folder.iterdir():
        if not entry.is_file():
            continue
        match = pattern_new.match(entry.name) or pattern_old.match(entry.name)
        if not match:
            continue
        if match.re is pattern_old:
            ts = int(match.group(1))
        else:
            try:
                ts = int(entry.stat().st_mtime * 1000)
            except OSError:
                ts = 0
        photos.append(
            {
                "id": ts,
                "setup_id": safe_setup_id,
                "camera_id": camera_id or "",
                "ts": ts,
                "path": f"/data/photos/{safe_setup_id}/{entry.name}",
            }
        )
    return sorted(photos, key=lambda item: item["ts"])
