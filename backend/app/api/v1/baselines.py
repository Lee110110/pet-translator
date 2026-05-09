from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_pet
from app.models.pet import Pet
from app.models.baseline import Baseline
from app.schemas.baseline import BaselineOut, ChartDataOut
from app.services.baseline_service import get_chart_data, calculate_baseline

router = APIRouter(prefix="/pets/{pet_id}/baselines", tags=["个体基线"])


@router.get("", response_model=list[BaselineOut])
async def get_baselines(pet_id: int, pet: Pet = Depends(get_current_pet), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Baseline).where(Baseline.pet_id == pet_id)
    )
    return result.scalars().all()


@router.get("/chart", response_model=ChartDataOut)
async def get_baseline_chart(pet_id: int, pet: Pet = Depends(get_current_pet), db: AsyncSession = Depends(get_db)):
    return await get_chart_data(pet_id, db)


@router.post("/recalculate")
async def recalculate_baselines(pet_id: int, pet: Pet = Depends(get_current_pet), db: AsyncSession = Depends(get_db)):
    for metric in ["diet", "water", "stool", "spirit"]:
        await calculate_baseline(pet_id, metric, db)
    await db.commit()
    return {"detail": "基线已重新计算"}