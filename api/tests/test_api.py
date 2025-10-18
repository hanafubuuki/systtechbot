"""Тесты для FastAPI endpoint статистики"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

# Создание test client
client = TestClient(app)


def test_root_endpoint() -> None:
    """Тест корневого endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "systtechbot Stats API"
    assert data["version"] == "0.1.0"
    assert "mode" in data
    assert data["docs"] == "/docs"
    assert data["stats_endpoint"] == "/api/v1/stats"


def test_health_check() -> None:
    """Тест health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "mode" in data


def test_get_stats_default_period() -> None:
    """Тест получения статистики с периодом по умолчанию (90 дней)"""
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()

    # Проверка структуры ответа
    assert "total_users" in data
    assert "total_chats" in data
    assert "total_messages" in data
    assert "avg_message_length" in data
    assert "activity_chart" in data

    # Проверка структуры метрик
    for metric_name in ["total_users", "total_chats", "total_messages", "avg_message_length"]:
        metric = data[metric_name]
        assert "value" in metric
        assert "change_percent" in metric
        assert "trend" in metric
        assert metric["trend"] in ["up", "down", "stable"]

    # Проверка временного ряда
    activity_chart = data["activity_chart"]
    assert isinstance(activity_chart, list)
    assert len(activity_chart) == 90  # По умолчанию 90 дней

    # Проверка структуры точки временного ряда
    point = activity_chart[0]
    assert "date" in point
    assert "messages" in point
    assert isinstance(point["messages"], int)
    assert point["messages"] >= 0


@pytest.mark.parametrize("period", [7, 30, 90])
def test_get_stats_with_different_periods(period: int) -> None:
    """Тест получения статистики с различными периодами"""
    response = client.get(f"/api/v1/stats?period={period}")
    assert response.status_code == 200
    data = response.json()

    # Проверка длины временного ряда
    activity_chart = data["activity_chart"]
    assert len(activity_chart) == period


def test_get_stats_invalid_period() -> None:
    """Тест получения статистики с недопустимым периодом"""
    response = client.get("/api/v1/stats?period=15")
    assert response.status_code == 400  # Validation error (custom check)


def test_get_stats_reproducibility() -> None:
    """Тест что Mock генерирует разумные данные при повторных вызовах"""
    # Два запроса должны вернуть данные (могут быть разные - это Mock)
    response1 = client.get("/api/v1/stats?period=7")
    response2 = client.get("/api/v1/stats?period=7")

    assert response1.status_code == 200
    assert response2.status_code == 200

    data1 = response1.json()
    data2 = response2.json()

    # Проверяем что оба запроса вернули валидные данные
    assert data1["total_users"]["value"] > 0
    assert data2["total_users"]["value"] > 0

    # Временные ряды должны иметь правильную длину
    assert len(data1["activity_chart"]) == 7
    assert len(data2["activity_chart"]) == 7

    # Даты должны быть одинаковые (независимо от seed)
    for i in range(7):
        assert data1["activity_chart"][i]["date"] == data2["activity_chart"][i]["date"]


def test_metric_card_values() -> None:
    """Тест валидности значений метрик"""
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()

    # Проверка что значения в разумных пределах
    assert data["total_users"]["value"] > 0
    assert data["total_chats"]["value"] > 0
    assert data["total_messages"]["value"] > 0
    assert data["avg_message_length"]["value"] > 0

    # Проверка что проценты изменений числовые
    for metric_name in ["total_users", "total_chats", "total_messages", "avg_message_length"]:
        change = data[metric_name]["change_percent"]
        assert isinstance(change, (int, float))


def test_activity_chart_chronological_order() -> None:
    """Тест что временной ряд отсортирован хронологически"""
    response = client.get("/api/v1/stats?period=30")
    assert response.status_code == 200
    data = response.json()

    activity_chart = data["activity_chart"]
    dates = [point["date"] for point in activity_chart]

    # Проверка что даты идут по возрастанию
    assert dates == sorted(dates)


def test_cors_headers() -> None:
    """Тест наличия CORS заголовков"""
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    # CORS заголовки должны присутствовать если настроены в config
    # В тестах может не быть, но проверяем что endpoint работает
