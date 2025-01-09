from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .api import SaveEcoBotClient

_LOGGER = logging.getLogger(__name__)

API_TO_HA_ICON_MAPPING = {
    "Humidity": "mdi:water-percent",
    "PM10": "mdi:air-filter",
    "PM2.5": "mdi:air-filter",
    "Pressure": "mdi:gauge",
    "Temperature": "mdi:thermometer",
    "Air Quality Index": "mdi:cloud",
}
API_TO_HA_UNIT_MAPPING = {
    "Humidity": PERCENTAGE,
    "PM10": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    "PM2.5": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    "Pressure": UnitOfPressure.HPA,
    "Temperature": UnitOfTemperature.CELSIUS,
    "Air Quality Index": "aqi",  # Немає константи в HA
}
SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up sensors for SaveEcoBot."""
    client = hass.data[DOMAIN][entry.entry_id]
    selected_sensors = entry.data.get("sensors", [])

    # Отримуємо список станцій

    entities = []
    async for station in client.get_sensors_by_ids(selected_sensors):
        # Create a separate entity for each pollutant in a station
        for pollutant in station.get("pollutants", []):
            entities.append(SaveEcoBotPollutantSensor(station, pollutant))

    async_add_entities(entities, update_before_add=True)


class SaveEcoBotPollutantSensor(SensorEntity):
    """Representation of a pollutant sensor."""

    def __init__(self, station, pollutant):
        self._station = station
        self._pollutant = pollutant
        self._attr_name = f"{station['cityName']} - {station['stationName'] or station['localName']} - {pollutant['pol']}"
        self._attr_unique_id = f"{station['id']}_{pollutant['pol']}"
        self._attr_native_unit_of_measurement = pollutant["unit"]
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return self._attr_unique_id

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return (
            API_TO_HA_UNIT_MAPPING.get(self._pollutant["pol"])
            or self._attr_native_unit_of_measurement
        )

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return API_TO_HA_ICON_MAPPING.get(self._pollutant["pol"])

    @property
    def extra_state_attributes(self):
        """Return additional attributes for the sensor."""
        return self._attributes

    async def async_update(self):
        """Fetch the latest data for the sensor."""
        try:
            station_data = None

            async for s in SaveEcoBotClient().get_sensors_by_ids([self._station["id"]]):
                station_data = s
                break

            if station_data:
                self._pollutant = next(
                    (
                        p
                        for p in station_data.get("pollutants", [])
                        if p["pol"] == self._pollutant["pol"]
                    ),
                    self._pollutant,
                )
                self._state = self._pollutant["value"]
                self._attributes = {
                    "city_name": station_data.get("cityName"),
                    "station_name": station_data.get("stationName")
                    or station_data.get("localName"),
                    "latitude": station_data.get("latitude"),
                    "longitude": station_data.get("longitude"),
                    "timezone": station_data.get("timezone"),
                    "platform_name": station_data.get("platformName"),
                    "time": self._pollutant["time"],
                    "averaging": self._pollutant["averaging"],
                }
        except Exception as exc:
            _LOGGER.error("Error updating sensor %s: %s", self.name, exc)
