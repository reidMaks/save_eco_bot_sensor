"""DataUpdateCoordinator for the SaveEcoBot integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SaveEcoBotClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SaveEcoBotCoordinator(DataUpdateCoordinator):
    """SaveEcoBot coordinator."""

    def __init__(self, hass: HomeAssistant, client: SaveEcoBotClient) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )
        self.client = client

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            # We fetch all stations from the API
            await self.client.fetch_stations()
            
            # Convert list of stations to a dict keyed by station ID for efficient lookup
            # The API returns a list of dictionaries. Each dictionary represents a station
            # and may contain multiple sensors (pollutants).
            # The station ID is unique.
            return {station["id"]: station for station in self.client.stations}
            
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
