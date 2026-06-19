"""Support for NerdQAxe+ Miner button entities."""

from __future__ import annotations

import logging

import aiohttp
import async_timeout
from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NerdQAxeConfigEntry, NerdQAxeDataUpdateCoordinator
from .const import API_SYSTEM_RESTART
from .exceptions import NerdQAxeApiError

_LOGGER = logging.getLogger(__name__)

# All entities read from a single coordinator; updates are not per-entity.
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NerdQAxeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NerdQAxe+ Miner button entities from a config entry.

    Creates button entity for restarting the miner.

    Args:
        hass: Home Assistant instance
        entry: Config entry
        async_add_entities: Callback to add entities

    """
    coordinator = entry.runtime_data.coordinator

    _LOGGER.debug("Setting up button entities for %s", coordinator.host)

    entities = [
        NerdQAxeRestartButton(coordinator),
    ]

    async_add_entities(entities)
    _LOGGER.info(
        "Successfully set up %d button entities for %s",
        len(entities),
        coordinator.host,
    )


class NerdQAxeRestartButton(
    CoordinatorEntity[NerdQAxeDataUpdateCoordinator], ButtonEntity
):
    """Representation of a NerdQAxe+ restart button.

    Button entity that sends a restart command to the miner via REST API.
    """

    __slots__ = ()

    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_icon = "mdi:restart"
    _attr_has_entity_name = True

    def __init__(self, coordinator: NerdQAxeDataUpdateCoordinator) -> None:
        """Initialize the button.

        Args:
            coordinator: Data update coordinator instance

        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id_base}_restart"
        self._attr_translation_key = "restart"
        self._attr_device_info = coordinator.get_device_info()

    async def async_press(self) -> None:
        """Handle the button press to restart the miner.

        Sends POST request to /api/system/restart endpoint.

        Raises:
            NerdQAxeApiError: If the restart command fails

        """
        _LOGGER.debug("Restart button pressed for %s", self.coordinator.host)
        try:
            async with (
                async_timeout.timeout(10),
                self.coordinator.session.post(
                    f"{self.coordinator.base_url}{API_SYSTEM_RESTART}"
                ) as response,
            ):
                response.raise_for_status()
                _LOGGER.info(
                    "Restart command sent successfully to %s",
                    self.coordinator.host,
                )
        except (aiohttp.ClientError, TimeoutError) as err:
            raise NerdQAxeApiError(
                f"Failed to restart miner at {self.coordinator.host}"
            ) from err
