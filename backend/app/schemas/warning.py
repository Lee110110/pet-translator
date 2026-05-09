from pydantic import BaseModel
from datetime import datetime


class WarningOut(BaseModel):
    id: int
    pet_id: int
    checkin_id: int | None
    level: str
    trigger_type: str
    trigger_detail: str | None
    message: str
    is_notified: bool
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WarningDashboardOut(BaseModel):
    green: int = 0
    yellow: int = 0
    orange: int = 0
    red: int = 0
    total_unread: int = 0