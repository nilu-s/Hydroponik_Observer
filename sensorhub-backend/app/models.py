from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class SetupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class SetupUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    port: Optional[str] = None
    cameraPort: Optional[str] = None
    valueIntervalMinutes: Optional[int] = Field(default=None, ge=1)
    photoIntervalMinutes: Optional[int] = Field(default=None, ge=1)


class Setup(BaseModel):
    setupId: str
    name: str
    port: Optional[str]
    cameraPort: Optional[str]
    valueIntervalMinutes: int
    photoIntervalMinutes: int
    createdAt: int


class Node(BaseModel):
    port: str
    alias: Optional[str] = None
    kind: str
    fw: Optional[str] = None
    capJson: Optional[str] = None
    mode: Optional[str] = None
    lastSeenAt: Optional[int] = None
    status: Optional[str] = None
    lastError: Optional[str] = None


class NodeUpdate(BaseModel):
    alias: Optional[str] = Field(default=None, min_length=1, max_length=100)


class CameraUpdate(BaseModel):
    alias: Optional[str] = Field(default=None, min_length=1, max_length=100)


class Reading(BaseModel):
    ts: int
    ph: float
    ec: float
    temp: float
    status: list[str]


class Calibration(BaseModel):
    port: str
    calibVersion: int
    calibHash: str
    payloadJson: str
    updatedAt: int


class NodeCommandRequest(BaseModel):
    t: Literal["hello", "get_all", "set_mode", "set_sim"]
    mode: Optional[Literal["real", "debug"]] = None
    simPh: Optional[float] = None
    simEc: Optional[float] = None
    simTemp: Optional[float] = None
