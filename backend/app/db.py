from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from typing import Any, Iterable, Optional

from .config import DB_PATH, DEFAULT_PHOTO_INTERVAL_SEC, DEFAULT_VALUE_INTERVAL_SEC, ensure_dirs


def _now_ms() -> int:
    return int(time.time() * 1000)


def _ensure_nodes_columns() -> None:
    with _get_conn() as conn:
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(nodes)").fetchall()
        }
        if "mode" not in columns:
            conn.execute("ALTER TABLE nodes ADD COLUMN mode TEXT")
        if "name" not in columns:
            conn.execute("ALTER TABLE nodes ADD COLUMN name TEXT")


def init_db(reset: bool = False) -> None:
    ensure_dirs()
    if DB_PATH.exists():
        if not reset:
            _ensure_nodes_columns()
            return
        DB_PATH.unlink(missing_ok=True)
    with _get_conn() as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.executescript(
            """
            CREATE TABLE setups (
                setup_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                node_id TEXT NULL,
                camera_id TEXT NULL,
                value_interval_sec INTEGER NOT NULL,
                photo_interval_sec INTEGER NOT NULL,
                created_at INTEGER NOT NULL
            );
            CREATE TABLE nodes (
                node_id TEXT PRIMARY KEY,
                name TEXT,
                kind TEXT NOT NULL,
                fw TEXT,
                cap_json TEXT,
                mode TEXT,
                last_seen_at INTEGER,
                status TEXT,
                last_error TEXT
            );
            CREATE TABLE cameras (
                camera_id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                friendly_name TEXT,
                pnp_device_id TEXT,
                container_id TEXT,
                last_seen_at INTEGER,
                status TEXT,
                last_error TEXT
            );
            CREATE TABLE photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setup_id TEXT NOT NULL,
                camera_id TEXT NOT NULL,
                ts INTEGER NOT NULL,
                path TEXT NOT NULL
            );
            CREATE TABLE calibration (
                node_id TEXT PRIMARY KEY,
                calib_version INTEGER NOT NULL,
                calib_hash TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                updated_at INTEGER NOT NULL
            );
            CREATE TABLE readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setup_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                ts INTEGER NOT NULL,
                ph REAL,
                ec REAL,
                temp REAL,
                status_json TEXT
            );
            """
        )
    _ensure_nodes_columns()


@contextmanager
def _get_conn() -> Iterable[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def list_setups() -> list[dict[str, Any]]:
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM setups ORDER BY created_at ASC").fetchall()
    return [dict(row) for row in rows]


def get_setup(setup_id: str) -> Optional[dict[str, Any]]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM setups WHERE setup_id = ?",
            (setup_id,),
        ).fetchone()
    return dict(row) if row else None


def create_setup(name: str) -> dict[str, Any]:
    setup_id = f"S{uuid.uuid4().hex[:8]}"
    created_at = _now_ms()
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO setups (
                setup_id, name, node_id, camera_id,
                value_interval_sec, photo_interval_sec, created_at
            ) VALUES (?, ?, NULL, NULL, ?, ?, ?)
            """,
            (
                setup_id,
                name,
                int(DEFAULT_VALUE_INTERVAL_SEC),
                int(DEFAULT_PHOTO_INTERVAL_SEC),
                created_at,
            ),
        )
    return get_setup(setup_id)  # type: ignore[return-value]


def update_setup(setup_id: str, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
    if not updates:
        return get_setup(setup_id)
    fields = []
    values: list[Any] = []
    mapping = {
        "name": "name",
        "nodeId": "node_id",
        "cameraId": "camera_id",
        "valueIntervalSec": "value_interval_sec",
        "photoIntervalSec": "photo_interval_sec",
    }
    for key, column in mapping.items():
        if key in updates:
            fields.append(f"{column} = ?")
            values.append(updates[key])
    if not fields:
        return get_setup(setup_id)
    values.append(setup_id)
    with _get_conn() as conn:
        conn.execute(
            f"UPDATE setups SET {', '.join(fields)} WHERE setup_id = ?",
            tuple(values),
        )
    return get_setup(setup_id)


def delete_setup(setup_id: str) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM setups WHERE setup_id = ?", (setup_id,))


def upsert_node(
    node_id: str,
    name: Optional[str],
    kind: str,
    fw: Optional[str],
    cap_json: Optional[str],
    mode: Optional[str],
    status: str,
    last_error: Optional[str],
) -> None:
    last_seen_at = _now_ms()
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO nodes (node_id, name, kind, fw, cap_json, mode, last_seen_at, status, last_error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(node_id) DO UPDATE SET
                name=COALESCE(excluded.name, nodes.name),
                kind=excluded.kind,
                fw=excluded.fw,
                cap_json=excluded.cap_json,
                mode=COALESCE(excluded.mode, nodes.mode),
                last_seen_at=excluded.last_seen_at,
                status=excluded.status,
                last_error=excluded.last_error
            """,
            (
                node_id,
                name,
                kind,
                fw,
                cap_json,
                mode,
                last_seen_at,
                status,
                last_error,
            ),
        )


