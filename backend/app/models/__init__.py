"""Models package — imports all models for easy access and table creation."""

from backend.app.models.customer import Customer, CustomerSegment
from backend.app.models.slot import Slot, SlotStatus
from backend.app.models.booking import Booking
from backend.app.models.notification import Notification, NotificationStatus
from backend.app.models.agent_activity import AgentActivity, AgentAction
from backend.app.models.behaviour_stats import BehaviourStats

__all__ = [
    "Customer", "CustomerSegment",
    "Slot", "SlotStatus",
    "Booking",
    "Notification", "NotificationStatus",
    "AgentActivity", "AgentAction",
    "BehaviourStats",
]
