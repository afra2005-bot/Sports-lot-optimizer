"""Agent activity model — logs every action the AI agent takes.
This table powers the manager dashboard timeline."""

import enum
from sqlalchemy import Column, String, Integer, Float, Enum, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from backend.app.database.connection import Base


class AgentAction(str, enum.Enum):
    SLOT_DETECTED = "SLOT_DETECTED"
    ANALYSIS = "ANALYSIS"
    NOTIFY = "NOTIFY"
    DISCOUNT = "DISCOUNT"
    REASSESS = "REASSESS"
    BOOKED = "BOOKED"
    STOP = "STOP"


class AgentActivity(Base):
    __tablename__ = "agent_activity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slot_id = Column(String, ForeignKey("slots.id"), nullable=False, index=True)
    action = Column(Enum(AgentAction), nullable=False)
    target_segment = Column(String, nullable=True)
    discount_percent = Column(Float, nullable=True, default=0.0)
    reason = Column(Text, nullable=True)
    recipients_count = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
