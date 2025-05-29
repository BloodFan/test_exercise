# pytest tests_exercise_1.py -v
import pytest
import re
from solution import strict


@strict
def sum_two(a: int, b: int) -> int:
    """Складывает два целых числа."""
    return a + b


def test_sum_two_success():
    "Тест на успешный результат."
    assert sum_two(1, 2) == 3


def test_sum_two_type_error():
    "Тест на тип позиционных аргументов."
    with pytest.raises(TypeError, match="Argument 'b' must be int, not float"):
        sum_two(1, 2.4)


def test_kwargs_type_error():
    "Тест на тип именованных аргументов."
    with pytest.raises(TypeError, match="Argument 'a' must be int, not str"):
        sum_two(a="1", b=2)


def test_metadata():
    """Тест сохранения метаданных функции."""
    assert sum_two.__name__ == 'sum_two'
    assert sum_two.__doc__ == "Складывает два целых числа."


def test_missing_arguments():
    """Проверяет реакцию на недостаток аргументов."""
    with pytest.raises(
        TypeError,
        match=re.escape("Missing required arguments: ['b']")
    ):
        sum_two(1)  # Пропущен аргумент b

    with pytest.raises(
        TypeError,
        match=re.escape("Missing required arguments: ['a', 'b']")
    ):
        sum_two()  # Все аргументы пропущены


def test_mixed_args_kwargs():
    """Проверяет смешанный вариант передачи аргументов."""
    assert sum_two(1, b=2) == 3  # Корректно
    with pytest.raises(
        TypeError,
        match=re.escape("Missing required arguments: ['b']")
    ):
        sum_two(a=1)  # Только kwargs, но b пропущен


def test_extra_arguments():
    "Проверяет обработку избыточных позиционных аргументов."
    with pytest.raises(TypeError, match="Expected 2 arguments, got 3"):
        sum_two(1, 2, 3)  # Лишний аргумент


def test_unexpected_kwarg():
    "Проверяет обнаружение неизвестных именованных аргументов."
    with pytest.raises(
        TypeError,
        match=re.escape("Unexpected keyword argument(s): ['c']")
    ):
        sum_two(a=1, b=2, c=3)


def test_no_annotations():
    "Проверяет требование наличия аннотаций у функции."
    with pytest.raises(TypeError, match="Function must have type annotations"):
        @strict
        def no_annotations(a, b):
            return a + b
