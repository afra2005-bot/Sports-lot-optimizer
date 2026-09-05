"""Customer API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.models.customer import Customer
from backend.app.models.notification import Notification
from backend.app.schemas.customer import CustomerResponse
from backend.app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("", response_model=list[CustomerResponse])
def list_customers(db: Session = Depends(get_db)):
    """List all customers."""
    customers = db.query(Customer).order_by(Customer.id).all()
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Get a customer by ID."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return customer


@router.get("/{customer_id}/notifications", response_model=list[NotificationResponse])
def get_customer_notifications(customer_id: str, db: Session = Depends(get_db)):
    """Get all notifications for a customer."""
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    notifications = (
        db.query(Notification)
        .filter(Notification.customer_id == customer_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return notifications
