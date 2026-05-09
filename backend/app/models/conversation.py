from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pet_id: Mapped[int] = mapped_column(Integer, ForeignKey("pets.id"), nullable=False)
    checkin_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("checkins.id"))
    warning_level: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    max_rounds: Mapped[int] = mapped_column(Integer, default=3)
    current_round: Mapped[int] = mapped_column(Integer, default=0)
    final_assessment: Mapped[str | None] = mapped_column(Text)
    final_recommendation: Mapped[str | None] = mapped_column(Text)

    pet: Mapped["Pet"] = relationship(back_populates="conversations")
    messages: Mapped[list["ConversationMessage"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class ConversationMessage(Base, TimestampMixin):
    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("conversations.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")