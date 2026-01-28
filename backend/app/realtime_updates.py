from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Optional

from fastapi import HTTPException, WebSocket

from .config import DEFAULT_VALUE_INTERVAL_MINUTES, LIVE_POLL_INTERVAL_SEC
from .db import get_setup, insert_reading, list_setups
from .nodes import fetch_node_reading


async def _fetch_live_reading(setup_id: str, node_id: Optional[str]) -> Optional[dict[str, Any]]:
    try:
        return await fetch_node_reading(setup_id, node_id)
    except HTTPException:
        return None


def _build_reading_payload(setup_id: str, reading: dict[str, Any]) -> dict[str, Any]:
    return {
        "t": "reading",
        "setupId": setup_id,
        "ts": reading["ts"],
        "ph": reading["ph"],
        "ec": reading["ec"],
        "temp": reading["temp"],
        "status": reading.get("status", ["ok"]),
    }


LIVE_MANAGER: Optional["LiveManager"] = None


def register_live_manager(manager: "LiveManager") -> None:
    global LIVE_MANAGER
    LIVE_MANAGER = manager


async def broadcast_system_reset(reason: str) -> None:
    if LIVE_MANAGER:
        await LIVE_MANAGER.broadcast_all({"t": "reset", "reason": reason})


class LiveManager:
    def __init__(self) -> None:
        self._subscriptions: dict[str, set[WebSocket]] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, setup_id: str, ws: WebSocket) -> None:
        async with self._lock:
            self._subscriptions.setdefault(setup_id, set()).add(ws)
            if setup_id not in self._tasks:
                self._tasks[setup_id] = asyncio.create_task(self._poll_setup(setup_id))

    async def unsubscribe(self, setup_id: str, ws: WebSocket) -> None:
        async with self._lock:
            subscribers = self._subscriptions.get(setup_id)
            if subscribers and ws in subscribers:
                subscribers.remove(ws)
            if not subscribers:
                self._subscriptions.pop(setup_id, None)
                task = self._tasks.pop(setup_id, None)
                if task:
                    task.cancel()

    async def remove_ws(self, ws: WebSocket) -> None:
        async with self._lock:
            for setup_id, subscribers in list(self._subscriptions.items()):
                if ws in subscribers:
                    subscribers.remove(ws)
                if not subscribers:
                    self._subscriptions.pop(setup_id, None)
                    task = self._tasks.pop(setup_id, None)
                    if task:
                        task.cancel()

    async def _poll_setup(self, setup_id: str) -> None:
        while True:
            setup = get_setup(setup_id)
            if not setup:
                await self._broadcast(setup_id, {"t": "error", "setupId": setup_id, "msg": "setup missing"})
                await asyncio.sleep(2)
                continue
            node_id = setup.get("node_id")
            poll_interval_sec = max(1, int(LIVE_POLL_INTERVAL_SEC))
            reading = await _fetch_live_reading(setup_id, node_id)
            if reading:
                await self._broadcast(setup_id, _build_reading_payload(setup_id, reading))
            await asyncio.sleep(poll_interval_sec)

    async def _broadcast(self, setup_id: str, payload: dict[str, Any]) -> None:
        subscribers = self._subscriptions.get(setup_id, set())
        if not subscribers:
            return
        data = json.dumps(payload)
        for ws in list(subscribers):
            try:
                await ws.send_text(data)
            except Exception:
                await self.unsubscribe(setup_id, ws)

    async def broadcast_all(self, payload: dict[str, Any]) -> None:
        data = json.dumps(payload)
        for setup_id, subscribers in list(self._subscriptions.items()):
            for ws in list(subscribers):
                try:
                    await ws.send_text(data)
                except Exception:
                    await self.unsubscribe(setup_id, ws)


async def readings_capture_loop() -> None:
    next_due_by_setup: dict[str, int] = {}
    while True:
        now_ms = int(time.time() * 1000)
        for setup in list_setups():
            setup_id = setup["setup_id"]
            node_id = setup.get("node_id")
            if not node_id:
                continue
            interval_minutes = setup.get("value_interval_sec")
            if interval_minutes is None:
                interval_minutes = DEFAULT_VALUE_INTERVAL_MINUTES
            if interval_minutes <= 0:
                continue
            interval_ms = int(interval_minutes * 60 * 1000)
            if setup_id not in next_due_by_setup:
                next_due_by_setup[setup_id] = now_ms + interval_ms
                continue
            next_due = next_due_by_setup.get(setup_id, 0)
            if now_ms < next_due:
                continue
            reading = await _fetch_live_reading(setup_id, node_id)
            if reading:
                ts = int(reading.get("ts") or now_ms)
                insert_reading(
                    setup_id=setup_id,
                    node_id=node_id,
                    ts=ts,
                    ph=reading.get("ph"),
                    ec=reading.get("ec"),
                    temp=reading.get("temp"),
                    status=reading.get("status"),
                )
            next_due = next_due + interval_ms
            if next_due <= now_ms:
                next_due = now_ms + interval_ms
            next_due_by_setup[setup_id] = next_due
        await asyncio.sleep(1)
