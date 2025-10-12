"""Support for NerdQAxe+ Miner number entities."""
from __future__ import annotations

import logging

import aiohttp
import async_timeout

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NerdQAxeDataUpdateCoordinator
from .const import (
    DOMAIN,
    API_SYSTEM_ASIC,
    ATTR_DEVICE_MODEL,
    ATTR_FREQUENCY,
    ATTR_CORE_VOLTAGE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NerdQAxe+ Miner number entities."""
    coordinator: NerdQAxeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        NerdQAxeFrequencyNumber(coordinator),
        NerdQAxeCoreVoltageNumber(coordinator),
    ]

    async_add_entities(entities)


class NerdQAxeFrequencyNumber(CoordinatorEntity, NumberEntity):
    """Representation of NerdQAxe+ ASIC frequency control."""

    _attr_icon = "mdi:sine-wave"
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 400
    _attr_native_max_value = 575
    _attr_native_step = 25
    _attr_native_unit_of_measurement = "MHz"

    def __init__(self, coordinator: NerdQAxeDataUpdateCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_frequency"
        self._attr_name = "NerdQAxe ASIC Frequency"
        self._attr_translation_key = "frequency"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": f"NerdQAxe+ Miner ({coordinator.host})",
            "manufacturer": "NerdQAxe",
            "model": coordinator.data.get(ATTR_DEVICE_MODEL, "Unknown") if coordinator.data else "Unknown",
        }

    @property
    def native_value(self) -> float | None:
        """Return the current frequency."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(ATTR_FREQUENCY)

    async def async_set_native_value(self, value: float) -> None:
        """Set new frequency value."""
        try:
            async with async_timeout.timeout(10):
                async with self.coordinator.session.post(
                    f"{self.coordinator.base_url}{API_SYSTEM_ASIC}",
                    json={"frequency": int(value)}
                ) as response:
                    response.raise_for_status()
                    _LOGGER.info(f"Frequency set to {value} MHz on {self.coordinator.host}")
                    await self.coordinator.async_request_refresh()
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Failed to set frequency: {err}")
            raise


class NerdQAxeCoreVoltageNumber(CoordinatorEntity, NumberEntity):
    """Representation of NerdQAxe+ core voltage control."""

    _attr_icon = "mdi:flash"
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 1000
    _attr_native_max_value = 1300
    _attr_native_step = 10
    _attr_native_unit_of_measurement = "mV"

    def __init__(self, coordinator: NerdQAxeDataUpdateCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_core_voltage"
        self._attr_name = "NerdQAxe Core Voltage"
        self._attr_translation_key = "core_voltage"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": f"NerdQAxe+ Miner ({coordinator.host})",
            "manufacturer": "NerdQAxe",
            "model": coordinator.data.get(ATTR_DEVICE_MODEL, "Unknown") if coordinator.data else "Unknown",
        }

    @property
    def native_value(self) -> float | None:
        """Return the current core voltage."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(ATTR_CORE_VOLTAGE)

    async def async_set_native_value(self, value: float) -> None:
        """Set new core voltage value."""
        try:
            async with async_timeout.timeout(10):
                async with self.coordinator.session.post(
                    f"{self.coordinator.base_url}{API_SYSTEM_ASIC}",
                    json={"coreVoltage": int(value)}
                ) as response:
                    response.raise_for_status()
                    _LOGGER.info(f"Core voltage set to {value} mV on {self.coordinator.host}")
                    await self.coordinator.async_request_refresh()
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Failed to set core voltage: {err}")
            raise
