"""Config flow for the Saveecobot integration."""

from __future__ import annotations

import logging
from math import atan2, cos, radians, sin, sqrt
from typing import Any

import voluptuous as vol

from homeassistant import config_entries

from .api import SaveEcoBotClient  # Ваш клієнт для роботи з API
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SaveEcoBotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SaveEcoBot."""

    VERSION = 1

    def __init__(self):
        self.client: SaveEcoBotClient = SaveEcoBotClient()
        self.selected_city: str | None = None
        self.selected_sensors: list[str] = []
        self.use_coordinates: bool = False
        self.home_coordinates: tuple[float, float] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step: selecting a city or using home coordinates."""
        errors: dict[str, str] = {}

        # Отримуємо координати дому, якщо доступні
        self.home_coordinates = (
            (
                self.hass.config.latitude,
                self.hass.config.longitude,
            )
            if self.hass.config.latitude and self.hass.config.longitude
            else None
        )

        if user_input is not None:
            self.use_coordinates = user_input["use_coordinates"]
            if self.use_coordinates:
                return await self.async_step_sensors()

            return await self.async_step_city()

        if self.home_coordinates:
            # Запитуємо, чи використовувати координати
            data_schema = vol.Schema(
                {
                    vol.Required("use_coordinates"): bool,
                }
            )
            return self.async_show_form(
                step_id="user",
                data_schema=data_schema,
                errors=errors,
                description_placeholders={
                    "suggested_value": True,
                    "label": "Use home location coordinates?",
                },
            )

        # Перехід одразу до вибору міста, якщо координати недоступні
        return await self.async_step_city()

    async def async_step_city(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the step for selecting a city manually."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.selected_city = user_input["city"]
            return await self.async_step_sensors()

        try:
            cities = await self.client.get_unique_cities()
        except Exception as exc:
            _LOGGER.exception("Failed to fetch cities from API: %s", exc)
            errors["base"] = "cannot_connect"
            cities = []

        if not cities:
            errors["base"] = "no_cities_available"

        data_schema = vol.Schema(
            {
                vol.Required("city"): vol.In(cities),
            }
        )

        return self.async_show_form(
            step_id="city", data_schema=data_schema, errors=errors
        )

    async def async_step_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the second step: selecting sensors."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.selected_sensors = user_input["sensors"]
            return self.async_create_entry(
                title=f"SaveEcoBot - {self.selected_city or 'Nearby Stations'}",
                data={
                    "city": self.selected_city,
                    "sensors": self.selected_sensors,
                },
            )

        try:
            if self.use_coordinates and self.home_coordinates:
                # Отримуємо 10 найближчих станцій до координат дому

                stations_with_distance = [
                    {
                        "station": station,
                        "distance": self._calculate_distance(
                            self.home_coordinates[0],
                            self.home_coordinates[1],
                            station["latitude"],
                            station["longitude"],
                        ),
                    }
                    async for station in self.client.get_all_stations()
                ]
                nearest_stations = list(
                    filter(lambda x: x["distance"] < 10, stations_with_distance)
                )
                nearest_stations.sort(key=lambda x: x["distance"])
                sensors = [station["station"] for station in nearest_stations[:10]]
            else:
                # Отримуємо всі станції для вибраного міста
                sensors = await self.client.get_sensors_by_city(self.selected_city)
        except Exception as exc:
            _LOGGER.exception("Failed to fetch sensors: %s", exc)
            errors["base"] = "cannot_connect"
            sensors = []

        if not sensors:
            errors["base"] = "no_sensors_available"

        sensors_repr = [
            f"{x['id']} | {x['cityName']} - {x['stationName'] or x['localName']}"
            for x in sensors
        ]

        data_schema = vol.Schema(
            {
                vol.Required("sensors"): vol.All(
                    vol.Length(min=1),  # Мінімум 1 датчик
                    vol.In(sensors_repr),  # Лише доступні датчики
                ),
            }
        )

        return self.async_show_form(
            step_id="sensors", data_schema=data_schema, errors=errors
        )

    def _calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Розрахувати відстань між двома координатами."""

        lat1 = float(lat1)
        lat2 = float(lat2)
        lon1 = float(lon1)
        lon2 = float(lon2)
        R = 6371  # Радіус Землі в км
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = (
            sin(dlat / 2) ** 2
            + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        )
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c
