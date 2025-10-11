"""Типы данных приложения"""

from typing import TypedDict


class Message(TypedDict):
    """Сообщение в диалоге.

    Attributes:
        role: Роль отправителя (system/user/assistant)
        content: Текст сообщения
    """

    role: str
    content: str
