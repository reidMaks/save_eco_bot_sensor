import logging
from typing import AsyncGenerator, Dict, List

import aiohttp

_LOGGER = logging.getLogger(__name__)


class SaveEcoBotClient:
    """Клієнт для роботи з SaveEcoBot API."""

    API_URL = "https://api.saveecobot.com/output.json"

    def __init__(self):
        self.stations = []  # Кеш станцій
        self.updated_at = None

    async def fetch_stations(self):
        """Завантажує дані станцій з API."""

        async with aiohttp.ClientSession() as session:
            async with session.get(self.API_URL) as response:
                if response.status != 200:
                    _LOGGER.error(
                        f"Не вдалося отримати дані. Статус: {response.status}"
                    )
                    raise Exception(f"API Error: {response.status}")
                self.stations = await response.json()
                self.updated_at = response.headers.get("Date", "Unknown")

    async def get_unique_cities(self) -> list[str]:
        """Отримати список унікальних міст."""
        await self.fetch_stations()  # Виконуємо асинхронний запит до API
        return sorted({station["cityName"] for station in self.stations})

    async def get_sensors_by_ids(
        self, station_ids: List[str]
    ) -> AsyncGenerator[Dict, None]:
        """Повертає дані сенсорів за списком ID станцій.

        :param station_ids: список ID станцій
        :return: асинхронний генератор станцій з сенсорами.
        """

        await self.fetch_stations()
        for station in self.stations:
            if station["id"] in station_ids:
                yield station

    async def get_all_stations(self) -> AsyncGenerator[Dict, None]:
        await self.fetch_stations()
        for station in self.stations:
            yield station

    async def get_sensors_by_city(self, city_name: str) -> List[Dict]:
        """
        Повертає список сенсорів у вказаному місті.
        :param city_name: назва міста
        :return: список станцій у місті
        """
        await self.fetch_stations()  # Виконуємо асинхронний запит до API
        return [
            station
            for station in self.stations
            if station["cityName"].lower() == city_name.lower()
        ]
