#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def _require_value(name: str, value: str) -> str:
    value = value.strip()
    if not value:
        raise SystemExit(f"{name} is not set.")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset SensorHub backend via API.")
    parser.add_argument(
        "--backend-url",
        default=os.getenv("SENSORHUB_BACKEND_URL", "http://localhost:8000"),
        help="Backend base URL (env: SENSORHUB_BACKEND_URL).",
    )
    parser.add_argument(
        "--reset-token",
        default=os.getenv("ADMIN_RESET_TOKEN", ""),
        help="Admin reset token (env: ADMIN_RESET_TOKEN).",
    )
    parser.add_argument(
        "--jwt",
        default=os.getenv("SENSORHUB_JWT", ""),
        help="JWT token (env: SENSORHUB_JWT).",
    )
    parser.add_argument(
        "--csrf-token",
        default=os.getenv("CSRF_TOKEN", ""),
        help="Optional CSRF token (env: CSRF_TOKEN).",
    )
    args = parser.parse_args()

    backend_url = args.backend_url.rstrip("/")
    reset_token = _require_value("ADMIN_RESET_TOKEN", args.reset_token)
    jwt = _require_value("SENSORHUB_JWT", args.jwt)
    csrf_token = args.csrf_token.strip()

    url = f"{backend_url}/api/admin/reset"
    headers = {
        "Authorization": f"Bearer {jwt}",
        "X-Reset-Token": reset_token,
        "Content-Type": "application/json",
    }
    if csrf_token:
        headers["X-CSRF-Token"] = csrf_token

    request = urllib.request.Request(url, method="POST", headers=headers, data=b"{}")
    try:
        with urllib.request.urlopen(request) as response:
            payload = response.read().decode("utf-8")
        if payload:
            print(payload)
        else:
            print(json.dumps({"ok": True}))
        return 0
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8")
        print(f"Reset failed: {exc.code} {exc.reason}")
        if error_body:
            print(error_body)
        return 1
    except urllib.error.URLError as exc:
        print(f"Reset failed: {exc.reason}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
