"""Абстрактный интерфейс для сбора статистики диалогов"""

from abc import ABC, abstractmethod

from api.models import DashboardStats


class StatCollector(ABC):
    """Абстрактный базовый класс для сбора статистики диалогов

    Определяет интерфейс для различных реализаций сбора статистики:
    - MockStatCollector - генерирует тестовые данные
    - RealStatCollector - собирает данные из реальной БД (S5)
    """

    @abstractmethod
    async def get_dashboard_stats(self, period_days: int = 90) -> DashboardStats:
        """Получить статистику для дашборда

        Args:
            period_days: Период в днях для временных рядов (7, 30, 90)

        Returns:
            DashboardStats с полной статистикой для дашборда

        Raises:
            ValueError: Если period_days не из допустимых значений
        """
        pass
