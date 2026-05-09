from pydantic import BaseModel
from datetime import date, datetime


class VaccineCreate(BaseModel):
    type: str
    name: str
    scheduled_date: date
    actual_date: date | None = None
    status: str = "scheduled"
    reminder_days: int = 3
    notes: str | None = None


class VaccineUpdate(BaseModel):
    type: str | None = None
    name: str | None = None
    scheduled_date: date | None = None
    actual_date: date | None = None
    status: str | None = None
    reminder_days: int | None = None
    notes: str | None = None


class VaccineOut(BaseModel):
    id: int
    pet_id: int
    type: str
    name: str
    scheduled_date: date
    actual_date: date | None
    status: str
    reminder_days: int
    is_notified: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}