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

from .config import (
    NODE_PING_FAILURES,
    NODE_PING_INTERVAL_SEC,
    NODE_SCAN_INTERVAL_SEC,
    SERIAL_BAUDRATE,
    SERIAL_TIMEOUT_SEC,
)
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
            dsrdtr=False,
            rtscts=False,
        )
        try:
            self._serial.dtr = True
            self._serial.rts = True
            time.sleep(0.2)
            self._serial.reset_input_buffer()
        except Exception:
            pass

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
        mode = data.get("mode") if isinstance(data, dict) else None
        if mode in ("real", "debug"):
            upsert_node(
                node_id=self.hello.node_id,
                name=None,
                kind="real",
                fw=self.hello.fw,
                cap_json=encode_cap_json(self.hello.cap),
                mode=mode,
                status="online",
                last_error=None,
            )
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
NODE_PING_FAILS: dict[str, int] = {}


def get_node_client(node_id: str) -> Optional[NodeClient]:
    return NODE_CLIENTS.get(node_id)


def _handshake(port: str) -> NodeHello:
    start_ms = _now_ms()
    print(f"[nodes] handshake start port={port} baud={SERIAL_BAUDRATE}")
    with serial.Serial(
        port=port,
        baudrate=SERIAL_BAUDRATE,
        timeout=SERIAL_TIMEOUT_SEC,
        write_timeout=SERIAL_TIMEOUT_SEC,
        dsrdtr=False,
        rtscts=False,
    ) as ser:
        print(
            f"[nodes] handshake open ok port={port} elapsed={_now_ms() - start_ms}ms"
        )
        # Allow time for USB CDC to become ready.
        try:
            ser.dtr = True
            ser.rts = True
        except Exception:
            pass
        time.sleep(2.0)
        print(
            f"[nodes] handshake boot wait done port={port} elapsed={_now_ms() - start_ms}ms"
        )
        hello_payload = {"t": "hello", "proto": 1}
        base = json.dumps(hello_payload, separators=(",", ":")).encode("utf-8")
        messages = [base + b"\n", base + b"\r\n"]
        line = ""
        for attempt, message in enumerate(messages, start=1):
            try:
                ser.reset_input_buffer()
            except Exception:
                pass
            try:
                ser.reset_output_buffer()
            except Exception:
                pass
            print(
                f"[nodes] hello -> port={port} attempt={attempt} elapsed={_now_ms() - start_ms}ms bytes={message!r}"
            )
            write_start = time.monotonic()
            written = ser.write(message)
            ser.flush()
            write_ms = int((time.monotonic() - write_start) * 1000)
            print(
                f"[nodes] hello write ok port={port} attempt={attempt} bytes={written} elapsed={_now_ms() - start_ms}ms write_ms={write_ms}"
            )
            time.sleep(0.1)
            line = ser.readline().decode("utf-8").strip()
            if line:
                break
            if attempt < len(messages):
                time.sleep(0.5)
        if not line:
            raise TimeoutError(
                f"hello timeout after {SERIAL_TIMEOUT_SEC}s (elapsed={_now_ms() - start_ms}ms)"
            )
        print(
            f"[nodes] hello <- port={port} elapsed={_now_ms() - start_ms}ms line={line}"
        )
        data = json.loads(line)
        if data.get("t") != "hello_ack":
            raise RuntimeError("bad hello ack")
        print(
            f"[nodes] handshake ok port={port} node_id={data.get('nodeId')} fw={data.get('fw')}"
        )
        return NodeHello(
            node_id=data.get("nodeId"),
            fw=data.get("fw"),
            cap=data.get("cap"),
            calib_hash=data.get("calibHash"),
        )


