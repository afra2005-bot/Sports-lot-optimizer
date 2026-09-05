"""Notification model — in-app notifications sent by the agent."""

import enum
from sqlalchemy import Column, String, Integer, Float, Enum, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from backend.app.database.connection import Base


class NotificationStatus(str, enum.Enum):
    SENT = "SENT"
    READ = "READ"
    BOOKED = "BOOKED"
    EXPIRED = "EXPIRED"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False, index=True)
    slot_id = Column(String, ForeignKey("slots.id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    discount_percent = Column(Float, nullable=False, default=0.0)
    status = Column(Enum(NotificationStatus), nullable=False, default=NotificationStatus.SENT)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