def update_node_name(node_id: str, name: Optional[str]) -> Optional[dict[str, Any]]:
    with _get_conn() as conn:
        conn.execute(
            "UPDATE nodes SET name = ? WHERE node_id = ?",
            (name, node_id),
        )
    return get_node(node_id)


def mark_nodes_offline(active_ids: set[str]) -> None:
    with _get_conn() as conn:
        rows = conn.execute("SELECT node_id FROM nodes").fetchall()
        for row in rows:
            node_id = row["node_id"]
            if node_id == "DUMMY":
                continue
            if node_id not in active_ids:
                conn.execute(
                    "UPDATE nodes SET status = ?, last_error = ? WHERE node_id = ?",
                    ("offline", "not detected", node_id),
                )


def list_nodes() -> list[dict[str, Any]]:
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM nodes ORDER BY node_id ASC").fetchall()
    return [dict(row) for row in rows]


def get_node(node_id: str) -> Optional[dict[str, Any]]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM nodes WHERE node_id = ?",
            (node_id,),
        ).fetchone()
    return dict(row) if row else None


def delete_node(node_id: str) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM nodes WHERE node_id = ?", (node_id,))


def delete_calibration(node_id: str) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM calibration WHERE node_id = ?", (node_id,))


def upsert_camera(
    camera_id: str,
    device_id: str,
    friendly_name: Optional[str],
    pnp_device_id: Optional[str],
    container_id: Optional[str],
    status: str,
    last_error: Optional[str],
) -> None:
    last_seen_at = _now_ms()
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO cameras (
                camera_id, device_id, friendly_name, pnp_device_id,
                container_id, last_seen_at, status, last_error
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(camera_id) DO UPDATE SET
                device_id=excluded.device_id,
                friendly_name=excluded.friendly_name,
                pnp_device_id=excluded.pnp_device_id,
                container_id=excluded.container_id,
                last_seen_at=excluded.last_seen_at,
                status=excluded.status,
                last_error=excluded.last_error
            """,
            (
                camera_id,
                device_id,
                friendly_name,
                pnp_device_id,
                container_id,
                last_seen_at,
                status,
                last_error,
            ),
        )


def mark_cameras_offline(active_ids: set[str]) -> None:
    with _get_conn() as conn:
        rows = conn.execute("SELECT camera_id FROM cameras").fetchall()
        for row in rows:
            camera_id = row["camera_id"]
            if camera_id not in active_ids:
                conn.execute(
                    "UPDATE cameras SET status = ?, last_error = ? WHERE camera_id = ?",
                    ("offline", "not detected", camera_id),
                )


def list_cameras(online_only: bool = False) -> list[dict[str, Any]]:
    query = "SELECT * FROM cameras"
    params: tuple[Any, ...] = ()
    if online_only:
        query += " WHERE status = ?"
        params = ("online",)
    query += " ORDER BY camera_id ASC"
    with _get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_camera(camera_id: str) -> Optional[dict[str, Any]]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM cameras WHERE camera_id = ?",
            (camera_id,),
        ).fetchone()
    return dict(row) if row else None


def delete_camera(camera_id: str) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM cameras WHERE camera_id = ?", (camera_id,))


def insert_photo(setup_id: str, camera_id: str, ts: int, path: str) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO photos (setup_id, camera_id, ts, path)
            VALUES (?, ?, ?, ?)
            """,
            (setup_id, camera_id, ts, path),
        )


def insert_reading(
    setup_id: str,
    node_id: str,
    ts: int,
    ph: Optional[float],
    ec: Optional[float],
    temp: Optional[float],
    status: Optional[list[str]],
) -> None:
    status_json = json.dumps(status or [])
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO readings (setup_id, node_id, ts, ph, ec, temp, status_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (setup_id, node_id, ts, ph, ec, temp, status_json),
        )


def list_readings(setup_id: str, limit: int = 500) -> list[dict[str, Any]]:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM readings
            WHERE setup_id = ?
            ORDER BY ts DESC
            LIMIT ?
            """,
            (setup_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def list_all_readings(setup_id: str) -> list[dict[str, Any]]:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM readings
            WHERE setup_id = ?
            ORDER BY ts DESC
            """,
            (setup_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_photos(setup_id: str, limit: int = 200) -> list[dict[str, Any]]:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM photos
            WHERE setup_id = ?
            ORDER BY ts DESC
            LIMIT ?
            """,
            (setup_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def list_all_photos(setup_id: str) -> list[dict[str, Any]]:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM photos
            WHERE setup_id = ?
            ORDER BY ts DESC
            """,
            (setup_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_photo_paths_by_setup(setup_id: str) -> list[str]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT path FROM photos WHERE setup_id = ?",
            (setup_id,),
        ).fetchall()
    return [row["path"] for row in rows]


def delete_photos_by_setup(setup_id: str) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM photos WHERE setup_id = ?", (setup_id,))


def delete_readings_by_setup(setup_id: str) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM readings WHERE setup_id = ?", (setup_id,))


def encode_cap_json(cap: Optional[dict[str, Any]]) -> Optional[str]:
    if cap is None:
        return None
    return json.dumps(cap)


def get_calibration(node_id: str) -> Optional[dict[str, Any]]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM calibration WHERE node_id = ?",
            (node_id,),
        ).fetchone()
    return dict(row) if row else None
