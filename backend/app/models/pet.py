from datetime import date
from sqlalchemy import String, Boolean, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Pet(Base, TimestampMixin):
    __tablename__ = "pets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    breed: Mapped[str | None] = mapped_column(String(100))
    birthday: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(10))
    weight_kg: Mapped[float | None] = mapped_column(Float)
    color: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship(back_populates="pets")
    checkins: Mapped[list["Checkin"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    baselines: Mapped[list["Baseline"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    warnings: Mapped[list["Warning"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    vaccines: Mapped[list["Vaccine"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="pet", cascade="all, delete-orphan")