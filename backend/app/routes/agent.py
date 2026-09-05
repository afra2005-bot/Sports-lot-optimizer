"""Agent API routes — run the AI agent, check/reassess, view activity."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.models.slot import Slot, SlotStatus
from backend.app.models.agent_activity import AgentActivity
from backend.app.schemas.agent import AgentActivityResponse, AgentRunResponse
from backend.app.services.agent_service import run_agent, check_agent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/agent", tags=["Agent"])


@router.get("/activity/{slot_id}", response_model=list[AgentActivityResponse])
def get_agent_activity(slot_id: str, db: Session = Depends(get_db)):
    """Get all agent activity for a slot (timeline view)."""
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail=f"Slot {slot_id} not found")

    activities = (
        db.query(AgentActivity)
        .filter(AgentActivity.slot_id == slot_id)
        .order_by(AgentActivity.created_at.asc())
        .all()
    )
    return activities


@router.post("/run/{slot_id}", response_model=AgentRunResponse)
def agent_run(slot_id: str, db: Session = Depends(get_db)):
    """Run the AI agent on a vacant slot.
    
    The agent will:
    1. Detect the slot
    2. Analyze historical statistics
    3. Get a decision from Gemini or Mock provider
    4. Execute the decision (send notification, apply discount, etc.)
    5. Record all actions
    """
    logger.info(f"[AGENT] Run requested for slot {slot_id}")
    result = run_agent(db, slot_id)
    return result


@router.post("/check/{slot_id}", response_model=AgentRunResponse)
def agent_check(slot_id: str, db: Session = Depends(get_db)):
    """Reassess a slot — check if it's been booked, and if not, get next decision.
    
    If the slot is BOOKED, records STOP and returns.
    If still VACANT, runs reassessment with updated urgency context.
    """
    logger.info(f"[AGENT] Check/reassess requested for slot {slot_id}")
    result = check_agent(db, slot_id)
    return result
