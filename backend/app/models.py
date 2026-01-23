from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class SetupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class SetupUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    nodeId: Optional[str] = None
    cameraId: Optional[str] = None
    valueIntervalSec: Optional[int] = Field(default=None, ge=1)
    photoIntervalSec: Optional[int] = Field(default=None, ge=1)


class Setup(BaseModel):
    setupId: str
    name: str
    nodeId: Optional[str]
    cameraId: Optional[str]
    valueIntervalSec: int
    photoIntervalSec: int
    createdAt: int


class Node(BaseModel):
    nodeId: str
    name: Optional[str] = None
    kind: str
    fw: Optional[str] = None
    capJson: Optional[str] = None
    mode: Optional[str] = None
    lastSeenAt: Optional[int] = None
    status: Optional[str] = None
    lastError: Optional[str] = None


class NodeUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)


class Camera(BaseModel):
    cameraId: str
    deviceId: str
    friendlyName: Optional[str] = None
    pnpDeviceId: Optional[str] = None
    containerId: Optional[str] = None
    lastSeenAt: Optional[int] = None
    status: Optional[str] = None
    lastError: Optional[str] = None


class CameraBindRequest(BaseModel):
    deviceId: str = Field(min_length=3, max_length=2000)


class Reading(BaseModel):
    ts: int
    ph: float
    ec: float
    temp: float
    status: list[str]


class Calibration(BaseModel):
    nodeId: str
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
