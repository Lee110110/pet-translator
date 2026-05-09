from pydantic import BaseModel
from datetime import date, datetime


class CheckinCreate(BaseModel):
    diet_score: int
    diet_note: str | None = None
    water_score: int
    water_note: str | None = None
    stool_score: int
    stool_note: str | None = None
    spirit_score: int
    spirit_note: str | None = None
    note: str | None = None


class CheckinUpdate(BaseModel):
    diet_score: int | None = None
    diet_note: str | None = None
    water_score: int | None = None
    water_note: str | None = None
    stool_score: int | None = None
    stool_note: str | None = None
    spirit_score: int | None = None
    spirit_note: str | None = None
    note: str | None = None


class CheckinOut(BaseModel):
    id: int
    pet_id: int
    checkin_date: date
    diet_score: int
    diet_note: str | None
    water_score: int
    water_note: str | None
    stool_score: int
    stool_note: str | None
    spirit_score: int
    spirit_note: str | None
    ai_interpretation: str | None
    ai_warning_level: str | None
    ai_confidence: float | None
    note: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}