"""Support for NerdQAxe+ Miner binary sensors."""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NerdQAxeConfigEntry, NerdQAxeDataUpdateCoordinator
from .const import (
    ATTR_POOL_CONNECTED,
    ATTR_STRATUM,
    ATTR_STRATUM_CONNECTED,
    ATTR_STRATUM_POOLS,
)

_LOGGER = logging.getLogger(__name__)

# All entities read from a single coordinator; updates are not per-entity.
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NerdQAxeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NerdQAxe+ Miner binary sensors from a config entry.

    Creates binary sensor for Stratum pool connection status.

    Args:
        hass: Home Assistant instance
        entry: Config entry
        async_add_entities: Callback to add entities

    """
    coordinator = entry.runtime_data.coordinator

    _LOGGER.debug("Setting up binary sensor entities for %s", coordinator.host)

    entities = [
        NerdQAxeStratumSensor(coordinator),
    ]

    async_add_entities(entities)
    _LOGGER.info(
        "Successfully set up %d binary sensor entities for %s",
        len(entities),
        coordinator.host,
    )


class NerdQAxeStratumSensor(
    CoordinatorEntity[NerdQAxeDataUpdateCoordinator], BinarySensorEntity
):
    """Representation of NerdQAxe+ Stratum pool connection status.

    Binary sensor indicating whether the miner is currently connected to
    the configured Stratum mining pool.
    """

    __slots__ = ()

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_has_entity_name = True

    def __init__(self, coordinator: NerdQAxeDataUpdateCoordinator) -> None:
        """Initialize the binary sensor.

        Args:
            coordinator: Data update coordinator instance

        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id_base}_stratum_connected"
        self._attr_translation_key = "stratum_connected"
        self._attr_device_info = coordinator.get_device_info()

    @property
    def is_on(self) -> bool:
        """Return true if the miner is connected to stratum pool.

        Modern firmware exposes the connection state inside the nested
        ``stratum.pools[].connected`` structure (one entry per pool in
        fallback/dual-pool mode). The miner is considered connected as soon as
        any configured pool reports ``connected``. A legacy flat
        ``isStratumConnected`` field is used as a fallback for older firmware.

        Returns:
            bool: True if connected to at least one pool, False otherwise

        """
        data = self.coordinator.data
        if not data:
            return False

        stratum = data.get(ATTR_STRATUM) or {}
        pools = stratum.get(ATTR_STRATUM_POOLS) or []
        if pools:
            return any(pool.get(ATTR_POOL_CONNECTED, False) for pool in pools)

        # Legacy fallback for firmware exposing a flat boolean field
        return bool(data.get(ATTR_STRATUM_CONNECTED, False))
