"""
Agent Service — the brain of SportsLot Optimizer.

Implements the OBSERVE → REASON → ACT → OBSERVE → REASSESS → ACT → STOP loop.

Two decision providers:
  - GeminiDecisionProvider: Uses Google Gemini for reasoning
  - MockDecisionProvider:   Deterministic logic from behaviour_stats

Controlled by AI_MODE env var ('gemini' or 'mock').
Falls back to mock automatically if Gemini returns 429/errors.
"""

import os
import json
import time
import logging
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from backend.app.models.slot import Slot, SlotStatus
from backend.app.models.customer import Customer, CustomerSegment
from backend.app.models.agent_activity import AgentActivity, AgentAction
from backend.app.models.behaviour_stats import BehaviourStats
from backend.app.models.notification import Notification
from backend.app.schemas.agent import AgentDecision, AgentRunResponse, AgentActivityResponse
from backend.app.services.notification_service import send_notification
from backend.app.services.pricing_service import (
    apply_discount_to_slot,
    validate_discount,
    calculate_final_price,
    is_discount_justified,
)

logger = logging.getLogger(__name__)

MAX_GEMINI_CALLS = int(os.getenv("MAX_GEMINI_CALLS", "3"))
MAX_DISCOUNT_PERCENT = float(os.getenv("MAX_DISCOUNT_PERCENT", "30"))
AGENT_WAIT_MINUTES = int(os.getenv("AGENT_WAIT_MINUTES", "30"))


# ══════════════════════════════════════════════════════════════════════════
# Helper: gather context for the agent
# ══════════════════════════════════════════════════════════════════════════

def get_slot_context(db: Session, slot_id: str) -> dict:
    """Gather all context needed for the agent to make a decision."""
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        return {}

    # Get segment statistics for this slot's sport and time
    day_of_week = slot.date.weekday()  # 0=Monday
    hour = slot.start_time.hour

    stats = (
        db.query(BehaviourStats)
        .filter(
            BehaviourStats.sport == slot.sport,
            BehaviourStats.day_of_week == day_of_week,
            BehaviourStats.hour == hour,
        )
        .all()
    )

    # If no exact match, get stats for the sport broadly
    if not stats:
        stats = (
            db.query(BehaviourStats)
            .filter(BehaviourStats.sport == slot.sport)
            .all()
        )

    segment_stats = []
    for s in stats:
        segment_stats.append({
            "segment": s.segment,
            "sport": s.sport,
            "day_of_week": s.day_of_week,
            "hour": s.hour,
            "fill_rate": round(s.fill_rate, 3),
            "avg_time_to_book": round(s.avg_time_to_book, 1),
            "conversion_rate": round(s.conversion_rate, 3),
            "num_bookings": s.num_bookings,
        })

    # Get previous agent actions for this slot
    prev_actions = (
        db.query(AgentActivity)
        .filter(AgentActivity.slot_id == slot_id)
        .order_by(AgentActivity.created_at.asc())
        .all()
    )
    action_history = []
    for a in prev_actions:
        action_history.append({
            "action": a.action.value,
            "segment": a.target_segment,
            "discount_percent": a.discount_percent,
            "reason": a.reason,
            "recipients_count": a.recipients_count,
            "timestamp": a.created_at.isoformat() if a.created_at else None,
        })

    # Count existing notifications for this slot
    notif_count = db.query(Notification).filter(Notification.slot_id == slot_id).count()

    # Calculate time remaining (approximate)
    now = datetime.now()
    slot_datetime = datetime.combine(slot.date, slot.start_time)
    time_remaining_minutes = max(0, (slot_datetime - now).total_seconds() / 60)

    # Count customers per segment
    segment_counts = {}
    for seg in CustomerSegment:
        count = db.query(Customer).filter(Customer.segment == seg).count()
        segment_counts[seg.value] = count

    return {
        "slot": {
            "id": slot.id,
            "sport": slot.sport,
            "date": slot.date.isoformat(),
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
            "price": slot.price,
            "status": slot.status.value,
            "current_discount": slot.discount_percent,
            "final_price": slot.final_price,
        },
        "segment_statistics": segment_stats,
        "action_history": action_history,
        "notifications_sent": notif_count,
        "time_remaining_minutes": round(time_remaining_minutes, 0),
        "segment_customer_counts": segment_counts,
        "max_discount_percent": MAX_DISCOUNT_PERCENT,
        "is_reassessment": len(action_history) > 0,
    }


