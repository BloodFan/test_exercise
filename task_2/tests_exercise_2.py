# pytest tests_exercise_2.py -v
import pytest
from unittest.mock import patch
from solution import normalize_first_char, fetch_animals_by_letter
from asyncio import Semaphore

from mock_api_client import MockAPIClient


def test_normalize_first_char():
    """Тест функции normalize_first_char"""
    assert normalize_first_char("Аист") == "А"
    assert normalize_first_char("ёж") == "Е"
    assert normalize_first_char("42 попугая") == "П"
    assert normalize_first_char("") == "#"
    assert normalize_first_char("Łoś") == "#"
    assert normalize_first_char("#метка") == "М"


@pytest.mark.asyncio
async def test_fetch_animals_by_letter():
    """Тест функции fetch_animals_by_letter"""
    client = MockAPIClient()
    semaphore = Semaphore(10)

    count = await fetch_animals_by_letter(client, "Б", semaphore)
    assert count == 3

    count = await fetch_animals_by_letter(client, "Е", semaphore)
    assert count == 1

    count = await fetch_animals_by_letter(client, "#", semaphore)
    assert count == 1


@pytest.mark.asyncio
async def test_main_integration(tmp_path, monkeypatch):
    """Тест с реальным временным файлом."""
    test_csv = tmp_path / "beasts_test.csv"

    monkeypatch.setattr("solution.CSV_FILENAME", str(test_csv))

    with patch("solution.APIClient", MockAPIClient):
        from solution import main
        await main()

    assert test_csv.exists()
    with open(test_csv, "r", encoding="utf-8-sig") as f:
        content = f.read()
        assert "Буква,Количество" in content
        assert "Б,3" in content


@pytest.mark.asyncio
async def test_file_write_error(caplog):
    """Проверка обработки ошибки записи в файл. """
    with patch("solution.APIClient", MockAPIClient), \
         patch("solution.open", side_effect=IOError("Disk full")):

        from solution import main
        await main()

        assert "Ошибка записи в файл: Disk full" in caplog.text
