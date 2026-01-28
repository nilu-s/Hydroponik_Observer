from pathlib import Path

import pytest
from fastapi import HTTPException

from app.security import resolve_under, validate_identifier


def test_validate_identifier_rejects_invalid() -> None:
    with pytest.raises(HTTPException):
        validate_identifier("../etc/passwd", "setup_id")


def test_validate_identifier_allows_simple() -> None:
    assert validate_identifier("S1a2b3c4", "setup_id") == "S1a2b3c4"


def test_resolve_under_rejects_traversal(tmp_path: Path) -> None:
    base = tmp_path / "base"
    base.mkdir()
    with pytest.raises(HTTPException):
        resolve_under(base, "..", "other")


def test_resolve_under_allows_child(tmp_path: Path) -> None:
    base = tmp_path / "base"
    base.mkdir()
    resolved = resolve_under(base, "child", "file.txt")
    assert resolved.parent == base / "child"
