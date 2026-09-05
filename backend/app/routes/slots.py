"""Slot API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database.connection import get_db
from backend.app.models.slot import Slot, SlotStatus
from backend.app.schemas.slot import SlotResponse, SlotListResponse

router = APIRouter(prefix="/api/slots", tags=["Slots"])


@router.get("", response_model=SlotListResponse)
def list_slots(
    status: Optional[str] = Query(None, description="Filter by status: VACANT, BOOKED, EXPIRED"),
    sport: Optional[str] = Query(None, description="Filter by sport"),
    db: Session = Depends(get_db),
):
    """List all slots, optionally filtered by status and/or sport."""
    query = db.query(Slot)
    if status:
        try:
            status_enum = SlotStatus(status)
            query = query.filter(Slot.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    if sport:
        query = query.filter(Slot.sport == sport)
    query = query.order_by(Slot.date, Slot.start_time)
    slots = query.all()
    return SlotListResponse(slots=slots, total=len(slots))


@router.get("/{slot_id}", response_model=SlotResponse)
def get_slot(slot_id: str, db: Session = Depends(get_db)):
    """Get a single slot by ID."""
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail=f"Slot {slot_id} not found")
    return slot
