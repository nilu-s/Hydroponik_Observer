from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from typing import Any, Iterable, Optional

from .config import DB_PATH, DEFAULT_PHOTO_INTERVAL_MINUTES, DEFAULT_VALUE_INTERVAL_MINUTES, ensure_dirs

_thread_local = threading.local()


def _now_ms() -> int:
    return int(time.time() * 1000)


def init_db(reset: bool = False) -> None:
    ensure_dirs()
    if reset:
        _delete_db_files()
    with _get_conn() as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS setups (
                setup_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                node_id TEXT NULL,
                camera_id TEXT NULL,
                value_interval_minutes INTEGER NOT NULL,
                photo_interval_minutes INTEGER NOT NULL,
                created_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                name TEXT,
                kind TEXT NOT NULL,
                fw TEXT,
                cap_json TEXT,
                mode TEXT,
                last_seen_at INTEGER,
                status TEXT,
                last_error TEXT,
                status_json TEXT
            );
            CREATE TABLE IF NOT EXISTS calibration (
                node_id TEXT PRIMARY KEY,
                calib_version INTEGER NOT NULL,
                calib_hash TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                updated_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setup_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                ts INTEGER NOT NULL,
                ph REAL,
                ec REAL,
                temp REAL,
                status_json TEXT
            );
            CREATE TABLE IF NOT EXISTS cameras (
                camera_id TEXT PRIMARY KEY,
                port TEXT NOT NULL,
                alias TEXT,
                friendly_name TEXT,
                pnp_device_id TEXT,
                container_id TEXT,
                status TEXT,
                last_seen_at INTEGER,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            );
            """
        )
        _ensure_schema(conn)


def reset_db_contents() -> None:
    close_connections()
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        conn.execute("PRAGMA foreign_keys=OFF;")
        for table in ("readings", "setups", "nodes", "cameras", "calibration"):
            conn.execute(f"DROP TABLE IF EXISTS {table}")
        try:
            conn.execute("DELETE FROM sqlite_sequence")
        except sqlite3.OperationalError:
            pass
        conn.execute("PRAGMA foreign_keys=ON;")
    close_connections()
    init_db()


def _ensure_schema(conn: sqlite3.Connection) -> None:
    cols = [row[1] for row in conn.execute("PRAGMA table_info(nodes)").fetchall()]
    if "status_json" not in cols:
        conn.execute("ALTER TABLE nodes ADD COLUMN status_json TEXT")


@contextmanager
def _get_conn() -> Iterable[sqlite3.Connection]:
    conn = getattr(_thread_local, "conn", None)
    if conn is None:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        _thread_local.conn = conn
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pass


def close_connections() -> None:
    conn = getattr(_thread_local, "conn", None)
    if conn is None:
        return
    try:
        conn.close()
    finally:
        _thread_local.conn = None


def _delete_db_files() -> None:
    close_connections()
    candidates = [
        DB_PATH,
        DB_PATH.with_suffix(DB_PATH.suffix + "-wal"),
        DB_PATH.with_suffix(DB_PATH.suffix + "-shm"),
    ]
    for attempt in range(5):
        pending = []
        for path in candidates:
            if not path.exists():
                continue
            try:
                path.unlink(missing_ok=True)
            except PermissionError:
                pending.append(path)
        if not pending:
            return
        time.sleep(0.2 * (attempt + 1))
        close_connections()


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
                setup_id, name, node_id,
                value_interval_minutes, photo_interval_minutes,
                created_at
            ) VALUES (?, ?, NULL, ?, ?, ?)
            """,
            (
                setup_id,
                name,
                int(DEFAULT_VALUE_INTERVAL_MINUTES),
                int(DEFAULT_PHOTO_INTERVAL_MINUTES),
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
        "cameraPort": "camera_id",
        "valueIntervalMinutes": "value_interval_minutes",
        "photoIntervalMinutes": "photo_interval_minutes",
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
    status_json: Optional[str],
) -> None:
    last_seen_at = _now_ms()
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO nodes (
                node_id, name, kind, fw, cap_json, mode, last_seen_at, status, last_error, status_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(node_id) DO UPDATE SET
                name=COALESCE(excluded.name, nodes.name),
                kind=excluded.kind,
                fw=excluded.fw,
                cap_json=excluded.cap_json,
                mode=COALESCE(excluded.mode, nodes.mode),
                last_seen_at=excluded.last_seen_at,
                status=excluded.status,
                last_error=excluded.last_error,
                status_json=COALESCE(excluded.status_json, nodes.status_json)
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
                status_json,
            ),
        )


