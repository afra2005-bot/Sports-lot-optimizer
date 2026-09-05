"""Booking API routes."""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.schemas.booking import BookingCreate, BookingResponse
from backend.app.services.booking_service import create_booking

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


@router.post("", response_model=BookingResponse)
def book_slot(payload: BookingCreate, db: Session = Depends(get_db)):
    """Create a booking. Validates customer/slot, prevents double-booking,
    records agent activity, and updates notifications."""
    logger.info(f"[BOOKING] Request: customer={payload.customer_id} slot={payload.slot_id}")
    booking = create_booking(db, payload.customer_id, payload.slot_id)
    logger.info(f"[BOOKING] Success: {booking.id}")
    return booking
