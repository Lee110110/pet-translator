import json
from openai import AsyncOpenAI
from app.core.config import get_settings

_settings = get_settings()

_client = AsyncOpenAI(
    api_key=_settings.LLM_API_KEY or "sk-placeholder",
    base_url=_settings.LLM_BASE_URL,
)


async def chat_completion(system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> str:
    """通用LLM对话接口"""
    response = await _client.chat.completions.create(
        model=_settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content


async def chat_with_history(system_prompt: str, messages: list[dict], max_tokens: int = 2048) -> str:
    """带历史消息的LLM对话接口"""
    all_messages = [{"role": "system", "content": system_prompt}] + messages
    response = await _client.chat.completions.create(
        model=_settings.LLM_MODEL,
        messages=all_messages,
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content


def load_knowledge(filename: str) -> str:
    """加载知识库JSON文件，返回格式化文本"""
    import pathlib
    path = pathlib.Path(__file__).parent.parent / "knowledge" / filename
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, ensure_ascii=False, indent=2)