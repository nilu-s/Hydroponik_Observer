from __future__ import annotations

import asyncio
import json
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
    update_node_mode,
)


@dataclass
class NodeHello:
    fw: Optional[str]
    cap: Optional[dict[str, Any]]
    calib_hash: Optional[str]


class NodeClient:
    def __init__(self, port: str, hello: NodeHello, node_key: str) -> None:
        self.port = port
        self.hello = hello
        self.node_key = node_key
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
        calib = get_calibration(self.node_key)
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
                    try:
                        self._serial.close()
                    except Exception:
                        pass
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


def remove_node_client(node_id: str) -> None:
    _remove_node_client(node_id)


def reset_runtime() -> None:
    for node_id in list(NODE_CLIENTS.keys()):
        _remove_node_client(node_id)


def _ensure_client_healthy(node_id: str, client: NodeClient) -> bool:
    if client.is_healthy():
        return True
    _remove_node_client(node_id)
    return False


def _parse_node_hello(data: dict[str, Any], expected_type: str) -> NodeHello:
    if data.get("t") != expected_type:
        raise RuntimeError("unexpected hello type")
    return NodeHello(
        fw=data.get("fw"),
        cap=data.get("cap"),
        calib_hash=data.get("calibHash"),
    )


def _send_hello_ack(ser: serial.Serial, hello: NodeHello) -> None:
    payload = {
        "t": "hello_ack",
        "fw": hello.fw,
        "cap": hello.cap,
        "calibHash": hello.calib_hash,
    }
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
    busy_ports: set[str] = set()
    for node_id, client in list(NODE_CLIENTS.items()):
        if _ensure_client_healthy(node_id, client):
            active_ids.add(node_id)
            busy_ports.add(client.port)
    ports = [port.device for port in list_ports.comports()]
    if not ports:
        log_event("nodes.scan_empty", ports=ports)
    for port in ports:
        if port in busy_ports:
            continue
        try:
            hello = _handshake(port)
            node_key = port
            log_event(
                "nodes.scan_success",
                port=port,
                node_key=node_key,
            )
            print(f"nodes.scan_success: port={port} key={node_key}")
            active_ids.add(node_key)
            existing = NODE_CLIENTS.get(node_key)
            if not existing or NODE_PORTS.get(node_key) != port:
                if existing:
                    _remove_node_client(node_key)
                NODE_CLIENTS[node_key] = NodeClient(port, hello, node_key)
                NODE_PORTS[node_key] = port
            NODE_CLIENTS[node_key].hello = hello
            existing_node = get_node(node_key)
            name_hint = None if existing_node and existing_node.get("name") else node_key
            upsert_node(
                node_id=node_key,
                name=name_hint,
                kind="real",
                fw=hello.fw,
                cap_json=encode_cap_json(hello.cap),
                mode=None,
                status="online",
                last_error=None,
            )
            _refresh_node_mode(node_key)
            try:
                NODE_CLIENTS[node_key].sync_calibration()
            except Exception as exc:
                upsert_node(
                    node_id=node_key,
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



async def _request_node_reading(setup_id: str, node_id: Optional[str]) -> dict[str, Any]:
    if not node_id:
        raise HTTPException(status_code=409, detail="no node assigned")
    client = get_node_client(node_id)
    if not client:
        raise HTTPException(status_code=503, detail="node offline")
    try:
        data = await asyncio.to_thread(client.request_all)
        mode = data.get("mode")
        if mode in ("real", "debug"):
            update_node_mode(node_id, mode)
        data["ts"] = _now_ms()
        return data
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"node error: {exc}")


def _refresh_node_mode(node_id: str) -> None:
    client = get_node_client(node_id)
    if not client:
        return
    try:
        data = client.request_all()
    except Exception as exc:
        log_event("nodes.mode_failed", port=client.port, error=str(exc))
        return
    mode = data.get("mode")
    if mode in ("real", "debug"):
        update_node_mode(node_id, mode)


async def fetch_setup_reading(setup_id: str) -> tuple[str, dict[str, Any]]:
    setup = get_setup(setup_id)
    if not setup:
        raise HTTPException(status_code=404, detail="setup not found")
    node_id = setup.get("node_id")
    reading = await _request_node_reading(setup_id, node_id)
    return node_id, reading


async def fetch_node_reading(setup_id: str, node_id: Optional[str]) -> dict[str, Any]:
    return await _request_node_reading(setup_id, node_id)


