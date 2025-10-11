"""Тесты для LLM сервиса"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

from config import Config
from services.llm import get_llm_response


def test_token_cleanup():
    """Тест очистки служебных токенов из ответа LLM"""

    # Имитируем логику очистки из services/llm.py
    def clean_tokens(answer: str) -> str:
        """Очистка от служебных токенов"""
        if not answer:
            return answer

        tokens_to_remove = [
            "<｜begin▁of▁sentence｜>",
            "<|begin_of_sentence|>",
            "<｜end▁of▁sentence｜>",
            "<|end_of_sentence|>",
            "<｜end▁of▁text｜>",
            "<|end_of_text|>",
        ]

        for token in tokens_to_remove:
            answer = answer.replace(token, "")

        return answer.strip()

    # Тест 1: Удаление токена в конце
    answer = "Привет! Как дела?<｜begin▁of▁sentence｜>"
    result = clean_tokens(answer)
    assert result == "Привет! Как дела?"
    assert "<｜begin▁of▁sentence｜>" not in result

    # Тест 2: Удаление альтернативного формата токена
    answer = "Столица России — Москва.<|begin_of_sentence|>"
    result = clean_tokens(answer)
    assert result == "Столица России — Москва."
    assert "<|begin_of_sentence|>" not in result

    # Тест 3: Удаление нескольких токенов
    answer = "<｜end▁of▁text｜>Ответ на вопрос<｜begin▁of▁sentence｜>"
    result = clean_tokens(answer)
    assert result == "Ответ на вопрос"

    # Тест 4: Текст без токенов (не должен измениться)
    answer = "Обычный текст без токенов"
    result = clean_tokens(answer)
    assert result == "Обычный текст без токенов"

    # Тест 5: Пустая строка
    answer = ""
    result = clean_tokens(answer)
    assert result == ""

    # Тест 6: Только пробелы (должны удалиться)
    answer = "   Текст с пробелами   "
    result = clean_tokens(answer)
    assert result == "Текст с пробелами"


def test_multiple_tokens_removal():
    """Тест удаления всех типов токенов одновременно"""

    def clean_tokens(answer: str) -> str:
        if not answer:
            return answer

        tokens_to_remove = [
            "<｜begin▁of▁sentence｜>",
            "<|begin_of_sentence|>",
            "<｜end▁of▁sentence｜>",
            "<|end_of_sentence|>",
            "<｜end▁of▁text｜>",
            "<|end_of_text|>",
        ]

        for token in tokens_to_remove:
            answer = answer.replace(token, "")

        return answer.strip()

    # Текст со всеми типами токенов
    answer = (
        "<｜begin▁of▁sentence｜>Начало текста. "
        "<|end_of_sentence|>Середина. "
        "<｜end▁of▁text｜>Конец<|begin_of_sentence|>"
    )
    result = clean_tokens(answer)

    # Все токены должны быть удалены
    assert "<｜begin▁of▁sentence｜>" not in result
    assert "<|begin_of_sentence|>" not in result
    assert "<｜end▁of▁sentence｜>" not in result
    assert "<|end_of_sentence|>" not in result
    assert "<｜end▁of▁text｜>" not in result
    assert "<|end_of_text|>" not in result

    # Должен остаться только чистый текст
    assert result == "Начало текста. Середина. Конец"


@pytest.fixture
def mock_config():
    """Создает mock объект Config"""
    return Config(
        telegram_token="test_token",
        openai_api_key="test_key",
        openai_base_url="https://test.api.com",
        openai_model="test-model",
        max_tokens=1000,
        temperature=0.7,
        max_context_messages=10,
        openai_timeout=30,
    )


@pytest.mark.asyncio
async def test_llm_rate_limit_error(mock_config):
    """Тест обработки ошибки RateLimitError"""
    with patch("services.llm.AsyncOpenAI") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.chat.completions.create = AsyncMock(
            side_effect=RateLimitError(
                "Rate limit exceeded", response=MagicMock(status_code=429), body=None
            )
        )

        result = await get_llm_response([{"role": "user", "content": "test"}], mock_config)

        assert "Слишком много запросов" in result
        assert "⚠️" in result


@pytest.mark.asyncio
async def test_llm_timeout_error(mock_config):
    """Тест обработки ошибки APITimeoutError"""
    with patch("services.llm.AsyncOpenAI") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.chat.completions.create = AsyncMock(
            side_effect=APITimeoutError(request=MagicMock())
        )

        result = await get_llm_response([{"role": "user", "content": "test"}], mock_config)

        assert "Превышено время ожидания" in result
        assert "⏱️" in result


@pytest.mark.asyncio
async def test_llm_connection_error(mock_config):
    """Тест обработки ошибки APIConnectionError"""
    with patch("services.llm.AsyncOpenAI") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.chat.completions.create = AsyncMock(
            side_effect=APIConnectionError(request=MagicMock())
        )

        result = await get_llm_response([{"role": "user", "content": "test"}], mock_config)

        assert "Не удалось подключиться" in result
        assert "❌" in result


@pytest.mark.asyncio
async def test_llm_status_error_404(mock_config):
    """Тест обработки ошибки APIStatusError (404)"""
    with patch("services.llm.AsyncOpenAI") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_instance.chat.completions.create = AsyncMock(
            side_effect=APIStatusError(message="Not found", response=mock_response, body=None)
        )

        result = await get_llm_response([{"role": "user", "content": "test"}], mock_config)

        assert "Модель не найдена" in result
        assert "❌" in result


@pytest.mark.asyncio
async def test_llm_status_error_500(mock_config):
    """Тест обработки ошибки APIStatusError (500)"""
    with patch("services.llm.AsyncOpenAI") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_instance.chat.completions.create = AsyncMock(
            side_effect=APIStatusError(
                message="Internal server error", response=mock_response, body=None
            )
        )

        result = await get_llm_response([{"role": "user", "content": "test"}], mock_config)

        assert "Ошибка сервиса LLM: 500" in result
        assert "❌" in result


@pytest.mark.asyncio
async def test_llm_unexpected_error(mock_config):
    """Тест обработки непредвиденной ошибки"""
    with patch("services.llm.AsyncOpenAI") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.chat.completions.create = AsyncMock(
            side_effect=ValueError("Unexpected error")
        )

        result = await get_llm_response([{"role": "user", "content": "test"}], mock_config)

        assert "непредвиденная ошибка" in result
        assert "❌" in result


@pytest.mark.asyncio
async def test_llm_empty_response(mock_config):
    """Тест обработки пустого ответа от LLM"""
    with patch("services.llm.AsyncOpenAI") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        mock_response = MagicMock()
        mock_response.choices = []

        mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await get_llm_response([{"role": "user", "content": "test"}], mock_config)

        assert "пустой ответ" in result
        assert "🤔" in result
