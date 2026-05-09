import json
from datetime import date


def calculate_age(birthday: date) -> str:
    """计算宠物年龄，返回中文描述"""
    age_days = (date.today() - birthday).days
    if age_days < 365:
        return f"{age_days // 30}个月"
    return f"{age_days // 365}岁"


def parse_llm_json(text: str, default_level: str = "green") -> dict:
    """解析 LLM 返回的 JSON，兼容 markdown code fence 包裹"""
    try:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {"assessment": text, "warning_level": default_level, "recommendation": "建议继续观察"}