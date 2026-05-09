from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_pet
from app.models.pet import Pet
from app.models.warning import Warning
from app.schemas.warning import WarningOut, WarningDashboardOut
from app.services.disease_probability_service import calculate_disease_probabilities

router = APIRouter(prefix="/pets/{pet_id}/warnings", tags=["预警系统"])


@router.get("/disease-probability")
async def get_disease_probability(
    pet_id: int,
    symptoms: list[str] = Query(..., description="症状列表"),
    pet: Pet = Depends(get_current_pet),
):
    return calculate_disease_probabilities(
        breed=pet.breed,
        birthday=pet.birthday,
        symptoms=symptoms,
    )


@router.get("", response_model=list[WarningOut])
async def list_warnings(
    pet_id: int,
    level: str | None = None,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    query = select(Warning).where(Warning.pet_id == pet_id).order_by(Warning.created_at.desc())
    if level:
        query = query.where(Warning.level == level)
    result = await db.execute(query.limit(50))
    return result.scalars().all()


@router.get("/dashboard", response_model=WarningDashboardOut)
async def warning_dashboard(
    pet_id: int,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Warning.level, func.count(Warning.id))
        .where(Warning.pet_id == pet_id, Warning.is_read == False)
        .group_by(Warning.level)
    )
    counts = {row[0]: row[1] for row in result.all()}
    return WarningDashboardOut(
        green=counts.get("green", 0),
        yellow=counts.get("yellow", 0),
        orange=counts.get("orange", 0),
        red=counts.get("red", 0),
        total_unread=sum(counts.values()),
    )


@router.get("/{warning_id}", response_model=WarningOut)
async def get_warning(
    pet_id: int,
    warning_id: int,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Warning).where(Warning.id == warning_id, Warning.pet_id == pet_id)
    )
    warning = result.scalar_one_or_none()
    if not warning:
        raise HTTPException(status_code=404, detail="预警记录不存在")
    return warning


@router.put("/{warning_id}/read", response_model=WarningOut)
async def mark_warning_read(
    pet_id: int,
    warning_id: int,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Warning).where(Warning.id == warning_id, Warning.pet_id == pet_id)
    )
    warning = result.scalar_one_or_none()
    if not warning:
        raise HTTPException(status_code=404, detail="预警记录不存在")
    warning.is_read = True
    await db.commit()
    await db.refresh(warning)
    return warning