def _scan_nodes_once() -> set[str]:
    active_ids: set[str] = set()
    port_infos = list(list_ports.comports())
    pico_ports = [
        port
        for port in port_infos
        if (getattr(port, "vid", None), getattr(port, "pid", None)) == (0x2E8A, 0x00C0)
    ]
    ports = [port.device for port in pico_ports]
    if not ports:
        print("[nodes] no pico serial ports detected")
    else:
        print(f"[nodes] scanning pico ports ({len(ports)}): {', '.join(ports)}")
        for port in pico_ports:
            print(
                "[nodes] pico port info:"
                f" device={port.device}"
                f" hwid={port.hwid}"
                f" vid={getattr(port, 'vid', None)}"
                f" pid={getattr(port, 'pid', None)}"
                f" manufacturer={getattr(port, 'manufacturer', None)}"
                f" product={getattr(port, 'product', None)}"
                f" serial_number={getattr(port, 'serial_number', None)}"
            )
    in_use_ports = set(NODE_PORTS.values())
    for port in ports:
        if port in in_use_ports:
            print(f"[nodes] skip port in use: {port}")
            continue
        try:
            handshake_start_ms = _now_ms()
            hello = _handshake(port)
            if not hello.node_id:
                continue
            print(
                f"[nodes] hello ok port={port} node_id={hello.node_id} fw={hello.fw}"
            )
            print(
                f"[nodes] handshake total port={port} elapsed={_now_ms() - handshake_start_ms}ms"
            )
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
                name=None,
                kind="real",
                fw=hello.fw,
                cap_json=encode_cap_json(hello.cap),
                mode=None,
                status="online",
                last_error=None,
            )
            try:
                NODE_CLIENTS[hello.node_id].sync_calibration()
            except Exception as exc:
                upsert_node(
                    node_id=hello.node_id,
                    name=None,
                    kind="real",
                    fw=hello.fw,
                    cap_json=encode_cap_json(hello.cap),
                    mode=None,
                    status="online",
                    last_error=f"calib sync failed: {exc}",
                )
        except Exception as exc:
            elapsed_ms = _now_ms() - handshake_start_ms
            print(
                f"[nodes] port {port} failed after {elapsed_ms}ms: {type(exc).__name__} {exc}"
            )
    active_ids.update(NODE_CLIENTS.keys())
    mark_nodes_offline(active_ids)
    return active_ids


def scan_nodes_once() -> set[str]:
    return _scan_nodes_once()


async def node_discovery_loop() -> None:
    while True:
        await asyncio.to_thread(_scan_nodes_once)
        await asyncio.sleep(NODE_SCAN_INTERVAL_SEC)


async def node_ping_loop() -> None:
    while True:
        for node_id, client in list(NODE_CLIENTS.items()):
            try:
                data = await asyncio.to_thread(
                    client.send_command, {"t": "ping"}, True
                )
                if data.get("t") != "pong":
                    raise RuntimeError("bad pong")
                NODE_PING_FAILS.pop(node_id, None)
                upsert_node(
                    node_id=node_id,
                    name=None,
                    kind="real",
                    fw=client.hello.fw,
                    cap_json=encode_cap_json(client.hello.cap),
                    mode=None,
                    status="online",
                    last_error=None,
                )
            except Exception as exc:
                fails = NODE_PING_FAILS.get(node_id, 0) + 1
                NODE_PING_FAILS[node_id] = fails
                if fails >= NODE_PING_FAILURES:
                    print(f"[nodes] ping failed node_id={node_id}: {exc}")
                    client.close()
                    NODE_CLIENTS.pop(node_id, None)
                    NODE_PORTS.pop(node_id, None)
                    upsert_node(
                        node_id=node_id,
                        name=None,
                        kind="real",
                        fw=client.hello.fw,
                        cap_json=encode_cap_json(client.hello.cap),
                        mode=None,
                        status="offline",
                        last_error=f"ping failed: {exc}",
                    )
        await asyncio.sleep(NODE_PING_INTERVAL_SEC)


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
        name=None,
        kind="dummy",
        fw=None,
        cap_json=None,
        mode=None,
        status="online",
        last_error=None,
    )
