from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ReservationStatus(str, Enum):
    confirmed = "confirmed"
    checked_in = "checked_in"
    checked_out = "checked_out"
    cancelled = "cancelled"


class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"


class IssueType(str, Enum):
    plumbing = "plumbing"
    access = "access"
    heating = "heating"
    electrical = "electrical"
    other = "other"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guest_name: str
    property_name: str
    status: str
    payment_status: str
    payment_notifications_sent: int


class ReservationStatusUpdate(BaseModel):
    status: ReservationStatus


class CleaningTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reservation_id: int
    status: str


class MaintenanceRequestCreate(BaseModel):
    issue_type: IssueType
    description: str = Field(min_length=5, max_length=500)
    severity: Severity


class MaintenanceRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reservation_id: int
    property_name: str
    issue_type: str
    description: str
    severity: str
    status: str


class PaymentWebhookEvent(BaseModel):
    event_id: str = Field(min_length=3, max_length=160)
    reservation_id: int
    status: PaymentStatus


class PaymentWebhookResult(BaseModel):
    event_id: str
    reservation_id: int
    payment_status: str
    payment_notifications_sent: int
    duplicate: bool
