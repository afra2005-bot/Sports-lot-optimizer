"""Behaviour stats model — pre-computed historical statistics per segment/sport/time."""

from sqlalchemy import Column, String, Integer, Float

from backend.app.database.connection import Base


class BehaviourStats(Base):
    __tablename__ = "behaviour_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    segment = Column(String, nullable=False, index=True)
    sport = Column(String, nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    hour = Column(Integer, nullable=False)          # 0-23
    fill_rate = Column(Float, nullable=False, default=0.0)
    avg_time_to_book = Column(Float, nullable=False, default=0.0)  # minutes
    conversion_rate = Column(Float, nullable=False, default=0.0)
    num_bookings = Column(Integer, nullable=False, default=0)
