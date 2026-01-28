from __future__ import annotations

from datetime import datetime
from typing import Iterable


def format_ts_iso(ts: int | None) -> str:
    if not isinstance(ts, int):
        return ""
    return datetime.fromtimestamp(ts / 1000).isoformat(sep=" ", timespec="seconds")


def iter_readings_with_iso(readings: Iterable[dict]) -> Iterable[dict]:
    for reading in readings:
        reading["ts_iso"] = format_ts_iso(reading.get("ts"))
        yield reading
