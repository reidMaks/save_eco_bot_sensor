from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SaveEcoBotCoordinator

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
    "Air Quality Index": "aqi",
}


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up sensors for SaveEcoBot."""
    coordinator: SaveEcoBotCoordinator = hass.data[DOMAIN][entry.entry_id]
    selected_sensors = entry.data.get("sensors", [])

    entities = []
    
    # Iterate through all stations data in the coordinator
    # Since coordinator.data is a dict keyed by station.id
    for station_id, station_data in coordinator.data.items():
        if station_id in selected_sensors:
             for pollutant in station_data.get("pollutants", []):
                entities.append(SaveEcoBotPollutantSensor(coordinator, station_data, pollutant))

    async_add_entities(entities)


class SaveEcoBotPollutantSensor(CoordinatorEntity, SensorEntity):
    """Representation of a pollutant sensor."""

    def __init__(self, coordinator, station, pollutant):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._station_id = station["id"]
        # Determine unique key for pollutant, e.g. "PM2.5"
        self._pollutant_key = pollutant["pol"]
        
        # Static info
        self._attr_name = f"{station['cityName']} - {station['stationName'] or station['localName']} - {pollutant['pol']}"
        self._attr_unique_id = f"{station['id']}_{pollutant['pol']}"
        self._attr_native_unit_of_measurement = API_TO_HA_UNIT_MAPPING.get(self._pollutant_key) or pollutant["unit"]
        self._attr_icon = API_TO_HA_ICON_MAPPING.get(self._pollutant_key)

    @property
    def _pollutant_data(self):
        """Get the specific pollutant data from the coordinator."""
        station = self.coordinator.data.get(self._station_id)
        if not station:
            return None
            
        for p in station.get("pollutants", []):
            if p["pol"] == self._pollutant_key:
                return p
        return None

    @property
    def native_value(self):
        """Return the current state of the sensor."""
        data = self._pollutant_data
        if data:
            return data["value"]
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        station = self.coordinator.data.get(self._station_id)
        data = self._pollutant_data
        
        if not station or not data:
            return {}
            
        return {
            "city_name": station.get("cityName"),
            "station_name": station.get("stationName") or station.get("localName"),
            "latitude": station.get("latitude"),
            "longitude": station.get("longitude"),
            "timezone": station.get("timezone"),
            "platform_name": station.get("platformName"),
            "time": data.get("time"),
            "averaging": data.get("averaging"),
        }
