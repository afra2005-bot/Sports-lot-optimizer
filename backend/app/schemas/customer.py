"""Pydantic schemas for customer API responses."""

from pydantic import BaseModel
from typing import Optional


class CustomerResponse(BaseModel):
    id: str
    name: str
    segment: str
    age: Optional[int] = None
    sport: Optional[str] = None

    model_config = {"from_attributes": True}
