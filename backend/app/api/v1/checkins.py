import json
import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user, get_current_pet
from app.core.utils import calculate_age, parse_llm_json
from app.models.user import User
from app.models.pet import Pet
from app.models.checkin import Checkin
from app.models.warning import Warning
from app.schemas.checkin import CheckinCreate, CheckinUpdate, CheckinOut
from app.services.warning_service import determine_warning_level
from app.services.baseline_service import calculate_baseline, check_deviations
from app.services.llm_service import chat_completion
from app.services.prompt_templates import CHECKIN_SYSTEM, CHECKIN_USER_TEMPLATE, BASELINE_WARNING_TEMPLATE

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pets/{pet_id}/checkins", tags=["每日打卡"])


@router.post("", response_model=CheckinOut)
async def create_checkin(
    pet_id: int,
    req: CheckinCreate,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(Checkin).where(Checkin.pet_id == pet_id, Checkin.checkin_date == date.today())
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="今日已打卡，请使用更新功能")

    checkin = Checkin(
        pet_id=pet_id,
        checkin_date=date.today(),
        **req.model_dump(),
    )
    db.add(checkin)
    await db.flush()

    await _process_checkin_ai(checkin, pet, db, req.note)

    await db.commit()
    await db.refresh(checkin)
    return checkin


@router.put("/{checkin_id}", response_model=CheckinOut)
async def update_checkin(
    pet_id: int,
    checkin_id: int,
    req: CheckinUpdate,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Checkin).where(Checkin.id == checkin_id, Checkin.pet_id == pet_id)
    )
    checkin = result.scalar_one_or_none()
    if not checkin:
        raise HTTPException(status_code=404, detail="打卡记录不存在")

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(checkin, key, value)

    await db.flush()

    note = checkin.note
    await _process_checkin_ai(checkin, pet, db, note)

    await db.commit()
    await db.refresh(checkin)
    return checkin


@router.get("", response_model=list[CheckinOut])
async def list_checkins(
    pet_id: int,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Checkin)
        .where(Checkin.pet_id == pet_id)
        .order_by(Checkin.checkin_date.desc())
        .limit(30)
    )
    return result.scalars().all()


@router.get("/latest", response_model=CheckinOut | None)
async def get_latest_checkin(
    pet_id: int,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Checkin)
        .where(Checkin.pet_id == pet_id)
        .order_by(Checkin.checkin_date.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _process_checkin_ai(checkin: Checkin, pet: Pet, db: AsyncSession, note: str | None):
    """Process checkin with AI: deviations, LLM interpretation, baseline recalc, warnings."""
    pet_id = checkin.pet_id

    deviations = await check_deviations(pet_id, checkin, db)
    warning_level, warning_message = determine_warning_level(checkin, deviations)

    age = calculate_age(pet.birthday) if pet.birthday else "未知"
    breed = pet.breed or "未知品种"

    try:
        user_prompt = CHECKIN_USER_TEMPLATE.format(
            breed=breed,
            age=age,
            diet_score=checkin.diet_score,
            diet_note=checkin.diet_note or "",
            water_score=checkin.water_score,
            water_note=checkin.water_note or "",
            stool_score=checkin.stool_score,
            stool_note=checkin.stool_note or "",
            spirit_score=checkin.spirit_score,
            spirit_note=checkin.spirit_note or "",
            note=note or "",
        )

        llm_response = await chat_completion(CHECKIN_SYSTEM, user_prompt)
        ai_result = parse_llm_json(llm_response)

        checkin.ai_interpretation = ai_result.get("interpretation", "")
        checkin.ai_warning_level = ai_result.get("warning_level", warning_level)
        checkin.ai_confidence = ai_result.get("confidence", 0.8)

        if ai_result.get("recommendation"):
            checkin.note = f"{checkin.note or ''}\n[AI建议]: {ai_result['recommendation']}"

        # If baseline deviations exist, get a baseline-specific interpretation
        if deviations:
            try:
                deviation_details = "；".join(
                    f"{m}: 实际{d['actual']}, 基线{d['baseline']}, 偏离{d['sigma']}σ"
                    for m, d in deviations.items()
                )
                baseline_values = "；".join(
                    f"{m}: {d['baseline']}±σ"
                    for m, d in deviations.items()
                )
                baseline_prompt = BASELINE_WARNING_TEMPLATE.format(
                    breed=breed,
                    deviation_details=deviation_details,
                    baseline_values=baseline_values,
                )
                baseline_response = await chat_completion(CHECKIN_SYSTEM, baseline_prompt)
                baseline_result = parse_llm_json(baseline_response, default_level="yellow")
                if baseline_result.get("interpretation"):
                    checkin.ai_interpretation = (
                        f"{checkin.ai_interpretation}\n[基线偏离]: {baseline_result['interpretation']}"
                    )
                if baseline_result.get("warning_level") and baseline_result["warning_level"] not in ("green", warning_level):
                    checkin.ai_warning_level = baseline_result["warning_level"]
            except Exception as e:
                logger.warning(f"基线偏离LLM解读失败: {e}")

        final_level = checkin.ai_warning_level or warning_level

    except Exception as e:
        logger.warning(f"LLM解读失败: {e}, 使用规则引擎结果")
        checkin.ai_interpretation = warning_message
        checkin.ai_warning_level = warning_level
        checkin.ai_confidence = 0.5
        final_level = warning_level

    for metric in ["diet", "water", "stool", "spirit"]:
        await calculate_baseline(pet_id, metric, db)

    if final_level != "green":
        warning = Warning(
            pet_id=pet_id,
            checkin_id=checkin.id,
            level=final_level,
            trigger_type="checkin",
            trigger_detail=json.dumps(deviations, ensure_ascii=False) if deviations else None,
            message=checkin.ai_interpretation or warning_message,
            is_notified=True,
        )
        db.add(warning)