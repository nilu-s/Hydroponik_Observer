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
from fastapi import HTTPException

from .config import (
    NODE_RETRY_ATTEMPTS,
    NODE_RETRY_BACKOFF_BASE_SEC,
    NODE_SCAN_INTERVAL_SEC,
    SERIAL_BAUDRATE,
    SERIAL_HANDSHAKE_TIMEOUT_SEC,
    SERIAL_OPEN_DELAY_SEC,
    SERIAL_TIMEOUT_SEC,
    log_event,
)
from .db import (
    _now_ms,
    encode_cap_json,
    get_calibration,
    get_node,
    get_setup,
    mark_nodes_offline,
    upsert_node,
)


@dataclass
class NodeHello:
    node_id: str
    fw: Optional[str]
    cap: Optional[dict[str, Any]]
    calib_hash: Optional[str]
    usb_name: Optional[str]


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

    def is_healthy(self) -> bool:
        return self._serial.is_open and _is_port_available(self.port)

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
        last_exc: Optional[Exception] = None
        for attempt in range(NODE_RETRY_ATTEMPTS):
            try:
                with self._lock:
                    message = json.dumps(payload).encode("utf-8") + b"\n"
                    self._serial.write(message)
                    if not expect_response:
                        return {"ok": True}
                    line = self._serial.readline().decode("utf-8").strip()
                    if not line:
                        raise TimeoutError("serial timeout")
                    return json.loads(line)
            except (TimeoutError, serial.SerialException, UnicodeDecodeError, json.JSONDecodeError) as exc:
                last_exc = exc
                if attempt + 1 >= NODE_RETRY_ATTEMPTS:
                    raise
                time.sleep(NODE_RETRY_BACKOFF_BASE_SEC * (2**attempt))
        raise last_exc if last_exc else RuntimeError("serial command failed")


NODE_CLIENTS: dict[str, NodeClient] = {}
NODE_PORTS: dict[str, str] = {}


def get_node_client(node_id: str) -> Optional[NodeClient]:
    client = NODE_CLIENTS.get(node_id)
    if not client:
        return None
    if not _ensure_client_healthy(node_id, client):
        return None
    return client


def _is_port_available(port: str) -> bool:
    return any(info.device == port for info in list_ports.comports())


RP2040_USB_VID = 0x2E8A
RP2040_USB_PIDS = {0x0005, 0x000A}


def _is_rp2040_port(info: list_ports.ListPortInfo) -> bool:
    if info.vid == RP2040_USB_VID and (info.pid in RP2040_USB_PIDS):
        return True
    desc = (info.description or "").lower()
    hwid = (info.hwid or "").lower()
    return "rp2040" in desc or "rp2040" in hwid or "2e8a" in hwid


def list_serial_ports() -> list[dict[str, str]]:
    ports = []
    for info in list_ports.comports():
        if not _is_rp2040_port(info):
            continue
        ports.append(
            {
                "device": info.device or "",
                "name": info.name or "",
                "description": info.description or "",
                "hwid": info.hwid or "",
                "manufacturer": info.manufacturer or "",
                "serial_number": info.serial_number or "",
                "vid": f"{info.vid:04x}" if info.vid is not None else "",
                "pid": f"{info.pid:04x}" if info.pid is not None else "",
                "location": info.location or "",
                "interface": info.interface or "",
            }
        )
    return ports


def _remove_node_client(node_id: str) -> None:
    client = NODE_CLIENTS.pop(node_id, None)
    if client:
        client.close()
    NODE_PORTS.pop(node_id, None)


def _ensure_client_healthy(node_id: str, client: NodeClient) -> bool:
    if client.is_healthy():
        return True
    _remove_node_client(node_id)
    return False


def _parse_node_hello(data: dict[str, Any], expected_type: str) -> NodeHello:
    if data.get("t") != expected_type:
        raise RuntimeError("unexpected hello type")
    node_id = data.get("nodeId")
    if not node_id:
        raise RuntimeError("missing nodeId")
    return NodeHello(
        node_id=node_id,
        fw=data.get("fw"),
        cap=data.get("cap"),
        calib_hash=data.get("calibHash"),
        usb_name=data.get("usbName"),
    )


def _send_hello_ack(ser: serial.Serial, hello: NodeHello) -> None:
    payload = {
        "t": "hello_ack",
        "nodeId": hello.node_id,
        "fw": hello.fw,
        "cap": hello.cap,
        "calibHash": hello.calib_hash,
    }
    if hello.usb_name:
        payload["usbName"] = hello.usb_name
    ser.write(json.dumps(payload).encode("utf-8") + b"\n")


