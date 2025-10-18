"""Real реализация StatCollector для сбора статистики из PostgreSQL"""

import logging
from datetime import date, timedelta
from typing import Any, Literal

from api.collectors.base import StatCollector
from api.models import DashboardStats, MetricCard, TimeSeriesPoint
from services.database import get_pool

logger = logging.getLogger(__name__)


class RealStatCollector(StatCollector):
    """Real реализация для сбора статистики из PostgreSQL

    Собирает реальные данные из БД:
    - users, chats, messages таблицы
    - Расчет метрик и трендов
    - Временные ряды активности
    """

    async def get_dashboard_stats(self, period_days: int = 90) -> DashboardStats:
        """Получить статистику для дашборда из БД

        Args:
            period_days: Период в днях для временных рядов (7, 30, 90)

        Returns:
            DashboardStats с реальными данными из БД

        Raises:
            ValueError: Если period_days не из допустимых значений
        """
        if period_days not in [7, 30, 90]:
            raise ValueError(f"period_days должен быть 7, 30 или 90, получено: {period_days}")

        logger.info(f"Collecting real stats for period: {period_days} days")

        pool = await get_pool()

        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                # Получение всех метрик
                total_users = await self._get_total_users(cur, period_days)
                total_chats = await self._get_total_chats(cur, period_days)
                total_messages = await self._get_total_messages(cur, period_days)
                avg_message_length = await self._get_avg_message_length(cur, period_days)
                activity_chart = await self._get_activity_chart(cur, period_days)

        logger.info(
            f"Stats collected: users={total_users.value}, chats={total_chats.value}, "
            f"messages={total_messages.value}, avg_length={avg_message_length.value}"
        )

        return DashboardStats(
            total_users=total_users,
            total_chats=total_chats,
            total_messages=total_messages,
            avg_message_length=avg_message_length,
            activity_chart=activity_chart,
        )

    async def _get_total_users(self, cur: Any, period_days: int) -> MetricCard:
        """Получить метрику общего количества пользователей с трендом"""
        # Текущее значение
        await cur.execute(
            "SELECT COUNT(*) FROM users WHERE deleted_at IS NULL"
        )
        result = await cur.fetchone()
        current = result[0] if result else 0

        # Предыдущий период
        await cur.execute(
            """
            SELECT COUNT(*) FROM users
            WHERE deleted_at IS NULL
            AND created_at < (CURRENT_DATE - INTERVAL '%s days')
            """,
            (period_days,)
        )
        result = await cur.fetchone()
        previous = result[0] if result else 0

        return self._calculate_metric_card(current, previous)

    async def _get_total_chats(self, cur: Any, period_days: int) -> MetricCard:
        """Получить метрику общего количества диалогов с трендом"""
        # Текущее значение
        await cur.execute(
            "SELECT COUNT(*) FROM chats WHERE deleted_at IS NULL"
        )
        result = await cur.fetchone()
        current = result[0] if result else 0

        # Предыдущий период
        await cur.execute(
            """
            SELECT COUNT(*) FROM chats
            WHERE deleted_at IS NULL
            AND created_at < (CURRENT_DATE - INTERVAL '%s days')
            """,
            (period_days,)
        )
        result = await cur.fetchone()
        previous = result[0] if result else 0

        return self._calculate_metric_card(current, previous)

    async def _get_total_messages(self, cur: Any, period_days: int) -> MetricCard:
        """Получить метрику общего количества сообщений с трендом"""
        # Текущее значение
        await cur.execute(
            "SELECT COUNT(*) FROM messages WHERE deleted_at IS NULL"
        )
        result = await cur.fetchone()
        current = result[0] if result else 0

        # Предыдущий период
        await cur.execute(
            """
            SELECT COUNT(*) FROM messages
            WHERE deleted_at IS NULL
            AND created_at < (CURRENT_DATE - INTERVAL '%s days')
            """,
            (period_days,)
        )
        result = await cur.fetchone()
        previous = result[0] if result else 0

        return self._calculate_metric_card(current, previous)

    async def _get_avg_message_length(self, cur: Any, period_days: int) -> MetricCard:
        """Получить метрику средней длины сообщения с трендом"""
        # Текущее значение
        await cur.execute(
            "SELECT AVG(length) FROM messages WHERE deleted_at IS NULL"
        )
        result = await cur.fetchone()
        current = float(result[0]) if result and result[0] is not None else 0.0

        # Предыдущий период
        await cur.execute(
            """
            SELECT AVG(length) FROM messages
            WHERE deleted_at IS NULL
            AND created_at < (CURRENT_DATE - INTERVAL '%s days')
            """,
            (period_days,)
        )
        result = await cur.fetchone()
        previous = float(result[0]) if result and result[0] is not None else 0.0

        return self._calculate_metric_card(round(current, 1), round(previous, 1))

    async def _get_activity_chart(self, cur: Any, period_days: int) -> list[TimeSeriesPoint]:
        """Получить временной ряд активности сообщений"""
        await cur.execute(
            """
            SELECT
                DATE(created_at) as date,
                COUNT(*) as messages
            FROM messages
            WHERE deleted_at IS NULL
            AND created_at >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(created_at)
            ORDER BY date
            """,
            (period_days,)
        )

        results = await cur.fetchall()

        # Создаем словарь с данными
        data_dict = {row[0]: row[1] for row in results}

        # Заполняем все дни в периоде (даже те, где нет сообщений)
        today = date.today()
        points: list[TimeSeriesPoint] = []

        for i in range(period_days):
            current_date = today - timedelta(days=period_days - i - 1)
            messages_count = data_dict.get(current_date, 0)
            points.append(TimeSeriesPoint(date=current_date, messages=messages_count))

        return points

    def _calculate_metric_card(
        self, current: int | float, previous: int | float
    ) -> MetricCard:
        """Расчет метрики с трендом

        Args:
            current: Текущее значение метрики
            previous: Значение в предыдущем периоде

        Returns:
            MetricCard с рассчитанным трендом
        """
        # Расчет изменения в процентах
        if previous > 0:
            change_percent = ((current - previous) / previous) * 100
        else:
            # Если предыдущего значения нет, считаем что рост 100% если есть текущее
            change_percent = 100.0 if current > 0 else 0.0

        # Определение тренда по формуле из requirements
        trend: Literal["up", "down", "stable"]
        if change_percent > 1.0:
            trend = "up"
        elif change_percent < -1.0:
            trend = "down"
        else:
            trend = "stable"

        return MetricCard(
            value=current,
            change_percent=round(change_percent, 1),
            trend=trend
        )
