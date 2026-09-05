"""Customer model — maps to the customers.csv dataset."""

import enum
from sqlalchemy import Column, String, Integer, Enum

from backend.app.database.connection import Base


class CustomerSegment(str, enum.Enum):
    STUDENT = "STUDENT"
    WORKING_PROFESSIONAL = "WORKING_PROFESSIONAL"
    NON_WORKING = "NON_WORKING"
    OTHER = "OTHER"


# Mapping from CSV segment names to our enum
CSV_SEGMENT_MAP = {
    "college-group": CustomerSegment.STUDENT,
    "corporate": CustomerSegment.WORKING_PROFESSIONAL,
    "casual-walkin": CustomerSegment.NON_WORKING,
    "regular-weeknight": CustomerSegment.OTHER,
    "tournament-team": CustomerSegment.OTHER,
}


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)  # e.g. CUST0001
    name = Column(String, nullable=False)
    segment = Column(Enum(CustomerSegment), nullable=False)
    age = Column(Integer, nullable=True)
    sport = Column(String, nullable=True)  # preferred sport
