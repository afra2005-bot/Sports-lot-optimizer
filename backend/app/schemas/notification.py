"""Pydantic schemas for notification API responses."""

from pydantic import BaseModel
import datetime


class NotificationResponse(BaseModel):
    id: int
    customer_id: str
    slot_id: str
    message: str
    discount_percent: float
    status: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class NotificationSendResult(BaseModel):
    success: bool
    slot_id: str
    segment: str
    recipients_count: int
