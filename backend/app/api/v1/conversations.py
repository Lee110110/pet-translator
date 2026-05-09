import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_pet
from app.core.utils import calculate_age, parse_llm_json
from app.models.pet import Pet
from app.models.checkin import Checkin
from app.models.conversation import Conversation, ConversationMessage
from app.schemas.conversation import (
    StartConversationRequest,
    ReplyRequest,
    ConversationOut,
    MessageOut,
)
from app.services.llm_service import chat_with_history, load_knowledge
from app.services.prompt_templates import CONVERSATION_SYSTEM, CONVERSATION_USER_TEMPLATE

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pets/{pet_id}/conversations", tags=["症状对话"])


@router.post("", response_model=ConversationOut)
async def start_conversation(
    pet_id: int,
    req: StartConversationRequest,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    conversation = Conversation(
        pet_id=pet_id,
        checkin_id=req.checkin_id,
        warning_level=req.warning_level or "yellow",
        status="active",
        max_rounds=3,
        current_round=0,
    )
    db.add(conversation)
    await db.flush()

    age = calculate_age(pet.birthday) if pet.birthday else "未知"
    breed = pet.breed or "未知品种"

    # Fetch checkin data if checkin_id provided
    checkin_data = ""
    diet_score = "?"
    water_score = "?"
    stool_score = "?"
    spirit_score = "?"

    if req.checkin_id:
        result = await db.execute(select(Checkin).where(Checkin.id == req.checkin_id))
        checkin = result.scalar_one_or_none()
        if checkin:
            diet_score = str(checkin.diet_score)
            water_score = str(checkin.water_score)
            stool_score = str(checkin.stool_score)
            spirit_score = str(checkin.spirit_score)

    symptom_knowledge = load_knowledge("cat_symptoms.json")

    system_prompt = CONVERSATION_SYSTEM.format(symptom_knowledge=symptom_knowledge)
    user_prompt = CONVERSATION_USER_TEMPLATE.format(
        breed=breed,
        age=age,
        diet_score=diet_score,
        water_score=water_score,
        stool_score=stool_score,
        spirit_score=spirit_score,
        warning_level=req.warning_level or "yellow",
        initial_symptoms=req.initial_symptoms,
        round_number=1,
    )

    try:
        llm_response = await chat_with_history(system_prompt, [
            {"role": "user", "content": user_prompt}
        ])
        ai_result = parse_llm_json(llm_response, default_level="yellow")
        ai_content = json.dumps(ai_result, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"LLM对话启动失败: {e}")
        ai_content = json.dumps({
            "question": "请描述一下你观察到的具体症状，比如呕吐的形态、频率、持续时间？",
            "options": ["呕吐", "不吃东西", "精神不好", "排便异常"],
            "assessment": "需要更多信息",
            "warning_level": "yellow",
        }, ensure_ascii=False)

    system_msg = ConversationMessage(
        conversation_id=conversation.id,
        role="system",
        content=f"对话开始 - 症状: {req.initial_symptoms}",
        round_number=0,
    )
    ai_msg = ConversationMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_content,
        round_number=1,
    )
    db.add(system_msg)
    db.add(ai_msg)

    conversation.current_round = 1
    await db.commit()
    await db.refresh(conversation)

    return await _conversation_to_out(conversation, db)


@router.post("/{conversation_id}/reply", response_model=ConversationOut)
async def reply_conversation(
    pet_id: int,
    conversation_id: int,
    req: ReplyRequest,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.pet_id == pet_id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    if conversation.status != "active":
        raise HTTPException(status_code=400, detail="对话已结束")
    if conversation.current_round >= conversation.max_rounds:
        raise HTTPException(status_code=400, detail="已达最大对话轮数")

    user_msg = ConversationMessage(
        conversation_id=conversation.id,
        role="user",
        content=req.content,
        round_number=conversation.current_round,
    )
    db.add(user_msg)

    next_round = conversation.current_round + 1
    is_final = next_round >= conversation.max_rounds

    result_msgs = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.created_at.asc())
    )
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in result_msgs.scalars().all()
    ]

    age = calculate_age(pet.birthday) if pet.birthday else "未知"
    breed = pet.breed or "未知品种"
    symptom_knowledge = load_knowledge("cat_symptoms.json")

    system_prompt = CONVERSATION_SYSTEM.format(symptom_knowledge=symptom_knowledge)
    user_prompt = CONVERSATION_USER_TEMPLATE.format(
        breed=breed,
        age=age,
        diet_score="见对话历史",
        water_score="见对话历史",
        stool_score="见对话历史",
        spirit_score="见对话历史",
        warning_level=conversation.warning_level,
        initial_symptoms="见对话历史",
        round_number=next_round,
    )
    if is_final:
        user_prompt += "\n\n这是最后一轮，请给出完整的最终评估和建议，不要继续提问。"

    try:
        llm_response = await chat_with_history(system_prompt, history + [
            {"role": "user", "content": user_prompt}
        ])
        ai_result = parse_llm_json(llm_response, default_level="yellow")
        ai_content = json.dumps(ai_result, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"LLM对话回复失败: {e}")
        ai_result = {
            "assessment": "基于当前信息，建议带猫咪就医检查",
            "warning_level": "orange",
            "recommendation": "建议48小时内就诊，进行血常规和生化检查",
        }
        ai_content = json.dumps(ai_result, ensure_ascii=False)

    ai_msg = ConversationMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_content,
        round_number=next_round,
    )
    db.add(ai_msg)

    conversation.current_round = next_round

    if is_final:
        conversation.status = "completed"
        if ai_result.get("assessment"):
            conversation.final_assessment = ai_result["assessment"]
        if ai_result.get("recommendation"):
            conversation.final_recommendation = ai_result["recommendation"]
        if ai_result.get("warning_level"):
            conversation.warning_level = ai_result["warning_level"]

    await db.commit()
    await db.refresh(conversation)
    return await _conversation_to_out(conversation, db)


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
    pet_id: int,
    conversation_id: int,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.pet_id == pet_id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    return await _conversation_to_out(conversation, db)


@router.get("", response_model=list[ConversationOut])
async def list_conversations(
    pet_id: int,
    pet: Pet = Depends(get_current_pet),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.pet_id == pet_id)
        .order_by(Conversation.created_at.desc())
        .limit(20)
    )
    conversations = result.scalars().all()
    out_list = []
    for conv in conversations:
        out_list.append(await _conversation_to_out(conv, db))
    return out_list


async def _conversation_to_out(conversation: Conversation, db: AsyncSession) -> dict:
    result = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation.id)
        .order_by(ConversationMessage.created_at.asc())
    )
    messages = result.scalars().all()
    return {
        "id": conversation.id,
        "pet_id": conversation.pet_id,
        "checkin_id": conversation.checkin_id,
        "warning_level": conversation.warning_level,
        "status": conversation.status,
        "max_rounds": conversation.max_rounds,
        "current_round": conversation.current_round,
        "final_assessment": conversation.final_assessment,
        "final_recommendation": conversation.final_recommendation,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "round_number": m.round_number,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
    }