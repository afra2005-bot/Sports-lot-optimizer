"""Pricing service — all financial arithmetic lives here, NOT in Gemini.
Calculates expected revenue, validates discounts, applies discount to slots."""

import os
import logging
from sqlalchemy.orm import Session
from backend.app.models.slot import Slot

logger = logging.getLogger(__name__)

MAX_DISCOUNT_PERCENT = float(os.getenv("MAX_DISCOUNT_PERCENT", "30"))


def validate_discount(discount_percent: float) -> bool:
    """Check that a discount is within allowed bounds."""
    return 0 <= discount_percent <= MAX_DISCOUNT_PERCENT


def calculate_final_price(original_price: float, discount_percent: float) -> float:
    """Calculate price after applying discount."""
    return round(original_price * (1 - discount_percent / 100), 2)


def expected_revenue_without_discount(
    original_price: float, booking_probability: float
) -> float:
    """Expected revenue if we don't offer a discount."""
    return round(original_price * booking_probability, 2)


def expected_revenue_with_discount(
    original_price: float, discount_percent: float, boosted_probability: float
) -> float:
    """Expected revenue if we offer a discount.
    The boosted_probability should be higher than the base probability."""
    discounted_price = calculate_final_price(original_price, discount_percent)
    return round(discounted_price * boosted_probability, 2)


def is_discount_justified(
    original_price: float,
    discount_percent: float,
    base_probability: float,
    boosted_probability: float,
) -> bool:
    """A discount is justified only when the expected revenue WITH discount
    exceeds the expected revenue WITHOUT discount."""
    rev_no_discount = expected_revenue_without_discount(original_price, base_probability)
    rev_with_discount = expected_revenue_with_discount(
        original_price, discount_percent, boosted_probability
    )
    justified = rev_with_discount > rev_no_discount
    logger.info(
        f"Discount justification: no_discount_rev=₹{rev_no_discount}, "
        f"with_discount_rev=₹{rev_with_discount}, justified={justified}"
    )
    return justified


def apply_discount_to_slot(db: Session, slot: Slot, discount_percent: float) -> Slot:
    """Apply a validated discount to a slot and update its final_price."""
    if not validate_discount(discount_percent):
        raise ValueError(
            f"Discount {discount_percent}% exceeds maximum allowed {MAX_DISCOUNT_PERCENT}%"
        )
    slot.discount_percent = discount_percent
    slot.final_price = calculate_final_price(slot.price, discount_percent)
    db.commit()
    db.refresh(slot)
    logger.info(
        f"Applied {discount_percent}% discount to slot {slot.id}: "
        f"₹{slot.price} → ₹{slot.final_price}"
    )
    return slot
