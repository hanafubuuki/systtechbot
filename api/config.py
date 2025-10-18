"""Конфигурация API модуля"""

from dataclasses import dataclass
from os import getenv
from typing import Literal

from dotenv import load_dotenv

load_dotenv()


@dataclass
class APIConfig:
    """Конфигурация API для статистики

    Attributes:
        mode: Режим работы коллектора статистики (mock/real)
        host: Хост для запуска API
        port: Порт для запуска API
        mock_seed: Seed для Mock генератора (воспроизводимость данных)
        cors_origins: Список разрешенных origins для CORS
        database_url: URL подключения к PostgreSQL (для real режима)
    """

    mode: Literal["mock", "real"] = "real"  # По умолчанию используем real данные
    host: str = "0.0.0.0"
    port: int = 8000
    mock_seed: int = 42
    cors_origins: list[str] | None = None
    database_url: str = ""


def load_api_config() -> APIConfig:
    """Загрузить конфигурацию API из переменных окружения

    Returns:
        APIConfig с настройками из environment

    Raises:
        ValueError: Если DATABASE_URL не установлен в real режиме
    """
    mode = getenv("API_MODE", "real")  # По умолчанию real
    if mode not in ["mock", "real"]:
        mode = "real"

    # CORS origins - разделенные запятыми
    cors_origins_str = getenv("API_CORS_ORIGINS", "*")
    cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

    database_url = getenv("DATABASE_URL", "")

    config = APIConfig(
        mode=mode,  # type: ignore
        host=getenv("API_HOST", "0.0.0.0"),
        port=int(getenv("API_PORT", "8000")),
        mock_seed=int(getenv("API_MOCK_SEED", "42")),
        cors_origins=cors_origins,
        database_url=database_url,
    )

    # Валидация для real режима
    if config.mode == "real" and not config.database_url:
        raise ValueError("DATABASE_URL должен быть установлен для API_MODE=real")

    return config
