"""Support for NerdQAxe+ Miner binary sensors."""
from __future__ import annotations

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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NerdQAxe+ Miner binary sensors."""
    coordinator: NerdQAxeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        NerdQAxeStratumSensor(coordinator),
    ]

    async_add_entities(entities)


class NerdQAxeStratumSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of NerdQAxe+ Stratum connection status."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: NerdQAxeDataUpdateCoordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_stratum_connected"
        self._attr_name = "NerdQAxe Stratum Connected"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": f"NerdQAxe+ Miner ({coordinator.host})",
            "manufacturer": "NerdQAxe",
            "model": coordinator.data.get(ATTR_DEVICE_MODEL, "Unknown") if coordinator.data else "Unknown",
        }

    @property
    def is_on(self) -> bool:
        """Return true if the miner is connected to stratum."""
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get(ATTR_STRATUM_CONNECTED, False)
