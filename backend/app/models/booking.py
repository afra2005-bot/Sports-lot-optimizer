"""Booking model — records a customer's booking of a slot."""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from backend.app.database.connection import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, index=True)  # e.g. BK0001
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False, index=True)
    slot_id = Column(String, ForeignKey("slots.id"), nullable=False, index=True)
    booking_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    original_price = Column(Float, nullable=False)
    discount_percent = Column(Float, nullable=False, default=0.0)
    final_price = Column(Float, nullable=False)