def _handshake(port: str) -> NodeHello:
    with serial.Serial(
        port=port,
        baudrate=SERIAL_BAUDRATE,
        timeout=SERIAL_TIMEOUT_SEC,
    ) as ser:
        if SERIAL_OPEN_DELAY_SEC > 0:
            time.sleep(SERIAL_OPEN_DELAY_SEC)
        deadline = time.time() + SERIAL_HANDSHAKE_TIMEOUT_SEC
        last_error: Optional[Exception] = None
        while time.time() < deadline:
            try:
                line = ser.readline().decode("utf-8").strip()
                if not line:
                    continue
                data = json.loads(line)
                if data.get("t") != "hello":
                    continue
                hello = _parse_node_hello(data, "hello")
                _send_hello_ack(ser, hello)
                return hello
            except (UnicodeDecodeError, json.JSONDecodeError, RuntimeError) as exc:
                last_error = exc
                continue
        if last_error:
            raise RuntimeError(f"hello parse failed: {last_error}")
        raise TimeoutError("hello timeout")


def _scan_nodes_once() -> set[str]:
    active_ids: set[str] = set()
    ports = [port.device for port in list_ports.comports()]
    if not ports:
        log_event("nodes.scan_empty", ports=ports)
    for port in ports:
        try:
            hello = _handshake(port)
            if not hello.node_id:
                continue
            log_event("nodes.scan_success", port=port, node_id=hello.node_id)
            print(f"nodes.scan_success: port={port} node_id={hello.node_id}")
            active_ids.add(hello.node_id)
            existing = NODE_CLIENTS.get(hello.node_id)
            if not existing or NODE_PORTS.get(hello.node_id) != port:
                if existing:
                    _remove_node_client(hello.node_id)
                NODE_CLIENTS[hello.node_id] = NodeClient(port, hello)
                NODE_PORTS[hello.node_id] = port
            NODE_CLIENTS[hello.node_id].hello = hello
            existing_node = get_node(hello.node_id)
            name_hint = None if existing_node and existing_node.get("name") else hello.node_id
            upsert_node(
                node_id=hello.node_id,
                name=name_hint,
                kind="real",
                fw=hello.fw,
                cap_json=encode_cap_json(hello.cap),
                mode=None,
                status="online",
                last_error=None,
            )
            if existing_node and existing_node.get("name") and existing_node.get("name") != hello.usb_name:
                try:
                    NODE_CLIENTS[hello.node_id].send_command(
                        {"t": "set_usb_name", "name": existing_node.get("name")},
                        expect_response=True,
                    )
                    log_event(
                        "nodes.usb_name_sync",
                        node_id=hello.node_id,
                        name=existing_node.get("name"),
                    )
                except Exception as exc:
                    log_event(
                        "nodes.usb_name_sync_failed",
                        node_id=hello.node_id,
                        error=str(exc),
                    )
            try:
                NODE_CLIENTS[hello.node_id].sync_calibration()
            except Exception as exc:
                upsert_node(
                    node_id=hello.node_id,
                    name=name_hint,
                    kind="real",
                    fw=hello.fw,
                    cap_json=encode_cap_json(hello.cap),
                    mode=None,
                    status="online",
                    last_error=f"calib sync failed: {exc}",
                )
        except Exception as exc:
            log_event("nodes.scan_failed", port=port, error=str(exc))
            print(f"nodes.scan_failed: port={port} error={exc}")
    mark_nodes_offline(active_ids)
    return active_ids


async def node_discovery_loop() -> None:
    while True:
        await asyncio.to_thread(_scan_nodes_once)
        await asyncio.sleep(NODE_SCAN_INTERVAL_SEC)


_DUMMY_STATE: dict[str, dict[str, float]] = {}


def _init_dummy_state(state_key: str) -> None:
    _DUMMY_STATE[state_key] = {
        "ph": random.uniform(5.8, 6.4),
        "ec": random.uniform(1.2, 1.8),
        "temp": random.uniform(18.0, 22.0),
    }


def get_dummy_reading(state_key: str) -> dict[str, Any]:
    if state_key not in _DUMMY_STATE:
        _init_dummy_state(state_key)
    state = _DUMMY_STATE[state_key]
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


def ensure_dummy_node() -> None:
    upsert_node(
        node_id="DUMMY",
        name=None,
        kind="dummy",
        fw=None,
        cap_json=None,
        mode=None,
        status="online",
        last_error=None,
    )

