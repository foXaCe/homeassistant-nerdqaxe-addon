"""Support for NerdQAxe+ Miner binary sensors."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NerdQAxeDataUpdateCoordinator
from .const import (
    DOMAIN,
    ATTR_STRATUM_CONNECTED,
    ATTR_DEVICE_MODEL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NerdQAxe+ Miner binary sensors from a config entry.

    Creates binary sensor for Stratum pool connection status.

    Args:
        hass: Home Assistant instance
        entry: Config entry
        async_add_entities: Callback to add entities
    """
    coordinator: NerdQAxeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    _LOGGER.debug("Setting up binary sensor entities for %s", coordinator.host)

    entities = [
        NerdQAxeStratumSensor(coordinator),
    ]

    async_add_entities(entities)
    _LOGGER.info("Successfully set up %d binary sensor entities for %s", len(entities), coordinator.host)


class NerdQAxeStratumSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of NerdQAxe+ Stratum pool connection status.

    Binary sensor indicating whether the miner is currently connected to
    the configured Stratum mining pool.
    """

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: NerdQAxeDataUpdateCoordinator) -> None:
        """Initialize the binary sensor.

        Args:
            coordinator: Data update coordinator instance
        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_stratum_connected"
        self._attr_name = "NerdQAxe Stratum Connected"
        self._attr_translation_key = "stratum_connected"
        self._attr_device_info = coordinator.get_device_info()

    @property
    def is_on(self) -> bool:
        """Return true if the miner is connected to stratum pool.

        Returns:
            bool: True if connected, False otherwise
        """
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get(ATTR_STRATUM_CONNECTED, False)
