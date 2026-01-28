from __future__ import annotations

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
            "port": row["node_id"],
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


@router.delete("/{port}", dependencies=[Depends(require_roles(ROLE_ADMIN))])
def delete_node_route(port: str) -> dict:
    node = get_node(port)
    if not node:
        raise HTTPException(status_code=404, detail="node not found")
    if get_node_client(port):
        remove_node_client(port)
    setups = [row for row in list_setups() if row.get("node_id") == port]
    deleted_photos = 0
    for setup in setups:
        setup_id = setup["setup_id"]
        deleted_photos += delete_setup_assets(setup_id)
        update_setup(setup_id, {"port": None})
    delete_calibration(port)
    delete_node(port)
    log_event(
        "node.deleted",
        node_id=port,
        affected_setups=len(setups),
        deleted_photos=deleted_photos,
    )
    return {
        "ok": True,
        "affectedSetups": len(setups),
        "deletedPhotos": deleted_photos,
    }


@router.post("/{port}/command", dependencies=[Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))])
def post_node_command(port: str, payload: NodeCommandRequest) -> dict:
    client = get_node_client(port)
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
            node_id=port,
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


@router.patch("/{port}", dependencies=[Depends(require_roles(ROLE_OPERATOR, ROLE_ADMIN))])
def patch_node(port: str, payload: NodeUpdate) -> dict:
    node = get_node(port)
    if not node:
        raise HTTPException(status_code=404, detail="node not found")
    updated = update_node_alias(port, payload.alias) or node
    return {
        "port": updated["node_id"],
        "alias": updated.get("name"),
        "kind": updated["kind"],
        "fw": updated["fw"],
        "capJson": updated["cap_json"],
        "mode": updated.get("mode"),
        "lastSeenAt": updated["last_seen_at"],
        "status": updated["status"],
        "lastError": updated["last_error"],
    }
