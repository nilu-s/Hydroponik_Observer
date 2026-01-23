from __future__ import annotations

import asyncio
import json
import random
import time
from dataclasses import dataclass
from threading import Lock
from typing import Any, Optional

import serial
from serial.tools import list_ports

from .config import NODE_SCAN_INTERVAL_SEC, SERIAL_BAUDRATE, SERIAL_TIMEOUT_SEC
from .db import encode_cap_json, get_calibration, mark_nodes_offline, upsert_node


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class NodeHello:
    node_id: str
    fw: Optional[str]
    cap: Optional[dict[str, Any]]
    calib_hash: Optional[str]


class NodeClient:
    def __init__(self, port: str, hello: NodeHello) -> None:
        self.port = port
        self.hello = hello
        self._lock = Lock()
        self._serial = serial.Serial(
            port=self.port,
            baudrate=SERIAL_BAUDRATE,
            timeout=SERIAL_TIMEOUT_SEC,
        )

    def close(self) -> None:
        try:
            self._serial.close()
        except Exception:
            pass

    def request_all(self) -> dict[str, Any]:
        payload = {"t": "get_all"}
        data = self.send_command(payload, expect_response=True)
        if data.get("t") != "all":
            raise RuntimeError("unexpected response")
        return data

    def sync_calibration(self) -> None:
        calib = get_calibration(self.hello.node_id)
        if not calib:
            return
        if calib["calib_hash"] == self.hello.calib_hash:
            return
        payload = {
            "t": "set_calib",
            "version": calib["calib_version"],
            "payload": json.loads(calib["payload_json"]),
        }
        data = self.send_command(payload, expect_response=True)
        if data.get("t") != "set_calib_ack":
            raise RuntimeError("calibration ack missing")

    def send_command(
        self,
        payload: dict[str, Any],
        expect_response: bool = True,
    ) -> dict[str, Any]:
        with self._lock:
            message = json.dumps(payload).encode("utf-8") + b"\n"
            self._serial.write(message)
            if not expect_response:
                return {"ok": True}
            line = self._serial.readline().decode("utf-8").strip()
            if not line:
                raise TimeoutError("serial timeout")
            return json.loads(line)


NODE_CLIENTS: dict[str, NodeClient] = {}
NODE_PORTS: dict[str, str] = {}


def get_node_client(node_id: str) -> Optional[NodeClient]:
    return NODE_CLIENTS.get(node_id)


def _handshake(port: str) -> NodeHello:
    with serial.Serial(
        port=port,
        baudrate=SERIAL_BAUDRATE,
        timeout=SERIAL_TIMEOUT_SEC,
    ) as ser:
        ser.write(json.dumps({"t": "hello", "proto": 1}).encode("utf-8") + b"\n")
        line = ser.readline().decode("utf-8").strip()
        if not line:
            raise TimeoutError("hello timeout")
        data = json.loads(line)
        if data.get("t") != "hello_ack":
            raise RuntimeError("bad hello ack")
        return NodeHello(
            node_id=data.get("nodeId"),
            fw=data.get("fw"),
            cap=data.get("cap"),
            calib_hash=data.get("calibHash"),
        )


def _scan_nodes_once() -> set[str]:
    active_ids: set[str] = set()
    ports = [port.device for port in list_ports.comports()]
    for port in ports:
        try:
            hello = _handshake(port)
            if not hello.node_id:
                continue
            active_ids.add(hello.node_id)
            existing = NODE_CLIENTS.get(hello.node_id)
            if not existing or NODE_PORTS.get(hello.node_id) != port:
                if existing:
                    existing.close()
                NODE_CLIENTS[hello.node_id] = NodeClient(port, hello)
                NODE_PORTS[hello.node_id] = port
            NODE_CLIENTS[hello.node_id].hello = hello
            upsert_node(
                node_id=hello.node_id,
                kind="real",
                fw=hello.fw,
                cap_json=encode_cap_json(hello.cap),
                status="online",
                last_error=None,
            )
            try:
                NODE_CLIENTS[hello.node_id].sync_calibration()
            except Exception as exc:
                upsert_node(
                    node_id=hello.node_id,
                    kind="real",
                    fw=hello.fw,
                    cap_json=encode_cap_json(hello.cap),
                    status="online",
                    last_error=f"calib sync failed: {exc}",
                )
        except Exception as exc:
            print(f"[nodes] port {port} failed: {exc}")
    mark_nodes_offline(active_ids)
    return active_ids


def scan_nodes_once() -> set[str]:
    return _scan_nodes_once()


async def node_discovery_loop() -> None:
    while True:
        await asyncio.to_thread(_scan_nodes_once)
        await asyncio.sleep(NODE_SCAN_INTERVAL_SEC)


_DUMMY_STATE: dict[str, dict[str, float]] = {}


def _init_dummy_state(setup_id: str) -> None:
    _DUMMY_STATE[setup_id] = {
        "ph": random.uniform(5.8, 6.4),
        "ec": random.uniform(1.2, 1.8),
        "temp": random.uniform(18.0, 22.0),
    }


def get_dummy_reading(setup_id: str) -> dict[str, Any]:
    if setup_id not in _DUMMY_STATE:
        _init_dummy_state(setup_id)
    state = _DUMMY_STATE[setup_id]
    state["ph"] = max(4.5, min(7.5, state["ph"] + random.uniform(-0.03, 0.03)))
    state["ec"] = max(0.6, min(2.6, state["ec"] + random.uniform(-0.05, 0.05)))
    state["temp"] = max(12.0, min(28.0, state["temp"] + random.uniform(-0.1, 0.1)))
    return {
        "t": "all",
        "ts": _now_ms(),
        "ph": round(state["ph"], 2),
        "ec": round(state["ec"], 2),
        "temp": round(state["temp"], 2),
        "status": ["ok"],
    }


def ensure_dummy_node() -> None:
    upsert_node(
        node_id="DUMMY",
        kind="dummy",
        fw=None,
        cap_json=None,
        status="online",
        last_error=None,
    )
