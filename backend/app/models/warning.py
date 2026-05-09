from sqlalchemy import String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Warning(Base, TimestampMixin):
    __tablename__ = "warnings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pet_id: Mapped[int] = mapped_column(Integer, ForeignKey("pets.id"), nullable=False)
    checkin_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("checkins.id"))
    level: Mapped[str] = mapped_column(String(10), nullable=False)
    trigger_type: Mapped[str] = mapped_column(String(30), nullable=False)
    trigger_detail: Mapped[str | None] = mapped_column(Text)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    pet: Mapped["Pet"] = relationship(back_populates="warnings")
    checkin: Mapped["Checkin | None"] = relationship(back_populates="warning")