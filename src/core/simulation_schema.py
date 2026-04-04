"""Data models for simulation configuration and results."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


def _id() -> str:
    return uuid.uuid4().hex[:12]


class SimStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimConfig(BaseModel):
    id: str = Field(default_factory=_id)
    simulation_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SimResult(BaseModel):
    id: str = Field(default_factory=_id)
    config_id: str
    status: SimStatus = SimStatus.PENDING
    metrics: dict[str, Any] = Field(default_factory=dict)
    figures: list[str] = Field(default_factory=list, description="Paths to generated figure files")
    raw_data: Optional[dict[str, Any]] = None
    analysis_notes: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
