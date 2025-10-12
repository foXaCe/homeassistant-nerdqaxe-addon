"""Support for NerdQAxe+ Miner button entities."""
from __future__ import annotations

import logging

import aiohttp
import async_timeout

from homeassistant.components.button import ButtonEntity, ButtonDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NerdQAxeDataUpdateCoordinator
from .const import (
    DOMAIN,
    API_SYSTEM_RESTART,
    ATTR_DEVICE_MODEL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NerdQAxe+ Miner button entities."""
    coordinator: NerdQAxeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        NerdQAxeRestartButton(coordinator),
    ]

    async_add_entities(entities)


class NerdQAxeRestartButton(CoordinatorEntity, ButtonEntity):
    """Representation of a NerdQAxe+ restart button."""

    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_icon = "mdi:restart"

    def __init__(self, coordinator: NerdQAxeDataUpdateCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_restart"
        self._attr_name = "NerdQAxe Restart"
        self._attr_translation_key = "restart"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": f"NerdQAxe+ Miner ({coordinator.host})",
            "manufacturer": "NerdQAxe",
            "model": coordinator.data.get(ATTR_DEVICE_MODEL, "Unknown") if coordinator.data else "Unknown",
        }

    async def async_press(self) -> None:
        """Handle the button press - restart the miner."""
        try:
            async with async_timeout.timeout(10):
                async with self.coordinator.session.post(
                    f"{self.coordinator.base_url}{API_SYSTEM_RESTART}"
                ) as response:
                    response.raise_for_status()
                    _LOGGER.info(f"Restart command sent to {self.coordinator.host}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Failed to restart miner: {err}")
            raise
