from __future__ import annotations

from pathlib import Path

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
NODE_PING_INTERVAL_SEC = 5
NODE_PING_FAILURES = 2

SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT_SEC = 1.5
LIVE_MIN_FPS = 5
LIVE_MAX_FPS = 10
LIVE_POLL_INTERVAL_SEC = 5

def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
