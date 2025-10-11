"""Тесты для конфигурации"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config, load_config


def test_load_config_missing_telegram_token():
    """Тест ошибки при отсутствии TELEGRAM_TOKEN"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}, clear=True):
        with pytest.raises(ValueError, match="TELEGRAM_TOKEN"):
            load_config()


def test_load_config_missing_openai_key():
    """Тест ошибки при отсутствии OPENAI_API_KEY"""
    with patch.dict("os.environ", {"TELEGRAM_TOKEN": "test-token"}, clear=True):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            load_config()


def test_load_config_success():
    """Тест успешной загрузки конфигурации"""
    env_vars = {
        "TELEGRAM_TOKEN": "test-telegram-token",
        "OPENAI_API_KEY": "test-openai-key",
    }
    with patch.dict("os.environ", env_vars, clear=True):
        config = load_config()

        assert config.telegram_token == "test-telegram-token"
        assert config.openai_api_key == "test-openai-key"


def test_load_config_with_optional_params():
    """Тест загрузки конфигурации с опциональными параметрами"""
    env_vars = {
        "TELEGRAM_TOKEN": "test-telegram-token",
        "OPENAI_API_KEY": "test-openai-key",
        "OPENAI_BASE_URL": "https://custom-api.example.com",
        "OPENAI_MODEL": "gpt-4",
        "MAX_CONTEXT_MESSAGES": "20",
        "TEMPERATURE": "0.8",
    }
    with patch.dict("os.environ", env_vars, clear=True):
        config = load_config()

        assert config.openai_base_url == "https://custom-api.example.com"
        assert config.openai_model == "gpt-4"
        assert config.max_context_messages == 20
        assert config.temperature == 0.8


def test_config_defaults():
    """Тест значений по умолчанию"""
    env_vars = {
        "TELEGRAM_TOKEN": "test-telegram-token",
        "OPENAI_API_KEY": "test-openai-key",
    }
    with patch.dict("os.environ", env_vars, clear=True):
        config = load_config()

        # Проверяем дефолтные значения
        assert config.openai_base_url == "https://api.openai.com/v1"
        assert config.openai_model == "gpt-4o-mini"
        assert config.max_context_messages == 10
        assert config.temperature == 0.7


def test_config_dataclass():
    """Тест создания Config напрямую"""
    config = Config(
        telegram_token="token123",
        openai_api_key="key456",
        openai_base_url="https://test.com",
        openai_model="gpt-3.5-turbo",
        max_context_messages=15,
        temperature=0.5,
    )

    assert config.telegram_token == "token123"
    assert config.openai_api_key == "key456"
    assert config.openai_base_url == "https://test.com"
    assert config.openai_model == "gpt-3.5-turbo"
    assert config.max_context_messages == 15
    assert config.temperature == 0.5


@pytest.mark.parametrize(
    "max_context,expected",
    [
        ("5", 5),
        ("100", 100),
        ("1", 1),
    ],
)
def test_max_context_messages_conversion(max_context, expected):
    """Параметризованный тест преобразования MAX_CONTEXT_MESSAGES"""
    env_vars = {
        "TELEGRAM_TOKEN": "test-token",
        "OPENAI_API_KEY": "test-key",
        "MAX_CONTEXT_MESSAGES": max_context,
    }
    with patch.dict("os.environ", env_vars, clear=True):
        config = load_config()
        assert config.max_context_messages == expected


@pytest.mark.parametrize(
    "temperature,expected",
    [
        ("0.1", 0.1),
        ("0.9", 0.9),
        ("1.0", 1.0),
        ("0.0", 0.0),
    ],
)
def test_temperature_conversion(temperature, expected):
    """Параметризованный тест преобразования TEMPERATURE"""
    env_vars = {
        "TELEGRAM_TOKEN": "test-token",
        "OPENAI_API_KEY": "test-key",
        "TEMPERATURE": temperature,
    }
    with patch.dict("os.environ", env_vars, clear=True):
        config = load_config()
        assert config.temperature == expected
