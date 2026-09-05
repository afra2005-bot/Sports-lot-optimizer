"""Pydantic schemas for booking API requests and responses."""

from pydantic import BaseModel
from typing import Optional
import datetime


class BookingCreate(BaseModel):
    customer_id: str
    slot_id: str


class BookingResponse(BaseModel):
    id: str
    customer_id: str
    slot_id: str
    booking_time: datetime.datetime
    original_price: float
    discount_percent: float
    final_price: float

    model_config = {"from_attributes": True}
