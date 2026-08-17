"""Support for NerdQAxe+ Miner binary sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
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
from .pool import is_using_fallback

_LOGGER = logging.getLogger(__name__)

# All entities read from a single coordinator; updates are not per-entity.
PARALLEL_UPDATES = 0


def _is_stratum_connected(data: dict[str, Any]) -> bool:
    """Return True if the miner is connected to a stratum pool.

    Modern firmware exposes the connection state inside the nested
    ``stratum.pools[].connected`` structure (one entry per pool in
    fallback/dual-pool mode). The miner is considered connected as soon as any
    configured pool reports ``connected``. A legacy flat ``isStratumConnected``
    field is used as a fallback for older firmware.
    """
    stratum = data.get(ATTR_STRATUM) or {}
    pools = stratum.get(ATTR_STRATUM_POOLS) or []
    if pools:
        return any(pool.get(ATTR_POOL_CONNECTED, False) for pool in pools)

    # Legacy fallback for firmware exposing a flat boolean field
    return bool(data.get(ATTR_STRATUM_CONNECTED, False))


@dataclass(frozen=True, kw_only=True)
class NerdQAxeBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a NerdQAxe+ binary sensor entity.

    ``value_fn`` derives the on/off state from the coordinator data dict, which
    keeps all per-sensor logic declarative and in one place.
    """

    value_fn: Callable[[dict[str, Any]], bool]


BINARY_SENSORS: tuple[NerdQAxeBinarySensorEntityDescription, ...] = (
    NerdQAxeBinarySensorEntityDescription(
        key="stratum_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=_is_stratum_connected,
    ),
    NerdQAxeBinarySensorEntityDescription(
        key="using_fallback_pool",
        icon="mdi:swap-horizontal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=is_using_fallback,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NerdQAxeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NerdQAxe+ Miner binary sensors from a config entry.

    Creates binary sensors for the Stratum pool connection status and for the
    failover state (whether the fallback pool is currently in use).

    Args:
        hass: Home Assistant instance
        entry: Config entry
        async_add_entities: Callback to add entities

    """
    coordinator = entry.runtime_data.coordinator

    _LOGGER.debug("Setting up binary sensor entities for %s", coordinator.host)

    entities = [
        NerdQAxeBinarySensor(coordinator, description) for description in BINARY_SENSORS
    ]

    async_add_entities(entities)
    _LOGGER.info(
        "Successfully set up %d binary sensor entities for %s",
        len(entities),
        coordinator.host,
    )


class NerdQAxeBinarySensor(
    CoordinatorEntity[NerdQAxeDataUpdateCoordinator], BinarySensorEntity
):
    """Representation of a NerdQAxe+ Miner binary sensor.

    Generic binary sensor entity driven by a
    :class:`NerdQAxeBinarySensorEntityDescription` that derives its state from
    the coordinator data via ``value_fn``.
    """

    entity_description: NerdQAxeBinarySensorEntityDescription

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NerdQAxeDataUpdateCoordinator,
        description: NerdQAxeBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor.

        Args:
            coordinator: Data update coordinator instance
            description: Binary sensor description (key, device class, value_fn)

        """
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id_base}_{description.key}"
        self._attr_translation_key = description.key
        self._attr_device_info = coordinator.get_device_info()

    @property
    def is_on(self) -> bool:
        """Return the binary sensor state.

        Returns:
            bool: True if the underlying condition holds, False otherwise

        """
        if not self.coordinator.data:
            return False
        return self.entity_description.value_fn(self.coordinator.data)
