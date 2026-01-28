from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
PHOTOS_DIR = DATA_DIR / "photos"
DB_PATH = DATA_DIR / "sensorhub.db"
DEFAULT_VALUE_INTERVAL_MINUTES = 30
DEFAULT_PHOTO_INTERVAL_MINUTES = 720

DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8081",
    "http://localhost:19006",
]


def _split_env_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


ADMIN_RESET_TOKEN = os.getenv("ADMIN_RESET_TOKEN", "")
JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ISSUER = os.getenv("JWT_ISSUER", "")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "")
CSRF_TOKEN = os.getenv("CSRF_TOKEN", "")
CORS_ALLOW_ORIGINS = _split_env_list(os.getenv("CORS_ALLOW_ORIGINS", "")) or DEFAULT_CORS_ORIGINS
CSRF_TRUSTED_ORIGINS = _split_env_list(os.getenv("CSRF_TRUSTED_ORIGINS", "")) or CORS_ALLOW_ORIGINS

NODE_SCAN_INTERVAL_SEC = 2
CAMERA_SCAN_INTERVAL_SEC = 5
NODE_RETRY_ATTEMPTS = 3
NODE_RETRY_BACKOFF_BASE_SEC = 0.1

CAMERA_WORKER_TIMEOUT_SEC = 10
CAMERA_WORKER_PATH = os.getenv("CAMERA_WORKER_PATH", "")
CAMERA_WORKER_MAX_PER_DEVICE = int(os.getenv("CAMERA_WORKER_MAX_PER_DEVICE", "2"))
CAMERA_WORKER_MAX_TOTAL = int(os.getenv("CAMERA_WORKER_MAX_TOTAL", "6"))
CAMERA_WORKER_CANDIDATES = [
    PROJECT_DIR
    / "sensorhub-backend"
    / "worker"
    / "bin"
    / "Release"
    / "net6.0-windows10.0.19041.0"
    / "CameraWorker.exe",
    PROJECT_DIR
    / "sensorhub-backend"
    / "worker"
    / "bin"
    / "Debug"
    / "net6.0-windows10.0.19041.0"
    / "CameraWorker.exe",
]

SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT_SEC = 1.5
SERIAL_OPEN_DELAY_SEC = 0.4
SERIAL_HANDSHAKE_TIMEOUT_SEC = 4.0
LIVE_MIN_FPS = 5
LIVE_MAX_FPS = 10
LIVE_POLL_INTERVAL_SEC = 2
PHOTO_CAPTURE_POLL_INTERVAL_SEC = float(os.getenv("PHOTO_CAPTURE_POLL_INTERVAL_SEC", "1"))

def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)


logger = logging.getLogger("sensorhub.camera")


def log_event(event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    logger.info(json.dumps(payload, ensure_ascii=True, separators=(",", ":")))
