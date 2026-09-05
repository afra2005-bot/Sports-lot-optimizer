"""Slot model — represents a bookable time slot on a sports turf."""

import enum
from sqlalchemy import Column, String, Integer, Float, Date, Time, Enum

from backend.app.database.connection import Base


class SlotStatus(str, enum.Enum):
    VACANT = "VACANT"
    BOOKED = "BOOKED"
    EXPIRED = "EXPIRED"


class Slot(Base):
    __tablename__ = "slots"

    id = Column(String, primary_key=True, index=True)  # e.g. SL0001
    sport = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    price = Column(Float, nullable=False)         # original full price
    status = Column(Enum(SlotStatus), nullable=False, default=SlotStatus.VACANT)
    discount_percent = Column(Float, nullable=False, default=0.0)
    final_price = Column(Float, nullable=False)    # price after current discount
