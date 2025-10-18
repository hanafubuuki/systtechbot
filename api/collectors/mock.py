"""Mock реализация StatCollector для генерации тестовых данных"""

import random
from datetime import date, timedelta
from typing import Literal

from faker import Faker

from api.collectors.base import StatCollector
from api.models import DashboardStats, MetricCard, TimeSeriesPoint


class MockStatCollector(StatCollector):
    """Mock реализация для генерации реалистичных тестовых данных

    Генерирует воспроизводимые данные с помощью Faker с фиксированным seed.
    Используется для разработки frontend до готовности реальной БД.

    Attributes:
        seed: Seed для генератора случайных чисел (для воспроизводимости)
        fake: Экземпляр Faker для генерации данных
    """

    def __init__(self, seed: int = 42) -> None:
        """Инициализация Mock коллектора

        Args:
            seed: Seed для генератора случайных чисел
        """
        self.seed = seed
        self.fake = Faker()
        Faker.seed(seed)
        random.seed(seed)

    async def get_dashboard_stats(self, period_days: int = 90) -> DashboardStats:
        """Получить mock статистику для дашборда

        Args:
            period_days: Период в днях для временных рядов (7, 30, 90)

        Returns:
            DashboardStats с сгенерированными данными

        Raises:
            ValueError: Если period_days не из допустимых значений
        """
        if period_days not in [7, 30, 90]:
            raise ValueError(f"period_days должен быть 7, 30 или 90, получено: {period_days}")

        # Генерация базовых значений метрик
        total_users = random.randint(800, 2000)
        total_chats = random.randint(1000, 3000)
        total_messages = random.randint(10000, 50000)
        avg_message_length = round(random.uniform(80.0, 200.0), 1)

        # Генерация трендов для метрик
        return DashboardStats(
            total_users=self._generate_metric_card(total_users, "users"),
            total_chats=self._generate_metric_card(total_chats, "chats"),
            total_messages=self._generate_metric_card(total_messages, "messages"),
            avg_message_length=self._generate_metric_card(avg_message_length, "length"),
            activity_chart=self._generate_activity_chart(period_days),
        )

    def _generate_metric_card(self, value: int | float, metric_type: str) -> MetricCard:
        """Генерация карточки метрики с трендом

        Args:
            value: Значение метрики
            metric_type: Тип метрики для разнообразия трендов

        Returns:
            MetricCard с трендом
        """
        # Генерация изменения в процентах с разным распределением для разных метрик
        if metric_type == "users":
            change_percent = random.uniform(5.0, 20.0)  # Обычно растет
        elif metric_type == "chats":
            change_percent = random.uniform(-25.0, 15.0)  # Может падать
        elif metric_type == "messages":
            change_percent = random.uniform(0.0, 15.0)  # Обычно стабилен или растет
        else:  # length
            change_percent = random.uniform(-3.0, 3.0)  # Обычно стабилен

        # Определение тренда
        trend: Literal["up", "down", "stable"]
        if change_percent > 1.0:
            trend = "up"
        elif change_percent < -1.0:
            trend = "down"
        else:
            trend = "stable"

        return MetricCard(value=value, change_percent=round(change_percent, 1), trend=trend)

    def _generate_activity_chart(self, period_days: int) -> list[TimeSeriesPoint]:
        """Генерация временного ряда активности сообщений

        Args:
            period_days: Количество дней для генерации

        Returns:
            Список точек временного ряда с колебаниями
        """
        today = date.today()
        points: list[TimeSeriesPoint] = []

        # Базовое количество сообщений в день
        base_messages = random.randint(100, 300)

        for i in range(period_days):
            current_date = today - timedelta(days=period_days - i - 1)

            # Добавляем волнообразные колебания + случайный шум
            day_of_week = current_date.weekday()

            # Меньше активности в выходные
            weekend_factor = 0.7 if day_of_week >= 5 else 1.0

            # Волнообразный тренд (синусоида)
            wave = 1.0 + 0.3 * random.uniform(-1, 1) * (i / period_days)

            # Случайный шум
            noise = random.uniform(0.8, 1.2)

            messages = int(base_messages * weekend_factor * wave * noise)
            messages = max(10, messages)  # Минимум 10 сообщений

            points.append(TimeSeriesPoint(date=current_date, messages=messages))

        return points
