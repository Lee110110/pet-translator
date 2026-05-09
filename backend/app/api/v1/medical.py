from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_pet
from app.core.utils import calculate_age, parse_llm_json
from app.models.pet import Pet
from app.models.checkin import Checkin
from app.models.baseline import Baseline
from app.models.warning import Warning
from app.models.conversation import Conversation
from app.schemas.medical import MedicalSummaryRequest, MedicalSummaryOut
from app.services.llm_service import chat_completion
from app.services.prompt_templates import MEDICAL_SUMMARY_SYSTEM, MEDICAL_SUMMARY_USER_TEMPLATE

router = APIRouter(prefix="/pets/{pet_id}/medical", tags=["就医助手"])


@router.post("/summary", response_model=MedicalSummaryOut)
async def generate_medical_summary(
    pet_id: int,
    req: MedicalSummaryRequest,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    end_date = req.end_date or date.today()
    start_date = req.start_date or (end_date - timedelta(days=7))
    days = (end_date - start_date).days or 7

    # Gather checkin data
    result = await db.execute(
        select(Checkin)
        .where(Checkin.pet_id == pet_id, Checkin.checkin_date >= start_date, Checkin.checkin_date <= end_date)
        .order_by(Checkin.checkin_date.asc())
    )
    checkins = result.scalars().all()
    checkin_data = "\n".join(
        f"- {c.checkin_date.isoformat()}: 饮食{c.diet_score}/5, 饮水{c.water_score}/5, "
        f"排便{c.stool_score}/5, 精神{c.spirit_score}/5"
        + (f" | AI解读: {c.ai_interpretation}" if c.ai_interpretation else "")
        for c in checkins
    ) or "无打卡数据"

    # Gather baseline data
    result = await db.execute(select(Baseline).where(Baseline.pet_id == pet_id))
    baselines = result.scalars().all()
    baseline_data = "\n".join(
        f"- {b.metric_type}: 基线值{b.baseline_value}±{b.std_deviation} (已建立: {b.is_established})"
        for b in baselines
    ) or "未建立基线"

    # Gather warning data
    result = await db.execute(
        select(Warning)
        .where(Warning.pet_id == pet_id)
        .order_by(Warning.created_at.desc())
        .limit(10)
    )
    warnings = result.scalars().all()
    warning_data = "\n".join(
        f"- [{w.level}] {w.created_at.date()}: {w.message}"
        for w in warnings
    ) or "无预警记录"

    # Gather conversation conclusions
    result = await db.execute(
        select(Conversation)
        .where(Conversation.pet_id == pet_id, Conversation.status == "completed")
        .order_by(Conversation.created_at.desc())
        .limit(5)
    )
    conversations = result.scalars().all()
    conversation_data = "\n".join(
        f"- 对话{c.id}: 最终评估={c.final_assessment}, 建议={c.final_recommendation}"
        for c in conversations
    ) or "无对话记录"

    breed = pet.breed or "未知品种"
    age = calculate_age(pet.birthday) if pet.birthday else "未知"

    user_prompt = MEDICAL_SUMMARY_USER_TEMPLATE.format(
        breed=breed,
        age=age,
        weight_kg=pet.weight_kg or "未知",
        gender=pet.gender or "未知",
        visit_reason=req.visit_reason or "定期检查",
        days=days,
        checkin_data=checkin_data,
        baseline_data=baseline_data,
        warning_data=warning_data,
        conversation_data=conversation_data,
    )

    try:
        llm_response = await chat_completion(MEDICAL_SUMMARY_SYSTEM, user_prompt, max_tokens=2048)
        result = parse_llm_json(llm_response)
    except Exception:
        result = {
            "summary_text": f"{breed}{age}，近{days}天健康数据汇总",
            "key_findings": [],
            "recommendations": [],
            "warning_history_summary": warning_data,
            "suggested_tests": [],
        }

    from datetime import datetime
    return MedicalSummaryOut(
        summary_text=result.get("summary_text", ""),
        key_findings=result.get("key_findings", []),
        recommendations=result.get("recommendations", []),
        warning_history_summary=result.get("warning_history_summary", ""),
        suggested_tests=result.get("suggested_tests", []),
        generated_at=datetime.now(),
    )