from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException

from ..config import log_event
from ..db import (
    delete_calibration,
    delete_node,
    encode_cap_json,
    get_node,
    list_nodes,
    list_setups,
    update_node_alias,
    update_setup,
    upsert_node,
)
from ..models import NodeCommandRequest, NodeUpdate
from ..nodes import get_node_client, list_serial_ports, remove_node_client
from .setups import delete_setup_assets
from ..security import ROLE_ADMIN, ROLE_OPERATOR, require_roles

router = APIRouter(prefix="/nodes")


@router.get("")
def get_nodes() -> list[dict]:
    rows = list_nodes()
    return [
        {
            "nodeId": row["node_id"],
            "port": (json.loads(row.get("status_json") or "{}") or {}).get("port"),
            "alias": row.get("name"),
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


@router.get("/ports")
def get_serial_ports() -> list[dict[str, str]]:
    return list_serial_ports()


@router.delete("/{uid}", dependencies=[Depends(require_roles(ROLE_ADMIN))])
def delete_node_route(uid: str) -> dict:
    node = get_node(uid)
    if not node:
        raise HTTPException(status_code=404, detail="node not found")
    if get_node_client(uid):
        remove_node_client(uid)
    setups = [row for row in list_setups() if row.get("node_id") == uid]
    deleted_photos = 0
    for setup in setups:
        setup_id = setup["setup_id"]
        deleted_photos += delete_setup_assets(setup_id)
        update_setup(setup_id, {"nodeId": None})
    delete_calibration(uid)
    delete_node(uid)
    log_event(
        "node.deleted",
        node_id=uid,
        affected_setups=len(setups),
        deleted_photos=deleted_photos,
    )
    return {
        "ok": True,
        "affectedSetups": len(setups),
        "deletedPhotos": deleted_photos,
    }


@router.post("/{uid}/command", dependencies=[Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))])
def post_node_command(uid: str, payload: NodeCommandRequest) -> dict:
    client = get_node_client(uid)
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
            node_id=uid,
            name=None,
            kind="real",
            fw=client.hello.fw,
            cap_json=encode_cap_json(client.hello.cap),
            mode=payload.mode,
            status="online",
            last_error=None,
            status_json=None,
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


@router.patch("/{uid}", dependencies=[Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))])
def patch_node(uid: str, payload: NodeUpdate) -> dict:
    node = get_node(uid)
    if not node:
        raise HTTPException(status_code=404, detail="node not found")
    updated = update_node_alias(uid, payload.alias) or node
    status = json.loads(updated.get("status_json") or "{}") if updated else {}
    return {
        "nodeId": updated["node_id"],
        "port": status.get("port"),
        "alias": updated.get("name"),
        "kind": updated["kind"],
        "fw": updated["fw"],
        "capJson": updated["cap_json"],
        "mode": updated.get("mode"),
        "lastSeenAt": updated["last_seen_at"],
        "status": updated["status"],
        "lastError": updated["last_error"],
    }
