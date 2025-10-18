"""Коллекторы статистики для дашборда"""

from api.collectors.base import StatCollector
from api.collectors.mock import MockStatCollector
from api.collectors.real import RealStatCollector

__all__ = ["StatCollector", "MockStatCollector", "RealStatCollector"]
