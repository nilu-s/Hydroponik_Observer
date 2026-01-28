from __future__ import annotations

import re
from pathlib import Path

from fastapi import HTTPException

_id_pattern = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_identifier(value: str, label: str) -> str:
    if not value or not _id_pattern.match(value):
        raise HTTPException(status_code=400, detail=f"invalid {label}")
    return value


def resolve_under(base: Path, *parts: str) -> Path:
    resolved = base.joinpath(*parts).resolve()
    base_resolved = base.resolve()
    try:
        resolved.relative_to(base_resolved)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid path") from exc
    return resolved
