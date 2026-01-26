from __future__ import annotations

import csv
import io
import time
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from ..config import PHOTOS_DIR
from ..db import (
    create_setup,
    delete_setup,
    delete_photos_by_setup,
    delete_readings_by_setup,
    get_setup,
    insert_reading,
    list_all_photos,
    list_all_readings,
    list_photo_paths_by_setup,
    list_photos,
    list_readings,
    list_setups,
    update_setup,
)
from ..models import SetupCreate, SetupUpdate
from ..nodes import fetch_setup_reading
from ..camera_streaming import capture_photo_now

router = APIRouter()


@router.get("/setups")
def get_setups() -> list[dict]:
    return [
        {
            "setupId": row["setup_id"],
            "name": row["name"],
            "nodeId": row["node_id"],
            "cameraId": row["camera_id"],
            "valueIntervalSec": row["value_interval_sec"],
            "photoIntervalSec": row["photo_interval_sec"],
            "createdAt": row["created_at"],
        }
        for row in list_setups()
    ]


@router.post("/setups")
def post_setup(payload: SetupCreate) -> dict:
    row = create_setup(payload.name)
    return {
        "setupId": row["setup_id"],
        "name": row["name"],
        "nodeId": row["node_id"],
        "cameraId": row["camera_id"],
        "valueIntervalSec": row["value_interval_sec"],
        "photoIntervalSec": row["photo_interval_sec"],
        "createdAt": row["created_at"],
    }


@router.patch("/setups/{setup_id}")
def patch_setup(setup_id: str, payload: SetupUpdate) -> dict:
    updates = payload.model_dump(exclude_none=True)
    row = update_setup(setup_id, updates)
    if not row:
        raise HTTPException(status_code=404, detail="setup not found")
    return {
        "setupId": row["setup_id"],
        "name": row["name"],
        "nodeId": row["node_id"],
        "cameraId": row["camera_id"],
        "valueIntervalSec": row["value_interval_sec"],
        "photoIntervalSec": row["photo_interval_sec"],
        "createdAt": row["created_at"],
    }


@router.delete("/setups/{setup_id}")
def delete_setup_route(setup_id: str) -> dict:
    if not get_setup(setup_id):
        return {"ok": True, "deleted": False}
    deleted_photos = delete_setup_assets(setup_id)
    delete_setup(setup_id)
    return {"ok": True, "deleted": True, "deletedPhotos": deleted_photos}


@router.get("/setups/{setup_id}/reading")
async def get_reading(setup_id: str) -> dict:
    _, reading = await fetch_setup_reading(setup_id)
    return reading


@router.post("/setups/{setup_id}/capture-reading")
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


@router.post("/setups/{setup_id}/capture-photo")
async def capture_photo(setup_id: str) -> dict:
    return await capture_photo_now(setup_id)


@router.get("/setups/{setup_id}/history")
def get_history(setup_id: str, limit: int = 200) -> dict:
    setup = get_setup(setup_id)
    if not setup:
        raise HTTPException(status_code=404, detail="setup not found")
    readings = list_readings(setup_id, limit=limit)
    photos = list_photos(setup_id, limit=limit)
    return {"readings": readings, "photos": photos}


@router.get("/export/all")
def export_all(background_tasks: BackgroundTasks) -> FileResponse:
    setups = list_setups()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    temp_path = Path(temp.name)
    temp.close()

    with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for setup in setups:
            setup_id = setup["setup_id"]
            setup_name = setup.get("name") or setup_id
            readings = list_all_readings(setup_id)
            photos = list_all_photos(setup_id)
            for reading in readings:
                ts = reading.get("ts")
                reading["ts_iso"] = (
                    datetime.fromtimestamp(ts / 1000).isoformat(sep=" ", timespec="seconds")
                    if isinstance(ts, int)
                    else ""
                )
            write_csv_to_zip(
                zf,
                f"setups/{setup_id}/readings.csv",
                readings,
                ["id", "setup_id", "node_id", "ts_iso", "ph", "ec", "temp", "status_json"],
            )
            for photo in photos:
                path = Path(photo["path"])
                if path.exists():
                    zf.write(path, f"setups/{setup_id}/photos/{path.name}")
            zf.writestr(f"setups/{setup_id}/meta.txt", f"name={setup_name}\n")

    background_tasks.add_task(temp_path.unlink, missing_ok=True)
    return FileResponse(
        temp_path,
        filename="sensorhub-export.zip",
        media_type="application/zip",
    )


def write_csv_to_zip(
    zf: zipfile.ZipFile,
    name: str,
    rows: list[dict],
    headers: list[str],
) -> None:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key) for key in headers})
    zf.writestr(name, output.getvalue())


def delete_setup_assets(setup_id: str) -> int:
    paths = list_photo_paths_by_setup(setup_id)
    for path in paths:
        try:
            Path(path).unlink(missing_ok=True)
        except Exception:
            pass
    delete_photos_by_setup(setup_id)
    delete_readings_by_setup(setup_id)
    try:
        (PHOTOS_DIR / setup_id).rmdir()
    except Exception:
        pass
    return len(paths)
