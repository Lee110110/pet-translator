from datetime import date
from sqlalchemy import String, Integer, Float, Text, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Checkin(Base, TimestampMixin):
    __tablename__ = "checkins"
    __table_args__ = (UniqueConstraint("pet_id", "checkin_date", name="uq_pet_checkin_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pet_id: Mapped[int] = mapped_column(Integer, ForeignKey("pets.id"), nullable=False)
    checkin_date: Mapped[date] = mapped_column(Date, nullable=False)

    diet_score: Mapped[int] = mapped_column(Integer, nullable=False)
    diet_note: Mapped[str | None] = mapped_column(Text)
    water_score: Mapped[int] = mapped_column(Integer, nullable=False)
    water_note: Mapped[str | None] = mapped_column(Text)
    stool_score: Mapped[int] = mapped_column(Integer, nullable=False)
    stool_note: Mapped[str | None] = mapped_column(Text)
    spirit_score: Mapped[int] = mapped_column(Integer, nullable=False)
    spirit_note: Mapped[str | None] = mapped_column(Text)

    ai_interpretation: Mapped[str | None] = mapped_column(Text)
    ai_warning_level: Mapped[str | None] = mapped_column(String(10))
    ai_confidence: Mapped[float | None] = mapped_column(Float)

    note: Mapped[str | None] = mapped_column(Text)

    pet: Mapped["Pet"] = relationship(back_populates="checkins")
    warning: Mapped["Warning | None"] = relationship(back_populates="checkin", uselist=False)