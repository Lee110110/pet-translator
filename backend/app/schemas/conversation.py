from pydantic import BaseModel
from datetime import datetime


class StartConversationRequest(BaseModel):
    initial_symptoms: str
    checkin_id: int | None = None
    warning_level: str | None = None


class ReplyRequest(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    round_number: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationOut(BaseModel):
    id: int
    pet_id: int
    checkin_id: int | None
    warning_level: str
    status: str
    max_rounds: int
    current_round: int
    final_assessment: str | None
    final_recommendation: str | None
    messages: list[MessageOut]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}