"""FastAPI приложение для статистики диалогов systtechbot"""

import logging

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from api.collectors.base import StatCollector
from api.collectors.mock import MockStatCollector
from api.config import load_api_config
from api.models import DashboardStats
from config import load_config as load_main_config
from services.analytics import process_analytics_query
from services.context import clear_context, get_context, save_context
from services.database import close_db, init_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Загрузка конфигурации
config = load_api_config()

# Создание FastAPI приложения
app = FastAPI(
    title="systtechbot Stats API",
    description="API для получения статистики диалогов Telegram-бота systtechbot",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Настройка CORS
if config.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS включен для origins: {config.cors_origins}")

# Инициализация коллектора статистики
collector: StatCollector
if config.mode == "mock":
    collector = MockStatCollector(seed=config.mock_seed)
    logger.info(f"Используется MockStatCollector с seed={config.mock_seed}")
else:
    from api.collectors.real import RealStatCollector
    collector = RealStatCollector()
    logger.info("Используется RealStatCollector для реальных данных из БД")


# ===== Pydantic модели для Chat API =====

class ChatMessage(BaseModel):
    """Сообщение в чате

    Attributes:
        role: Роль отправителя (user или assistant)
        content: Текст сообщения
    """
    role: str = Field(..., description="Роль: user или assistant")
    content: str = Field(..., description="Текст сообщения")


class ChatRequest(BaseModel):
    """Запрос для отправки сообщения в чат

    Attributes:
        user_id: ID пользователя (виртуальный для веб-чата)
        message: Текст сообщения от пользователя
        history: История диалога (опционально)
    """
    user_id: int = Field(..., description="ID пользователя", ge=1)
    message: str = Field(..., description="Текст сообщения", min_length=1)
    history: list[ChatMessage] = Field(default=[], description="История диалога")


class ChatResponse(BaseModel):
    """Ответ от чата

    Attributes:
        response: Ответ ассистента
        sql_executed: SQL запрос который был выполнен (для отладки)
    """
    response: str = Field(..., description="Ответ ассистента")
    sql_executed: str | None = Field(None, description="Выполненный SQL (для отладки)")


class ClearHistoryRequest(BaseModel):
    """Запрос на очистку истории чата"""
    user_id: int = Field(..., description="ID пользователя", ge=1)


# Lifecycle events для управления подключением к БД
@app.on_event("startup")
async def startup_event() -> None:
    """Инициализация при запуске приложения"""
    if config.mode == "real":
        logger.info("Инициализация подключения к БД...")
        try:
            await init_db()
            logger.info("✅ Подключение к БД успешно установлено")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к БД: {e}")
            raise


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Очистка ресурсов при остановке приложения"""
    if config.mode == "real":
        logger.info("Закрытие подключения к БД...")
        await close_db()
        logger.info("✅ Подключение к БД закрыто")


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Корневой endpoint с информацией об API

    Returns:
        Информация о сервисе и доступных endpoints
    """
    return {
        "service": "systtechbot Stats API",
        "version": "0.1.0",
        "mode": config.mode,
        "docs": "/docs",
        "stats_endpoint": "/api/v1/stats",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint

    Returns:
        Статус здоровья сервиса
    """
    return {"status": "healthy", "mode": config.mode}


@app.get(
    "/api/v1/stats",
    response_model=DashboardStats,
    tags=["Statistics"],
    summary="Получить статистику для дашборда",
    description="""
    Возвращает полную статистику диалогов для отображения на дашборде.

    Включает:
    - Метрики: пользователи, диалоги, сообщения, средняя длина
    - Временной ряд активности сообщений по дням

    Поддерживаемые периоды: 7, 30, 90 дней
    """,
)
async def get_stats(
    period: int = Query(
        default=90,
        description="Период в днях для временного ряда (7, 30 или 90)",
        ge=7,
        le=90,
    ),
) -> DashboardStats:
    """Получить статистику для дашборда

    Args:
        period: Период в днях (7, 30 или 90)

    Returns:
        DashboardStats с метриками и временным рядом

    Raises:
        HTTPException: При ошибке получения статистики
    """
    # Валидация допустимых значений
    if period not in [7, 30, 90]:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимое значение period. Допустимые значения: 7, 30, 90. Получено: {period}",
        )

    try:
        logger.info(f"Запрос статистики за {period} дней")
        stats = await collector.get_dashboard_stats(period_days=period)
        logger.info(f"Статистика успешно получена: {len(stats.activity_chart)} точек")
        return stats
    except ValueError as e:
        logger.error(f"Ошибка валидации: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении статистики") from e


@app.post(
    "/api/v1/chat",
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Отправить сообщение в аналитический чат",
    description="""
    Обработать сообщение пользователя в аналитическом чате.

    Чат поддерживает:
    - Аналитические запросы на естественном языке
    - Автоматическую генерацию SQL запросов
    - Выполнение запросов к БД и формирование ответов

    История диалога сохраняется в БД для каждого user_id.
    """,
)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Обработать сообщение в аналитическом чате

    Args:
        request: Запрос с сообщением пользователя

    Returns:
        Ответ от ассистента

    Raises:
        HTTPException: При ошибке обработки сообщения
    """
    try:
        logger.info(f"Получен chat запрос от user_id={request.user_id}")

        # Загружаем главную конфигурацию для LLM
        main_config = load_main_config()

        # Получаем контекст из БД
        # Используем user_id как telegram_user_id и chat_id
        context = await get_context(request.user_id, request.user_id)
        messages = context.get("messages", [])

        # Обрабатываем аналитический запрос
        response, sql_executed = await process_analytics_query(
            request.message,
            messages,
            main_config
        )

        # Сохраняем контекст (user message + assistant response)
        from constants import MessageRole
        messages.append({"role": MessageRole.USER, "content": request.message})
        messages.append({"role": MessageRole.ASSISTANT, "content": response})

        await save_context(
            request.user_id,
            request.user_id,
            messages,
            f"WebUser_{request.user_id}",
            main_config.max_context_messages
        )

        logger.info(f"Chat запрос обработан успешно для user_id={request.user_id}")

        return ChatResponse(response=response, sql_executed=sql_executed)

    except Exception as e:
        logger.error(f"Ошибка обработки chat запроса: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке сообщения: {str(e)}"
        ) from e


@app.post(
    "/api/v1/chat/clear",
    tags=["Chat"],
    summary="Очистить историю чата",
    description="Очистить всю историю диалога для указанного пользователя.",
)
async def clear_chat_history(request: ClearHistoryRequest) -> dict[str, str]:
    """Очистить историю чата для пользователя

    Args:
        request: Запрос с user_id

    Returns:
        Сообщение об успешной очистке

    Raises:
        HTTPException: При ошибке очистки
    """
    try:
        logger.info(f"Очистка истории чата для user_id={request.user_id}")

        # Очищаем контекст (используем user_id как telegram_user_id и chat_id)
        await clear_context(request.user_id, request.user_id)

        logger.info(f"История чата очищена для user_id={request.user_id}")

        return {"status": "success", "message": "История чата успешно очищена"}

    except Exception as e:
        logger.error(f"Ошибка очистки истории чата: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при очистке истории: {str(e)}"
        ) from e


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Запуск API в режиме {config.mode}")
    logger.info(f"📚 Документация: http://{config.host}:{config.port}/docs")
    uvicorn.run(
        "api.main:app",
        host=config.host,
        port=config.port,
        reload=True,
        log_level="info",
    )
