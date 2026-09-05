"""Pydantic schemas for the AI agent — decision validation and activity responses."""

from pydantic import BaseModel, field_validator
from typing import Optional
import datetime


# Allowed actions the Gemini agent can take
VALID_ACTIONS = {"NOTIFY", "NOTIFY_WITH_DISCOUNT", "WAIT", "REASSESS", "STOP"}
VALID_SEGMENTS = {"STUDENT", "WORKING_PROFESSIONAL", "NON_WORKING", "OTHER"}


class AgentDecision(BaseModel):
    """Structured decision schema that Gemini must return.
    Validated with Pydantic before any execution."""
    action: str
    segment: Optional[str] = None
    discount_percent: float = 0.0
    wait_minutes: int = 30
    reason: str

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in VALID_ACTIONS:
            raise ValueError(f"Invalid action '{v}'. Must be one of: {VALID_ACTIONS}")
        return v

    @field_validator("segment")
    @classmethod
    def validate_segment(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_SEGMENTS:
            raise ValueError(f"Invalid segment '{v}'. Must be one of: {VALID_SEGMENTS}")
        return v

    @field_validator("discount_percent")
    @classmethod
    def validate_discount(cls, v: float) -> float:
        if v < 0 or v > 30:
            raise ValueError(f"Discount {v}% is out of allowed range [0, 30]")
        return v


class AgentActivityResponse(BaseModel):
    id: int
    slot_id: str
    action: str
    target_segment: Optional[str] = None
    discount_percent: Optional[float] = 0.0
    reason: Optional[str] = None
    recipients_count: Optional[int] = 0
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class AgentRunResponse(BaseModel):
    success: bool
    slot_id: str
    decision: Optional[AgentDecision] = None
    message: str
    activity: list[AgentActivityResponse] = []