# ══════════════════════════════════════════════════════════════════════════
# Decision Providers
# ══════════════════════════════════════════════════════════════════════════

class DecisionProvider(ABC):
    """Abstract base for agent decision-making."""

    @abstractmethod
    def get_decision(self, context: dict) -> AgentDecision:
        """Given slot context, return a structured decision."""
        pass


class MockDecisionProvider(DecisionProvider):
    """Deterministic decision provider using behaviour_stats data.
    Works without Gemini API — perfect for dev/demo."""

    def get_decision(self, context: dict) -> AgentDecision:
        slot = context["slot"]
        stats = context["segment_statistics"]
        history = context["action_history"]
        time_remaining = context["time_remaining_minutes"]
        segment_counts = context["segment_customer_counts"]

        # If slot is already booked, STOP
        if slot["status"] == "BOOKED":
            return AgentDecision(
                action="STOP",
                segment=None,
                discount_percent=0,
                wait_minutes=0,
                reason="Slot is already booked. Stopping agent.",
            )

        # Determine what actions have already been taken
        notified_segments = set()
        discount_applied = False
        for h in history:
            if h["action"] in ("NOTIFY", "DISCOUNT"):
                if h["segment"]:
                    notified_segments.add(h["segment"])
            if h["action"] == "DISCOUNT":
                discount_applied = True

        # Find the best segment by conversion rate
        best_segment = None
        best_conversion = -1.0
        for s in stats:
            if s["conversion_rate"] > best_conversion and s["segment"] not in notified_segments:
                best_conversion = s["conversion_rate"]
                best_segment = s["segment"]

        # If all segments from stats have been notified, try any unnotified segment
        if not best_segment:
            all_segments = ["STUDENT", "WORKING_PROFESSIONAL", "NON_WORKING", "OTHER"]
            for seg in all_segments:
                if seg not in notified_segments and segment_counts.get(seg, 0) > 0:
                    best_segment = seg
                    best_conversion = 0.3  # default assumption
                    break

        # If truly no segment left to notify, consider discount or stop
        if not best_segment:
            if not discount_applied and time_remaining < 360:  # < 6 hours
                # Re-notify first segment with discount
                first_seg = next(iter(notified_segments), "STUDENT")
                discount = min(10.0, MAX_DISCOUNT_PERCENT)
                return AgentDecision(
                    action="NOTIFY_WITH_DISCOUNT",
                    segment=first_seg,
                    discount_percent=discount,
                    wait_minutes=AGENT_WAIT_MINUTES,
                    reason=(
                        f"All segments notified. Slot still vacant with {time_remaining:.0f} min remaining. "
                        f"Applying {discount}% discount to {first_seg} segment."
                    ),
                )
            else:
                return AgentDecision(
                    action="WAIT",
                    segment=None,
                    discount_percent=0,
                    wait_minutes=AGENT_WAIT_MINUTES,
                    reason="All segments have been notified. Waiting for bookings.",
                )

        # First run or fresh segment — NOTIFY without discount
        if not history or len(notified_segments) == 0:
            return AgentDecision(
                action="NOTIFY",
                segment=best_segment,
                discount_percent=0,
                wait_minutes=AGENT_WAIT_MINUTES,
                reason=(
                    f"{best_segment} has the highest historical conversion rate "
                    f"({best_conversion:.1%}) for {slot['sport']} on this day/time. "
                    f"Notifying without discount first."
                ),
            )

        # Reassessment — slot still vacant after first notification
        # If time is getting tight, consider discount
        if time_remaining < 120:  # < 2 hours
            discount = min(15.0, MAX_DISCOUNT_PERCENT)
            return AgentDecision(
                action="NOTIFY_WITH_DISCOUNT",
                segment=best_segment,
                discount_percent=discount,
                wait_minutes=AGENT_WAIT_MINUTES,
                reason=(
                    f"Slot remains vacant with only {time_remaining:.0f} minutes remaining. "
                    f"Urgent: applying {discount}% discount to {best_segment} segment."
                ),
            )
        elif time_remaining < 360:  # < 6 hours
            discount = min(10.0, MAX_DISCOUNT_PERCENT)
            return AgentDecision(
                action="NOTIFY_WITH_DISCOUNT",
                segment=best_segment,
                discount_percent=discount,
                wait_minutes=AGENT_WAIT_MINUTES,
                reason=(
                    f"Slot remains vacant. {time_remaining:.0f} minutes remaining. "
                    f"Moderate urgency: applying {discount}% discount to {best_segment}."
                ),
            )
        else:
            # Still plenty of time — notify another segment without discount
            return AgentDecision(
                action="NOTIFY",
                segment=best_segment,
                discount_percent=0,
                wait_minutes=AGENT_WAIT_MINUTES,
                reason=(
                    f"Slot still vacant but {time_remaining:.0f} minutes remaining — no urgency yet. "
                    f"Expanding outreach to {best_segment} without discount."
                ),
            )


