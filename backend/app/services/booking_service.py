"""Booking service — handles the atomic booking operation with race-condition safety."""

import logging
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException

from backend.app.models.slot import Slot, SlotStatus
from backend.app.models.booking import Booking
from backend.app.models.customer import Customer
from backend.app.models.notification import Notification, NotificationStatus
from backend.app.models.agent_activity import AgentActivity, AgentAction

logger = logging.getLogger(__name__)


def generate_booking_id(db: Session) -> str:
    """Generate the next sequential booking ID."""
    last = db.query(Booking).order_by(Booking.id.desc()).first()
    if last:
        num = int(last.id.replace("BK", "")) + 1
    else:
        num = 1
    return f"BK{num:04d}"


def create_booking(db: Session, customer_id: str, slot_id: str) -> Booking:
    """Create a booking with full validation and race-condition protection.

    Steps:
    1. Verify customer exists
    2. Lock the slot row (SELECT FOR UPDATE)
    3. Verify slot is VACANT
    4. Create booking record
    5. Update slot status to BOOKED
    6. Update related notifications to BOOKED
    7. Record BOOKED in agent_activity
    """
    # 1. Verify customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    # 2. Lock the slot row to prevent race conditions
    slot = (
        db.query(Slot)
        .filter(Slot.id == slot_id)
        .with_for_update()  # SELECT ... FOR UPDATE
        .first()
    )
    if not slot:
        raise HTTPException(status_code=404, detail=f"Slot {slot_id} not found")

    # 3. Verify slot is still VACANT
    if slot.status != SlotStatus.VACANT:
        raise HTTPException(
            status_code=409,
            detail=f"Slot {slot_id} is already {slot.status.value}. Cannot double-book."
        )

    # 4. Create booking
    booking_id = generate_booking_id(db)
    booking = Booking(
        id=booking_id,
        customer_id=customer_id,
        slot_id=slot_id,
        original_price=slot.price,
        discount_percent=slot.discount_percent,
        final_price=slot.final_price,
    )
    db.add(booking)

    # 5. Update slot status
    slot.status = SlotStatus.BOOKED
    
    # 6. Update related notifications to BOOKED status
    db.query(Notification).filter(
        Notification.slot_id == slot_id,
        Notification.status == NotificationStatus.SENT,
    ).update({"status": NotificationStatus.BOOKED})

    # 7. Record BOOKED in agent activity
    activity = AgentActivity(
        slot_id=slot_id,
        action=AgentAction.BOOKED,
        target_segment=customer.segment.value,
        discount_percent=slot.discount_percent,
        reason=f"Slot booked by {customer.name} ({customer.segment.value}) at ₹{slot.final_price:.0f}",
        recipients_count=0,
    )
    db.add(activity)

    db.commit()
    db.refresh(booking)

    logger.info(
        f"Booking {booking_id}: {customer_id} booked slot {slot_id} "
        f"at ₹{slot.final_price:.0f} (discount: {slot.discount_percent}%)"
    )

    return booking
