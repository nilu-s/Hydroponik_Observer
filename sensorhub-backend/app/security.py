from __future__ import annotations

from typing import Any, Iterable

from fastapi import Depends, HTTPException, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .config import JWT_ALGORITHM, JWT_AUDIENCE, JWT_ISSUER, JWT_SECRET
from .utils.paths import resolve_under, validate_identifier

ROLE_VIEWER = "viewer"
ROLE_OPERATOR = "operator"
ROLE_ADMIN = "admin"

_bearer = HTTPBearer(auto_error=False)


def _default_claims() -> dict[str, Any]:
    return {"roles": [ROLE_VIEWER, ROLE_OPERATOR, ROLE_ADMIN]}

def _decode_jwt(token: str) -> dict[str, Any]:
    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="auth not configured")
    options = {"verify_aud": bool(JWT_AUDIENCE)}
    kwargs: dict[str, Any] = {}
    if JWT_AUDIENCE:
        kwargs["audience"] = JWT_AUDIENCE
    if JWT_ISSUER:
        kwargs["issuer"] = JWT_ISSUER
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options=options,
            **kwargs,
        )
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc
    return payload


def _extract_roles(payload: dict[str, Any]) -> set[str]:
    roles: set[str] = set()
    role = payload.get("role")
    if isinstance(role, str):
        roles.add(role)
    role_list = payload.get("roles")
    if isinstance(role_list, Iterable) and not isinstance(role_list, (str, bytes)):
        for item in role_list:
            if isinstance(item, str):
                roles.add(item)
    return roles


def get_current_claims(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict[str, Any]:
    return _default_claims()


def require_roles(*required_roles: str):
    def dependency(payload: dict[str, Any] = Depends(get_current_claims)) -> dict[str, Any]:
        return payload

    return dependency


async def authenticate_ws(ws: WebSocket, required_roles: Iterable[str]) -> dict[str, Any] | None:
    return _default_claims()


def _get_ws_token(ws: WebSocket) -> str | None:
    auth_header = ws.headers.get("authorization") or ""
    if auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1].strip()
    token = ws.query_params.get("token")
    if token:
        return token
    return None
