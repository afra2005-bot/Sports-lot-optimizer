"""Notification service — creates in-app notifications for target customer segments."""

import logging
from sqlalchemy.orm import Session
from backend.app.models.customer import Customer, CustomerSegment
from backend.app.models.slot import Slot
from backend.app.models.notification import Notification, NotificationStatus
from backend.app.models.agent_activity import AgentActivity, AgentAction

logger = logging.getLogger(__name__)


def send_notification(
    db: Session,
    slot_id: str,
    segment: str,
    discount_percent: float = 0.0,
) -> dict:
    """Send in-app notifications to all customers in a segment for a given slot.

    1. Find eligible customers matching the segment
    2. Create notification records
    3. Record agent activity
    4. Return result summary
    """
    # Get slot details for the message
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        return {"success": False, "slot_id": slot_id, "segment": segment, "recipients_count": 0}

    # Find eligible customers in the target segment
    segment_enum = CustomerSegment(segment)
    customers = db.query(Customer).filter(Customer.segment == segment_enum).all()

    if not customers:
        logger.warning(f"No customers found in segment {segment}")
        return {"success": True, "slot_id": slot_id, "segment": segment, "recipients_count": 0}

    # Build notification message
    if discount_percent > 0:
        message = (
            f"🏸 Special offer! {slot.sport} slot on {slot.date} "
            f"({slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}) "
            f"now available at {discount_percent:.0f}% off! "
            f"Was ₹{slot.price:.0f}, now ₹{slot.final_price:.0f}. Book now!"
        )
    else:
        message = (
            f"🏸 {slot.sport} slot available on {slot.date} "
            f"({slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}) "
            f"at ₹{slot.price:.0f}. Book now before it's taken!"
        )

    # Check for existing notifications to avoid spamming same customers
    existing_notified = set(
        r[0] for r in db.query(Notification.customer_id).filter(
            Notification.slot_id == slot_id,
            Notification.customer_id.in_([c.id for c in customers]),
            Notification.discount_percent == discount_percent,
        ).all()
    )

    # Create notification records for customers not yet notified at this discount level
    new_notifications = []
    for customer in customers:
        if customer.id not in existing_notified:
            notif = Notification(
                customer_id=customer.id,
                slot_id=slot_id,
                message=message,
                discount_percent=discount_percent,
                status=NotificationStatus.SENT,
            )
            new_notifications.append(notif)

    db.add_all(new_notifications)
    recipients_count = len(new_notifications)

    # Record agent activity
    action = AgentAction.DISCOUNT if discount_percent > 0 else AgentAction.NOTIFY
    activity = AgentActivity(
        slot_id=slot_id,
        action=action,
        target_segment=segment,
        discount_percent=discount_percent,
        reason=f"Sent {'discount ' if discount_percent > 0 else ''}notifications to {segment} segment",
        recipients_count=recipients_count,
    )
    db.add(activity)
    db.commit()

    logger.info(
        f"Sent {recipients_count} notifications for slot {slot_id} "
        f"to segment {segment} (discount: {discount_percent}%)"
    )

    return {
        "success": True,
        "slot_id": slot_id,
        "segment": segment,
        "recipients_count": recipients_count,
    }
