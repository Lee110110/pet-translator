from pydantic import BaseModel
from datetime import date, datetime


class MedicalSummaryRequest(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    visit_reason: str | None = None


class MedicalSummaryOut(BaseModel):
    summary_text: str
    key_findings: list[str]
    recommendations: list[str]
    warning_history_summary: str
    suggested_tests: list[str]
    generated_at: datetime