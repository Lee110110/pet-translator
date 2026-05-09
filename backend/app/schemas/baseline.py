from pydantic import BaseModel
from datetime import date, datetime


class BaselineOut(BaseModel):
    id: int
    pet_id: int
    metric_type: str
    baseline_value: float
    std_deviation: float
    seasonal_adj: float | None
    start_date: date
    end_date: date
    data_points: int
    is_established: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChartMetricOut(BaseModel):
    dates: list[str]
    actual: list[int]
    baseline_value: float | None
    baseline_upper: float | None
    baseline_lower: float | None
    is_established: bool


class ChartDataOut(BaseModel):
    diet: ChartMetricOut
    water: ChartMetricOut
    stool: ChartMetricOut
    spirit: ChartMetricOut