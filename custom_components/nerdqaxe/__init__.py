"""The NerdQAxe+ Miner integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    NerdQAxeConfigEntry,
    NerdQAxeRuntimeData,
)
from .coordinator import NerdQAxeDataUpdateCoordinator

__all__ = [
    "DOMAIN",
    "NerdQAxeConfigEntry",
    "NerdQAxeDataUpdateCoordinator",
    "NerdQAxeRuntimeData",
]

_LOGGER = logging.getLogger(__name__)

# Current ConfigEntry version - increment when data structure changes
CONFIGENTRY_VERSION = 1

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.UPDATE,
    Platform.NUMBER,
]


async def async_setup_entry(hass: HomeAssistant, entry: NerdQAxeConfigEntry) -> bool:
    """Set up NerdQAxe+ Miner integration from a config entry.

    Creates the data update coordinator and initializes all platforms
    (sensors, binary sensors, buttons, updates, numbers).

    Args:
        hass: Home Assistant instance
        entry: Config entry containing host and options

    Returns:
        bool: True if setup was successful

    Raises:
        ConfigEntryNotReady: If initial data fetch fails

    """
    host = entry.data[CONF_HOST]
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    _LOGGER.info(
        "Setting up NerdQAxe+ integration for %s (scan interval: %ds)",
        host,
        scan_interval,
    )

    coordinator = NerdQAxeDataUpdateCoordinator(
        hass,
        host=host,
        scan_interval=scan_interval,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Failed to connect to miner at {host}") from err

    entry.runtime_data = NerdQAxeRuntimeData(coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.debug("NerdQAxe+ integration setup completed for %s", host)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: NerdQAxeConfigEntry) -> bool:
    """Unload a config entry and cleanup resources.

    Args:
        hass: Home Assistant instance
        entry: Config entry to unload

    Returns:
        bool: True if unload was successful

    """
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        _LOGGER.info(
            "Unloaded NerdQAxe+ integration for %s",
            entry.runtime_data.coordinator.host,
        )

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: NerdQAxeConfigEntry) -> None:
    """Reload config entry when options change.

    Args:
        hass: Home Assistant instance
        entry: Config entry to reload

    """
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old config entry to current version.

    This function handles data structure changes between versions.
    Migrations must be idempotent (safe to run multiple times).

    Args:
        hass: Home Assistant instance
        entry: Config entry to migrate

    Returns:
        bool: True if migration was successful

    """
    _LOGGER.debug(
        "Migrating config entry from version %s to %s",
        entry.version,
        CONFIGENTRY_VERSION,
    )

    # Version 1 is current - no migration needed yet
    # Future migrations will be added here as:
    #
    # if entry.version == 1:
    #     data = {**entry.data}
    #     # Transform data for version 2
    #     hass.config_entries.async_update_entry(entry, data=data, version=2)
    #
    # if entry.version == 2:
    #     data = {**entry.data}
    #     # Transform data for version 3
    #     hass.config_entries.async_update_entry(entry, data=data, version=3)

    if entry.version > CONFIGENTRY_VERSION:
        # Downgrade not supported
        _LOGGER.error(
            "Cannot downgrade config entry from version %s to %s",
            entry.version,
            CONFIGENTRY_VERSION,
        )
        return False

    _LOGGER.info("Migration to version %s successful", CONFIGENTRY_VERSION)
    return True
