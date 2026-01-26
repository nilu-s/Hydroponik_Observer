from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException

from ..config import log_event
from ..db import init_db

router = APIRouter(prefix="/admin")


@router.post("/reset-db")
def reset_db(token: str = Header("", alias="X-Reset-Token")) -> dict:
    if token != "reset123":
        raise HTTPException(status_code=401, detail="unauthorized")
    init_db(reset=True)
    log_event("db.reset")
    return {"ok": True}
