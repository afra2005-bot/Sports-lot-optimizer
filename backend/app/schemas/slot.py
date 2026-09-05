"""Pydantic schemas for slot API responses."""

from pydantic import BaseModel
from typing import Optional
import datetime


class SlotResponse(BaseModel):
    id: str
    sport: str
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    price: float
    status: str
    discount_percent: float
    final_price: float

    model_config = {"from_attributes": True}


class SlotListResponse(BaseModel):
    slots: list[SlotResponse]
    total: int
