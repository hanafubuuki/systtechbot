"""Константы приложения"""

from enum import Enum


class MessageRole(str, Enum):
    """Роли сообщений в диалоге"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
