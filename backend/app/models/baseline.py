from datetime import date
from sqlalchemy import String, Integer, Float, Boolean, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Baseline(Base, TimestampMixin):
    __tablename__ = "baselines"
    __table_args__ = (UniqueConstraint("pet_id", "metric_type", "end_date", name="uq_pet_metric_end"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pet_id: Mapped[int] = mapped_column(Integer, ForeignKey("pets.id"), nullable=False)
    metric_type: Mapped[str] = mapped_column(String(20), nullable=False)

    baseline_value: Mapped[float] = mapped_column(Float, nullable=False)
    std_deviation: Mapped[float] = mapped_column(Float, nullable=False)
    seasonal_adj: Mapped[float | None] = mapped_column(Float)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    data_points: Mapped[int] = mapped_column(Integer, nullable=False)
    is_established: Mapped[bool] = mapped_column(Boolean, default=False)

    pet: Mapped["Pet"] = relationship(back_populates="baselines")