from __future__ import annotations

import json
import logging
from typing import Any


logger = logging.getLogger("sensorhub.camera")


def log_event(event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    logger.info(json.dumps(payload, ensure_ascii=True, separators=(",", ":")))
