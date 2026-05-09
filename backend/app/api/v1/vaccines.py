import json
import pathlib
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_pet
from app.models.pet import Pet
from app.models.vaccine import Vaccine
from app.schemas.vaccine import VaccineCreate, VaccineUpdate, VaccineOut

router = APIRouter(prefix="/pets/{pet_id}/vaccines", tags=["疫苗/驱虫"])


def _load_vaccine_knowledge() -> list[dict]:
    path = pathlib.Path(__file__).parent.parent.parent / "knowledge" / "cat_vaccines.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _age_weeks(birthday: date) -> int:
    return (date.today() - birthday).days // 7


def _parse_age_to_weeks(age_str: str) -> int:
    age_str = age_str.replace("以上", "").strip()
    if "周" in age_str:
        return int(age_str.replace("周", ""))
    if "月" in age_str:
        return int(age_str.replace("月", "")) * 4
    if "岁" in age_str:
        return int(age_str.replace("岁", "")) * 52
    return 0


@router.post("", response_model=VaccineOut)
async def create_vaccine(
    pet_id: int,
    req: VaccineCreate,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    vaccine = Vaccine(pet_id=pet_id, **req.model_dump())
    db.add(vaccine)
    await db.commit()
    await db.refresh(vaccine)
    return vaccine


@router.get("", response_model=list[VaccineOut])
async def list_vaccines(
    pet_id: int,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vaccine)
        .where(Vaccine.pet_id == pet_id)
        .order_by(Vaccine.scheduled_date.asc())
    )
    return result.scalars().all()


@router.get("/schedule", response_model=list[VaccineCreate])
async def generate_schedule(
    pet_id: int,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    if not pet.birthday:
        raise HTTPException(status_code=400, detail="需要先设置宠物生日才能生成接种计划")

    knowledge = _load_vaccine_knowledge()
    age_weeks = _age_weeks(pet.birthday)
    suggestions = []

    for item in knowledge:
        for entry in item["schedule"]:
            scheduled_date = None

            if "age" in entry:
                target_weeks = _parse_age_to_weeks(entry["age"])
                scheduled_date = pet.birthday + timedelta(weeks=target_weeks)
            elif "interval" in entry:
                if "每" in entry["interval"] and "月" in entry["interval"]:
                    freq_months = int(entry["interval"].replace("每", "").replace("月", "").replace("次", "").strip())
                    scheduled_date = date.today() + timedelta(days=freq_months * 30)
                elif "每年" in entry["interval"]:
                    scheduled_date = date.today() + timedelta(days=365)
                elif "每2周" in entry["interval"]:
                    scheduled_date = date.today() + timedelta(days=14)
                elif "每3个月" in entry["interval"]:
                    scheduled_date = date.today() + timedelta(days=90)
                else:
                    scheduled_date = date.today() + timedelta(days=30)

            if scheduled_date and scheduled_date >= date.today():
                suggestions.append(VaccineCreate(
                    type=item["type"],
                    name=item["name"],
                    scheduled_date=scheduled_date,
                    notes=entry.get("dose", ""),
                ))

    return suggestions


@router.get("/{vaccine_id}", response_model=VaccineOut)
async def get_vaccine(
    pet_id: int,
    vaccine_id: int,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vaccine).where(Vaccine.id == vaccine_id, Vaccine.pet_id == pet_id)
    )
    vaccine = result.scalar_one_or_none()
    if not vaccine:
        raise HTTPException(status_code=404, detail="疫苗记录不存在")
    return vaccine


@router.put("/{vaccine_id}", response_model=VaccineOut)
async def update_vaccine(
    pet_id: int,
    vaccine_id: int,
    req: VaccineUpdate,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vaccine).where(Vaccine.id == vaccine_id, Vaccine.pet_id == pet_id)
    )
    vaccine = result.scalar_one_or_none()
    if not vaccine:
        raise HTTPException(status_code=404, detail="疫苗记录不存在")

    update_data = req.model_dump(exclude_unset=True)
    if "actual_date" in update_data and update_data["actual_date"]:
        update_data["status"] = "completed"
    for key, value in update_data.items():
        setattr(vaccine, key, value)

    await db.commit()
    await db.refresh(vaccine)
    return vaccine


@router.delete("/{vaccine_id}")
async def delete_vaccine(
    pet_id: int,
    vaccine_id: int,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Vaccine).where(Vaccine.id == vaccine_id, Vaccine.pet_id == pet_id)
    )
    vaccine = result.scalar_one_or_none()
    if not vaccine:
        raise HTTPException(status_code=404, detail="疫苗记录不存在")
    await db.delete(vaccine)
    await db.commit()
    return {"detail": "已删除"}