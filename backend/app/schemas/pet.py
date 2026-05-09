from pydantic import BaseModel
from datetime import date, datetime


class PetCreate(BaseModel):
    name: str
    breed: str | None = None
    birthday: date | None = None
    gender: str | None = None
    weight_kg: float | None = None
    color: str | None = None


class PetUpdate(BaseModel):
    name: str | None = None
    breed: str | None = None
    birthday: date | None = None
    gender: str | None = None
    weight_kg: float | None = None
    color: str | None = None
    avatar_url: str | None = None


class PetOut(BaseModel):
    id: int
    user_id: int
    name: str
    breed: str | None
    birthday: date | None
    gender: str | None
    weight_kg: float | None
    color: str | None
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}