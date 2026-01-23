from __future__ import annotations

import asyncio
from typing import Any, Optional

from fastapi import HTTPException

from .db import get_setup
from .nodes import get_dummy_reading, get_node_client


async def _request_node_reading(setup_id: str, node_id: Optional[str]) -> dict[str, Any]:
    if not node_id:
        raise HTTPException(status_code=409, detail="no node assigned")
    if node_id == "DUMMY":
        return get_dummy_reading(setup_id)
    client = get_node_client(node_id)
    if not client:
        raise HTTPException(status_code=503, detail="node offline")
    try:
        return await asyncio.to_thread(client.request_all)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"node error: {exc}")


async def fetch_setup_reading(setup_id: str) -> tuple[str, dict[str, Any]]:
    setup = get_setup(setup_id)
    if not setup:
        raise HTTPException(status_code=404, detail="setup not found")
    node_id = setup.get("node_id")
    reading = await _request_node_reading(setup_id, node_id)
    return node_id, reading


async def fetch_node_reading(setup_id: str, node_id: Optional[str]) -> dict[str, Any]:
    return await _request_node_reading(setup_id, node_id)
