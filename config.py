"""Конфигурация бота через переменные окружения"""

from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Конфигурация приложения"""

    telegram_token: str
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "openai/gpt-oss-20b:free"
    max_tokens: int = 1000
    temperature: float = 0.7
    max_context_messages: int = 10
    openai_timeout: int = 30


def load_config() -> Config:
    """Загрузить конфигурацию из переменных окружения"""
    config = Config(
        telegram_token=getenv("TELEGRAM_TOKEN", ""),
        openai_api_key=getenv("OPENAI_API_KEY", ""),
        openai_base_url=getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        openai_model=getenv("OPENAI_MODEL", "openai/gpt-oss-20b:free"),
        max_tokens=int(getenv("MAX_TOKENS", "1000")),
        temperature=float(getenv("TEMPERATURE", "0.7")),
        openai_timeout=int(getenv("OPENAI_TIMEOUT", "30")),
        max_context_messages=int(getenv("MAX_CONTEXT_MESSAGES", "10")),
    )

    if not config.telegram_token:
        raise ValueError("TELEGRAM_TOKEN не установлен в .env")

    if not config.openai_api_key:
        raise ValueError("OPENAI_API_KEY не установлен в .env")

    return config