def update_node_alias(node_id: str, alias: Optional[str]) -> Optional[dict[str, Any]]:
    with _get_conn() as conn:
        conn.execute(
            "UPDATE nodes SET name = ? WHERE node_id = ?",
            (alias, node_id),
        )
    return get_node(node_id)


def update_node_mode(node_id: str, mode: Optional[str]) -> Optional[dict[str, Any]]:
    with _get_conn() as conn:
        conn.execute(
            "UPDATE nodes SET mode = ? WHERE node_id = ?",
            (mode, node_id),
        )
    return get_node(node_id)


def mark_nodes_offline(active_ids: set[str]) -> None:
    with _get_conn() as conn:
        rows = conn.execute("SELECT node_id FROM nodes").fetchall()
        for row in rows:
            node_id = row["node_id"]
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


def iter_readings(setup_id: str, batch_size: int = 1000) -> Iterable[dict[str, Any]]:
    with _get_conn() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM readings
            WHERE setup_id = ?
            ORDER BY ts DESC
            """,
            (setup_id,),
        )
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            for row in batch:
                yield dict(row)


def delete_readings_by_setup(setup_id: str) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM readings WHERE setup_id = ?", (setup_id,))


def encode_cap_json(cap: Optional[dict[str, Any]]) -> Optional[str]:
    if cap is None:
        return None
    return json.dumps(cap)


def encode_status_json(status: Optional[dict[str, Any]]) -> Optional[str]:
    if status is None:
        return None
    return json.dumps(status)


def get_calibration(node_id: str) -> Optional[dict[str, Any]]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM calibration WHERE node_id = ?",
            (node_id,),
        ).fetchone()
    return dict(row) if row else None


def list_cameras() -> list[dict[str, Any]]:
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM cameras ORDER BY port ASC").fetchall()
    return [dict(row) for row in rows]


def get_camera(camera_id: str) -> Optional[dict[str, Any]]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM cameras WHERE camera_id = ?",
            (camera_id,),
        ).fetchone()
    return dict(row) if row else None


def upsert_camera(
    camera_id: str,
    port: str,
    alias: Optional[str],
    friendly_name: Optional[str],
    pnp_device_id: Optional[str],
    container_id: Optional[str],
    status: str,
) -> dict[str, Any]:
    now = _now_ms()
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO cameras (
                camera_id, port, alias, friendly_name,
                pnp_device_id, container_id, status,
                last_seen_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(camera_id) DO UPDATE SET
                port=excluded.port,
                friendly_name=excluded.friendly_name,
                pnp_device_id=excluded.pnp_device_id,
                container_id=excluded.container_id,
                status=excluded.status,
                last_seen_at=excluded.last_seen_at,
                updated_at=excluded.updated_at,
                alias=COALESCE(cameras.alias, excluded.alias)
            """,
            (
                camera_id,
                port,
                alias,
                friendly_name,
                pnp_device_id,
                container_id,
                status,
                now,
                now,
                now,
            ),
        )
    return get_camera(camera_id)  # type: ignore[return-value]


def update_camera_alias(camera_id: str, alias: Optional[str]) -> Optional[dict[str, Any]]:
    with _get_conn() as conn:
        conn.execute(
            "UPDATE cameras SET alias = ?, updated_at = ? WHERE camera_id = ?",
            (alias, _now_ms(), camera_id),
        )
    return get_camera(camera_id)


def delete_camera(camera_id: str) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM cameras WHERE camera_id = ?", (camera_id,))


def mark_cameras_offline(active_ids: set[str]) -> None:
    with _get_conn() as conn:
        rows = conn.execute("SELECT camera_id FROM cameras").fetchall()
        for row in rows:
            camera_id = row["camera_id"]
            if camera_id not in active_ids:
                conn.execute(
                    "UPDATE cameras SET status = ?, updated_at = ? WHERE camera_id = ?",
                    ("offline", _now_ms(), camera_id),
                )