class GeminiDecisionProvider(DecisionProvider):
    """Uses Google Gemini to reason about the best action."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self._model = None

    def _get_model(self):
        if self._model is None:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_INSTRUCTION,
                generation_config={
                    "temperature": 0.2,
                    "response_mime_type": "application/json",
                },
            )
        return self._model

    def get_decision(self, context: dict) -> AgentDecision:
        model = self._get_model()
        prompt = self._build_prompt(context)

        last_error = None
        for attempt in range(MAX_GEMINI_CALLS):
            try:
                logger.info(f"[AGENT] Gemini call attempt {attempt + 1}/{MAX_GEMINI_CALLS}")
                response = model.generate_content(prompt)
                text = response.text.strip()

                # Parse JSON response
                decision_data = json.loads(text)
                decision = AgentDecision(**decision_data)
                logger.info(f"[AGENT] Gemini decision: {decision.action} → {decision.segment}")
                return decision

            except Exception as e:
                last_error = e
                error_str = str(e)
                logger.warning(f"[AGENT] Gemini attempt {attempt + 1} failed: {error_str}")

                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait = 2 ** (attempt + 1)  # Exponential backoff: 2, 4, 8s
                    logger.info(f"[AGENT] Rate limited. Waiting {wait}s before retry...")
                    time.sleep(wait)
                else:
                    # Non-retryable error
                    break

        # All retries exhausted — fall back to mock
        logger.error(f"[AGENT] Gemini failed after {MAX_GEMINI_CALLS} attempts: {last_error}")
        logger.info("[AGENT] Falling back to MockDecisionProvider")
        return None  # Signal caller to use fallback

    def _build_prompt(self, context: dict) -> str:
        return f"""Analyze this vacant sports slot and decide the best action to fill it.

CURRENT CONTEXT:
{json.dumps(context, indent=2, default=str)}

RULES:
- Maximize expected revenue while minimizing unnecessary discounts
- Always prefer notifying WITHOUT discount first
- Only offer discounts when urgency justifies it (time_remaining_minutes is low)
- Consider which segment has the best conversion_rate and fill_rate
- Check action_history to avoid repeating the same action
- If the slot is already BOOKED, return STOP
- Discount must be between 0 and {MAX_DISCOUNT_PERCENT}%

Return a JSON object with EXACTLY these fields:
{{
  "action": "NOTIFY" | "NOTIFY_WITH_DISCOUNT" | "WAIT" | "REASSESS" | "STOP",
  "segment": "STUDENT" | "WORKING_PROFESSIONAL" | "NON_WORKING" | "OTHER" | null,
  "discount_percent": <number 0-{MAX_DISCOUNT_PERCENT}>,
  "wait_minutes": <number>,
  "reason": "<clear explanation of your reasoning>"
}}"""


# Gemini system instruction
SYSTEM_INSTRUCTION = """You are SportsLot Optimizer, an autonomous revenue optimization agent for sports turf bookings.

Your objective: Maximize expected revenue from vacant slots while minimizing unnecessary discounts.

You analyze:
- Historical fill rates, conversion rates, and average time-to-book per segment
- The specific sport, day of week, and hour
- Time remaining before the slot starts
- Previous outreach attempts and their results
- Discount constraints

Your strategy:
1. Identify the segment with the highest booking probability
2. First, NOTIFY without discount
3. Wait and reassess
4. Only escalate to discounts when time pressure justifies it
5. Stop immediately when booked

