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
    """Set up NerdQAxe+ Miner button entities from a config entry.

    Creates button entity for restarting the miner.

    Args:
        hass: Home Assistant instance
        entry: Config entry
        async_add_entities: Callback to add entities
    """
    coordinator: NerdQAxeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    _LOGGER.debug("Setting up button entities for %s", coordinator.host)

    entities = [
        NerdQAxeRestartButton(coordinator),
    ]

    async_add_entities(entities)
    _LOGGER.info("Successfully set up %d button entities for %s", len(entities), coordinator.host)


class NerdQAxeRestartButton(CoordinatorEntity, ButtonEntity):
    """Representation of a NerdQAxe+ restart button.

    Button entity that sends a restart command to the miner via REST API.
    """

    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_icon = "mdi:restart"

    def __init__(self, coordinator: NerdQAxeDataUpdateCoordinator) -> None:
        """Initialize the button.

        Args:
            coordinator: Data update coordinator instance
        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_restart"
        self._attr_name = "NerdQAxe Restart"
        self._attr_translation_key = "restart"
        self._attr_device_info = coordinator.get_device_info()

    async def async_press(self) -> None:
        """Handle the button press to restart the miner.

        Sends POST request to /api/system/restart endpoint.

        Raises:
            aiohttp.ClientError: If restart command fails
        """
        _LOGGER.debug("Restart button pressed for %s", self.coordinator.host)
        try:
            async with async_timeout.timeout(10):
                async with self.coordinator.session.post(
                    f"{self.coordinator.base_url}{API_SYSTEM_RESTART}"
                ) as response:
                    response.raise_for_status()
                    _LOGGER.info("Restart command sent successfully to %s", self.coordinator.host)
        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to restart miner at %s: %s", self.coordinator.host, err)
            raise
