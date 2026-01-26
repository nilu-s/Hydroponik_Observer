from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
PHOTOS_DIR = DATA_DIR / "photos"
DB_PATH = DATA_DIR / "sensorhub.db"
WORKER_PATH = (
    PROJECT_DIR
    / "backend"
    / "worker"
    / "bin"
    / "Release"
    / "net6.0-windows10.0.19041.0"
    / "camera_worker.dll"
)

DEFAULT_VALUE_INTERVAL_SEC = 1800
DEFAULT_PHOTO_INTERVAL_SEC = 43200

NODE_SCAN_INTERVAL_SEC = 7
CAMERA_SCAN_INTERVAL_SEC = 5
NODE_RETRY_ATTEMPTS = 3
NODE_RETRY_BACKOFF_BASE_SEC = 0.1

SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT_SEC = 1.5
SERIAL_OPEN_DELAY_SEC = 0.4
SERIAL_HANDSHAKE_TIMEOUT_SEC = 4.0
LIVE_MIN_FPS = 5
LIVE_MAX_FPS = 10
LIVE_POLL_INTERVAL_SEC = 5

def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)


logger = logging.getLogger("sensorhub.camera")


def log_event(event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    logger.info(json.dumps(payload, ensure_ascii=True, separators=(",", ":")))
