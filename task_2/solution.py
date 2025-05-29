import asyncio
import csv
import logging
import re
from asyncio import Semaphore
from typing import Dict

from api_client import APIClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("solution")

BASE_URL = "https://ru.wikipedia.org"
CSV_FILENAME = "beasts.csv"
MAX_CONCURRENT_REQUESTS = 10
WIKI_ANIMALS_EXPECTED = 47331  # актуально на 29.05.25


def normalize_first_char(title: str) -> str:
    """Нормализует первую букву названия"""
    if not title:
        return "#"

    # Удаляем все не-буквы в начале
    first_char = re.sub(r"^[^а-яА-ЯёЁ]*", "", title)
    if not first_char:
        return "#"

    first_char = first_char[0].upper()
    return "Е" if first_char in ("Ё", "Е") else first_char


async def fetch_animals_by_letter(
    client: APIClient, letter: str, semaphore: Semaphore
) -> int:
    """Получает количество животных для указанной буквы алфавита."""
    async with semaphore:
        animals_count = 0
        continue_token = None
        logger.info(f"Обработка буквы: {letter}")

        while True:
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": "Категория:Животные_по_алфавиту",
                "cmtype": "page|redirect",
                "cmshow": "all",
                "cmnamespace": "0",
                "cmlimit": "500",
                "format": "json",
                "cmstartsortkeyprefix": letter,  # Начало буквы
                "cmsort": "sortkey",
            }
            if continue_token:
                params["cmcontinue"] = continue_token

            response = await client.request("GET", "/w/api.php", params=params)

            if (
                "query" not in response
                or "categorymembers" not in response["query"]
            ):
                logger.error(
                    f"Неверный формат ответа для буквы {letter}: {response}"
                )
                return animals_count

            animals = response["query"]["categorymembers"]
            for animal in animals:
                normalized_char = normalize_first_char(animal["title"])
                if normalized_char == letter:
                    animals_count += 1

            # logger.info(f"[{letter}] Количество животных: {animals_count}")

            continue_token = response.get("continue", {}).get("cmcontinue")
            if not continue_token:
                logger.info(
                    f"[{letter}] Все животные обработаны. Итого: {animals_count}"
                )
                break

        return animals_count


async def main():
    semaphore = Semaphore(MAX_CONCURRENT_REQUESTS)

    # без "Ё", '#' - аггрегирует спецсимволы и все не начинается с кириллицы.
    # alphabet = "#АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ"
    alphabet = "#" + "".join(map(chr, range(ord("А"), ord("Я") + 1)))

    results: Dict[str, int] = {}

    async with APIClient(BASE_URL) as client:
        tasks = []
        for letter in alphabet:
            tasks.append(fetch_animals_by_letter(client, letter, semaphore))

        counts = await asyncio.gather(*tasks)

        for letter, count in zip(alphabet, counts):
            results[letter] = count

    try:
        with open(
            CSV_FILENAME, "w", newline="", encoding="utf-8-sig"
        ) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Буква", "Количество"])
            writer.writerows(results.items())

        total = sum(results.values())
        logger.info("Результаты сохранены в файл beasts.csv.")
        logger.info(
            f"Общее количество животных: {total} (ожидалось: {WIKI_ANIMALS_EXPECTED})"
        )
    except IOError as e:
        logger.error(f"Ошибка записи в файл: {e}")


if __name__ == "__main__":
    asyncio.run(main())