Always return valid JSON. Never return anything other than the decision JSON object."""


# ══════════════════════════════════════════════════════════════════════════
# Provider factory
# ══════════════════════════════════════════════════════════════════════════

def get_decision_provider() -> DecisionProvider:
    """Return the decision provider based on AI_MODE env var."""
    mode = os.getenv("AI_MODE", "mock").lower()
    if mode == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "")
        if api_key and api_key != "your-gemini-api-key":
            logger.info("[AGENT] Using GeminiDecisionProvider")
            return GeminiDecisionProvider()
        else:
            logger.warning("[AGENT] AI_MODE=gemini but no valid GEMINI_API_KEY. Falling back to mock.")
            return MockDecisionProvider()
    else:
        logger.info("[AGENT] Using MockDecisionProvider")
        return MockDecisionProvider()


# ══════════════════════════════════════════════════════════════════════════
# Record helper
# ══════════════════════════════════════════════════════════════════════════

def record_action(
    db: Session,
    slot_id: str,
    action: AgentAction,
    segment: Optional[str] = None,
    discount: float = 0.0,
    reason: str = "",
    recipients: int = 0,
) -> AgentActivity:
    """Record an agent action in the database."""
    activity = AgentActivity(
        slot_id=slot_id,
        action=action,
        target_segment=segment,
        discount_percent=discount,
        reason=reason,
        recipients_count=recipients,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    logger.info(f"[AGENT] Recorded: {action.value} for slot {slot_id}")
    return activity


# ══════════════════════════════════════════════════════════════════════════
# Execute decision
# ══════════════════════════════════════════════════════════════════════════

def execute_decision(db: Session, slot_id: str, decision: AgentDecision) -> dict:
    """Execute the agent's decision and return execution results."""
    execution = {
        "action_executed": decision.action,
        "notification_sent": False,
        "recipients_count": 0,
        "discount_applied": False,
    }

    if decision.action == "STOP":
        record_action(db, slot_id, AgentAction.STOP, reason=decision.reason)
        return execution

    if decision.action == "WAIT":
        record_action(
            db, slot_id, AgentAction.REASSESS,
            reason=decision.reason,
        )
        return execution

    if decision.action == "REASSESS":
        record_action(
            db, slot_id, AgentAction.REASSESS,
            reason=decision.reason,
        )
        return execution

    if decision.action in ("NOTIFY", "NOTIFY_WITH_DISCOUNT"):
        # Apply discount if needed
        if decision.discount_percent > 0:
            slot = db.query(Slot).filter(Slot.id == slot_id).first()
            if slot and validate_discount(decision.discount_percent):
                apply_discount_to_slot(db, slot, decision.discount_percent)
                execution["discount_applied"] = True
                logger.info(
                    f"[AGENT] Discount: {decision.discount_percent}% applied to slot {slot_id}"
                )

        # Send notifications
        if decision.segment:
            result = send_notification(
                db, slot_id, decision.segment, decision.discount_percent
            )
            execution["notification_sent"] = result["success"]
            execution["recipients_count"] = result["recipients_count"]
            logger.info(
                f"[AGENT] Sending notification to {result['recipients_count']} "
                f"{decision.segment} customers"
            )

    return execution


# ══════════════════════════════════════════════════════════════════════════
# Main agent entry points
# ══════════════════════════════════════════════════════════════════════════

