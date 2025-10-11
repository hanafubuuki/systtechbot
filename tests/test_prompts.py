"""Тесты для системных промптов"""

import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from roles.prompts import DEFAULT_SYSTEM_PROMPT, get_system_prompt


def test_default_prompt_without_name():
    """Тест получения промпта без имени пользователя"""
    result = get_system_prompt()

    # Должен вернуть базовый промпт
    assert result == DEFAULT_SYSTEM_PROMPT

    # Промпт должен содержать основные правила
    assert "AI-ассистент" in result
    assert "ПРАВИЛА" in result
    assert "вежливым" in result


def test_prompt_with_user_name():
    """Тест получения промпта с именем пользователя"""
    user_name = "Михаил"
    result = get_system_prompt(user_name)

    # Должен содержать базовый промпт
    assert DEFAULT_SYSTEM_PROMPT in result

    # Должен содержать имя пользователя
    assert user_name in result
    assert f"Имя пользователя: {user_name}" in result

    # Длина должна быть больше базового промпта
    assert len(result) > len(DEFAULT_SYSTEM_PROMPT)


def test_prompt_with_empty_name():
    """Тест с пустым именем пользователя"""
    result = get_system_prompt("")

    # Пустая строка считается False в Python, должен вернуть базовый промпт
    assert result == DEFAULT_SYSTEM_PROMPT


def test_prompt_with_none():
    """Тест с None вместо имени"""
    result = get_system_prompt(None)

    # None должен вернуть базовый промпт
    assert result == DEFAULT_SYSTEM_PROMPT


def test_prompt_content():
    """Тест содержимого базового промпта"""
    # Проверяем наличие ключевых инструкций
    assert "кратко" in DEFAULT_SYSTEM_PROMPT.lower()
    assert "вежлив" in DEFAULT_SYSTEM_PROMPT.lower()

    # Проверяем, что промпт запрещает использование markdown
    assert (
        "без markdown" in DEFAULT_SYSTEM_PROMPT.lower()
        or "не используй" in DEFAULT_SYSTEM_PROMPT.lower()
    )
    assert "простым текстом" in DEFAULT_SYSTEM_PROMPT.lower()


def test_prompt_with_special_characters_in_name():
    """Тест с именем, содержащим специальные символы"""
    user_name = "О'Брайен"
    result = get_system_prompt(user_name)

    # Имя должно корректно добавиться
    assert user_name in result
    assert "Имя пользователя: О'Брайен" in result


def test_prompt_with_long_name():
    """Тест с очень длинным именем"""
    user_name = "Александр Сергеевич Пушкин-Дюма"
    result = get_system_prompt(user_name)

    # Длинное имя должно корректно добавиться
    assert user_name in result
    assert DEFAULT_SYSTEM_PROMPT in result
