from __future__ import annotations

import time
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import csv
import io
import tempfile
import zipfile
from datetime import datetime

from .cameras import refresh_camera_registry, scan_cameras_once
from .db import (
    create_setup,
    delete_camera,
    delete_setup,
    delete_node,
    delete_calibration,
    delete_photos_by_setup,
    delete_readings_by_setup,
    get_camera,
    get_setup,
    get_node,
    init_db,
    insert_reading,
    list_cameras,
    list_nodes,
    list_all_photos,
    list_all_readings,
    list_photo_paths_by_setup,
    list_photos,
    list_readings,
    list_setups,
    update_setup,
    upsert_node,
    encode_cap_json,
    update_node_name,
)
from .log_events import log_event
from .config import PHOTOS_DIR
from .models import NodeCommandRequest, NodeUpdate, SetupCreate, SetupUpdate
from .nodes import ensure_dummy_node, get_dummy_reading, get_node_client
from .readings import fetch_setup_reading
from .stream import capture_photo_now


router = APIRouter(prefix="/api")


def _write_csv_to_zip(
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


def _delete_setup_assets(setup_id: str) -> int:
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
    deleted_photos = _delete_setup_assets(setup_id)
    delete_setup(setup_id)
    return {"ok": True, "deleted": True, "deletedPhotos": deleted_photos}


@router.get("/nodes")
def get_nodes() -> list[dict]:
    ensure_dummy_node()
    rows = list_nodes()
    return [
        {
            "nodeId": row["node_id"],
            "name": row.get("name"),
            "kind": row["kind"],
            "fw": row["fw"],
            "capJson": row["cap_json"],
            "mode": row.get("mode"),
            "lastSeenAt": row["last_seen_at"],
            "status": row["status"],
            "lastError": row["last_error"],
        }
        for row in rows
    ]


@router.delete("/nodes/{node_id}")
def delete_node_route(node_id: str) -> dict:
    if node_id == "DUMMY":
        raise HTTPException(status_code=409, detail="cannot delete dummy node")
    node = get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="node not found")
    setups = [row for row in list_setups() if row.get("node_id") == node_id]
    deleted_photos = 0
    for setup in setups:
        setup_id = setup["setup_id"]
        deleted_photos += _delete_setup_assets(setup_id)
        update_setup(setup_id, {"nodeId": None})
    delete_calibration(node_id)
    delete_node(node_id)
    log_event(
        "node.deleted",
        node_id=node_id,
        affected_setups=len(setups),
        deleted_photos=deleted_photos,
    )
    return {
        "ok": True,
        "affectedSetups": len(setups),
        "deletedPhotos": deleted_photos,
    }


@router.post("/nodes/{node_id}/command")
def post_node_command(node_id: str, payload: NodeCommandRequest) -> dict:
    if node_id == "DUMMY":
        if payload.t == "get_all":
            return get_dummy_reading(node_id)
        return {"ok": True, "note": "dummy node"}
    client = get_node_client(node_id)
    if not client:
        raise HTTPException(status_code=503, detail="node offline")

    if payload.t == "hello":
        return client.send_command({"t": "hello", "proto": 1}, expect_response=True)
    if payload.t == "get_all":
        return client.send_command({"t": "get_all"}, expect_response=True)
    if payload.t == "set_mode":
        if payload.mode not in ("real", "debug"):
            raise HTTPException(status_code=400, detail="invalid mode")
        client.send_command(
            {"t": "set_mode", "mode": payload.mode},
            expect_response=False,
        )
        upsert_node(
            node_id=node_id,
            name=None,
            kind="real",
            fw=client.hello.fw,
            cap_json=encode_cap_json(client.hello.cap),
            mode=payload.mode,
            status="online",
            last_error=None,
        )
        return {"ok": True}
    if payload.t == "set_sim":
        if payload.simPh is None and payload.simEc is None and payload.simTemp is None:
            raise HTTPException(status_code=400, detail="missing sim values")
        message = {"t": "set_sim"}
        if payload.simPh is not None:
            message["ph"] = payload.simPh
        if payload.simEc is not None:
            message["ec"] = payload.simEc
        if payload.simTemp is not None:
            message["temp"] = payload.simTemp
        return client.send_command(message, expect_response=False)

    raise HTTPException(status_code=400, detail="unknown command")


@router.get("/cameras/devices")
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


@router.delete("/cameras/{camera_id}")
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


@router.post("/admin/reset-db")
def reset_db(token: str = Header("", alias="X-Reset-Token")) -> dict:
    if token != "reset123":
        raise HTTPException(status_code=401, detail="unauthorized")
    init_db(reset=True)
    log_event("db.reset")
    return {"ok": True}


@router.patch("/nodes/{node_id}")
def patch_node(node_id: str, payload: NodeUpdate) -> dict:
    if node_id == "DUMMY":
        raise HTTPException(status_code=409, detail="cannot rename dummy node")
    node = get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="node not found")
    updated = update_node_name(node_id, payload.name) or node
    return {
        "nodeId": updated["node_id"],
        "name": updated.get("name"),
        "kind": updated["kind"],
        "fw": updated["fw"],
        "capJson": updated["cap_json"],
        "mode": updated.get("mode"),
        "lastSeenAt": updated["last_seen_at"],
        "status": updated["status"],
        "lastError": updated["last_error"],
    }


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
            _write_csv_to_zip(
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
