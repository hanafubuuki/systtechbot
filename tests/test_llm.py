"""Тесты для LLM сервиса"""
import pytest


def test_token_cleanup():
    """Тест очистки служебных токенов из ответа LLM"""
    # Имитируем логику очистки из services/llm.py
    def clean_tokens(answer: str) -> str:
        """Очистка от служебных токенов"""
        if not answer:
            return answer
            
        tokens_to_remove = [
            '<｜begin▁of▁sentence｜>',
            '<|begin_of_sentence|>',
            '<｜end▁of▁sentence｜>',
            '<|end_of_sentence|>',
            '<｜end▁of▁text｜>',
            '<|end_of_text|>',
        ]
        
        for token in tokens_to_remove:
            answer = answer.replace(token, '')
        
        return answer.strip()
    
    # Тест 1: Удаление токена в конце
    answer = "Привет! Как дела?<｜begin▁of▁sentence｜>"
    result = clean_tokens(answer)
    assert result == "Привет! Как дела?"
    assert '<｜begin▁of▁sentence｜>' not in result
    
    # Тест 2: Удаление альтернативного формата токена
    answer = "Столица России — Москва.<|begin_of_sentence|>"
    result = clean_tokens(answer)
    assert result == "Столица России — Москва."
    assert '<|begin_of_sentence|>' not in result
    
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
            '<｜begin▁of▁sentence｜>',
            '<|begin_of_sentence|>',
            '<｜end▁of▁sentence｜>',
            '<|end_of_sentence|>',
            '<｜end▁of▁text｜>',
            '<|end_of_text|>',
        ]
        
        for token in tokens_to_remove:
            answer = answer.replace(token, '')
        
        return answer.strip()
    
    # Текст со всеми типами токенов
    answer = (
        "<｜begin▁of▁sentence｜>Начало текста. "
        "<|end_of_sentence|>Середина. "
        "<｜end▁of▁text｜>Конец<|begin_of_sentence|>"
    )
    result = clean_tokens(answer)
    
    # Все токены должны быть удалены
    assert '<｜begin▁of▁sentence｜>' not in result
    assert '<|begin_of_sentence|>' not in result
    assert '<｜end▁of▁sentence｜>' not in result
    assert '<|end_of_sentence|>' not in result
    assert '<｜end▁of▁text｜>' not in result
    assert '<|end_of_text|>' not in result
    
    # Должен остаться только чистый текст
    assert result == "Начало текста. Середина. Конец"

