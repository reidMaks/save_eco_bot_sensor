"""The SaveEcoBot integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import SaveEcoBotClient
from .coordinator import SaveEcoBotCoordinator
from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SaveEcoBot from a config entry."""
    # Створення екземпляра API-клієнта
    client = SaveEcoBotClient()

    # Створення координатора
    coordinator = SaveEcoBotCoordinator(hass, client)
    
    # Перше завантаження даних
    await coordinator.async_config_entry_first_refresh()

    # Збереження координатора у hass.data
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Передаємо конфігурацію платформам
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Видаляємо клієнт із hass.data
    if entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)

    # Вивантажуємо платформи
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
