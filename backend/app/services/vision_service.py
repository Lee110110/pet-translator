import json
import base64
import pathlib
from openai import AsyncOpenAI
from app.core.config import get_settings
from app.core.utils import parse_llm_json
from app.services.prompt_templates import FOOD_BOWL_ANALYSIS, LITTER_BOX_ANALYSIS, VOMIT_ANALYSIS

_settings = get_settings()

_vision_client = AsyncOpenAI(
    api_key=_settings.VISION_API_KEY or _settings.LLM_API_KEY or "sk-placeholder",
    base_url=_settings.VISION_BASE_URL or _settings.LLM_BASE_URL,
)

ANALYSIS_PROMPTS = {
    "food_bowl": FOOD_BOWL_ANALYSIS,
    "litter_box": LITTER_BOX_ANALYSIS,
    "vomit": VOMIT_ANALYSIS,
}


async def analyze_image(image_path: str, analysis_type: str, pet_context: dict | None = None) -> dict:
    """Analyze an uploaded pet image using the vision model."""
    prompt = ANALYSIS_PROMPTS.get(analysis_type)
    if not prompt:
        return {"error": f"不支持的分析类型: {analysis_type}"}

    # Read and encode image
    path = pathlib.Path(image_path)
    if not path.exists():
        return {"error": "图片文件不存在"}

    with open(path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    media_type = "image/jpeg"
    if path.suffix == ".png":
        media_type = "image/png"
    elif path.suffix == ".webp":
        media_type = "image/webp"

    context_text = ""
    if pet_context:
        context_text = f"\n\n猫咪信息：品种{pet_context.get('breed', '未知')}, 年龄{pet_context.get('age', '未知')}"

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt + context_text},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_type};base64,{image_data}",
                    },
                },
            ],
        }
    ]

    try:
        response = await _vision_client.chat.completions.create(
            model=_settings.VISION_MODEL or _settings.LLM_MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.3,
        )
        result_text = response.choices[0].message.content
        return parse_llm_json(result_text, default_level="green")
    except Exception as e:
        return {"error": str(e)}