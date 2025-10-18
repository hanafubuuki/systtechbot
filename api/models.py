"""Pydantic модели для API контракта дашборда статистики"""

from datetime import date as dt_date
from typing import Literal

from pydantic import BaseModel, Field


class MetricCard(BaseModel):
    """Карточка метрики с трендом

    Attributes:
        value: Текущее значение метрики
        change_percent: Изменение в процентах относительно предыдущего периода
        trend: Направление тренда (up/down/stable)
    """

    value: int | float = Field(..., description="Текущее значение метрики")
    change_percent: float = Field(
        ..., description="Изменение в процентах относительно предыдущего периода"
    )
    trend: Literal["up", "down", "stable"] = Field(..., description="Направление тренда")

    model_config = {
        "json_schema_extra": {"example": {"value": 1234, "change_percent": 12.5, "trend": "up"}}
    }


class TimeSeriesPoint(BaseModel):
    """Точка временного ряда активности

    Attributes:
        date: Дата
        messages: Количество сообщений за этот день
    """

    date: dt_date = Field(..., description="Дата")
    messages: int = Field(..., ge=0, description="Количество сообщений")

    model_config = {"json_schema_extra": {"example": {"date": "2025-10-17", "messages": 142}}}


class DashboardStats(BaseModel):
    """Полная статистика для дашборда

    Содержит метрики и временной ряд активности для отображения на дашборде.

    Attributes:
        total_users: Метрика общего количества пользователей
        total_chats: Метрика общего количества диалогов
        total_messages: Метрика общего количества сообщений
        avg_message_length: Метрика средней длины сообщения
        activity_chart: Временной ряд сообщений по дням
    """

    total_users: MetricCard = Field(..., description="Общее количество пользователей")
    total_chats: MetricCard = Field(..., description="Общее количество диалогов")
    total_messages: MetricCard = Field(..., description="Общее количество сообщений")
    avg_message_length: MetricCard = Field(..., description="Средняя длина сообщения в символах")
    activity_chart: list[TimeSeriesPoint] = Field(
        ..., description="Временной ряд сообщений по дням"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_users": {"value": 1234, "change_percent": 12.5, "trend": "up"},
                "total_chats": {"value": 45678, "change_percent": -20.0, "trend": "down"},
                "total_messages": {"value": 89012, "change_percent": 5.3, "trend": "up"},
                "avg_message_length": {"value": 125.5, "change_percent": 0.8, "trend": "stable"},
                "activity_chart": [
                    {"date": "2025-10-15", "messages": 120},
                    {"date": "2025-10-16", "messages": 135},
                    {"date": "2025-10-17", "messages": 142},
                ],
            }
        }
    }