def run_agent(db: Session, slot_id: str) -> AgentRunResponse:
    """Run the agent on a slot for the first time.

    1. Check slot exists and is VACANT
    2. Record SLOT_DETECTED
    3. Gather context
    4. Record ANALYSIS
    5. Get decision from provider
    6. Validate + execute decision
    7. Return results
    """
    # 1. Check slot
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        return AgentRunResponse(
            success=False, slot_id=slot_id,
            message=f"Slot {slot_id} not found",
        )

    if slot.status != SlotStatus.VACANT:
        return AgentRunResponse(
            success=False, slot_id=slot_id,
            message=f"Slot {slot_id} is {slot.status.value}, not VACANT",
        )

    logger.info(f"[AGENT] Slot {slot_id} detected as VACANT")

    # 2. Record slot detection
    record_action(
        db, slot_id, AgentAction.SLOT_DETECTED,
        reason=f"Vacant {slot.sport} slot on {slot.date} "
               f"({slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}) "
               f"at ₹{slot.price:.0f}",
    )

    # 3. Gather context
    context = get_slot_context(db, slot_id)
    logger.info(f"[AGENT] Retrieved segment statistics")

    # 4. Record analysis
    stat_summary = ", ".join(
        f"{s['segment']}: conv={s['conversion_rate']:.1%}"
        for s in context.get("segment_statistics", [])[:4]
    )
    record_action(
        db, slot_id, AgentAction.ANALYSIS,
        reason=f"Analyzed {len(context.get('segment_statistics', []))} segment stats. {stat_summary}",
    )

    # 5. Get decision
    provider = get_decision_provider()
    decision = provider.get_decision(context)

    # Handle Gemini fallback
    if decision is None:
        logger.info("[AGENT] Gemini failed — using MockDecisionProvider fallback")
        record_action(
            db, slot_id, AgentAction.AI_FALLBACK,
            reason="Gemini API unavailable. Using deterministic fallback.",
        )
        mock_provider = MockDecisionProvider()
        decision = mock_provider.get_decision(context)

    logger.info(f"[AGENT] Decision: {decision.action} → {decision.segment}")

    # 6. Execute decision
    execution = execute_decision(db, slot_id, decision)

    # 7. Get updated activity for response
    activities = (
        db.query(AgentActivity)
        .filter(AgentActivity.slot_id == slot_id)
        .order_by(AgentActivity.created_at.asc())
        .all()
    )

    return AgentRunResponse(
        success=True,
        slot_id=slot_id,
        decision=decision,
        message=f"Agent executed {decision.action} on slot {slot_id}",
        activity=[AgentActivityResponse.model_validate(a) for a in activities],
    )


def check_agent(db: Session, slot_id: str) -> AgentRunResponse:
    """Reassess a slot that was previously processed.

    If BOOKED → record BOOKED + STOP → return.
    If VACANT → gather updated context → get new decision → execute.
    """
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        return AgentRunResponse(
            success=False, slot_id=slot_id,
            message=f"Slot {slot_id} not found",
        )

    # If booked, stop
    if slot.status == SlotStatus.BOOKED:
        logger.info(f"[AGENT] Slot {slot_id} is now BOOKED")
        record_action(
            db, slot_id, AgentAction.BOOKED,
            reason="Slot has been booked since last check.",
        )
        record_action(
            db, slot_id, AgentAction.STOP,
            reason="Booking confirmed. Agent stopping.",
        )

        activities = (
            db.query(AgentActivity)
            .filter(AgentActivity.slot_id == slot_id)
            .order_by(AgentActivity.created_at.asc())
            .all()
        )
        return AgentRunResponse(
            success=True,
            slot_id=slot_id,
            decision=AgentDecision(
                action="STOP", segment=None, discount_percent=0,
                wait_minutes=0, reason="Slot is booked. Agent stopped.",
            ),
            message="Slot is booked. Agent stopped.",
            activity=[AgentActivityResponse.model_validate(a) for a in activities],
        )

    # Still vacant — reassess
    logger.info(f"[AGENT] Slot {slot_id} remains VACANT — reassessing")
    record_action(
        db, slot_id, AgentAction.REASSESS,
        reason="Slot still vacant. Reassessing strategy.",
    )

    context = get_slot_context(db, slot_id)

    provider = get_decision_provider()
    decision = provider.get_decision(context)

    if decision is None:
        record_action(
            db, slot_id, AgentAction.AI_FALLBACK,
            reason="Gemini API unavailable during reassessment. Using fallback.",
        )
        mock_provider = MockDecisionProvider()
        decision = mock_provider.get_decision(context)

    logger.info(f"[AGENT] Reassessment decision: {decision.action} → {decision.segment}")

    execution = execute_decision(db, slot_id, decision)

    activities = (
        db.query(AgentActivity)
        .filter(AgentActivity.slot_id == slot_id)
        .order_by(AgentActivity.created_at.asc())
        .all()
    )

    return AgentRunResponse(
        success=True,
        slot_id=slot_id,
        decision=decision,
        message=f"Reassessment: {decision.action} on slot {slot_id}",
        activity=[AgentActivityResponse.model_validate(a) for a in activities],
    )
