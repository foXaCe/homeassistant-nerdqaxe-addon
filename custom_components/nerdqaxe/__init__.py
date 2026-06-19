"""The NerdQAxe+ Miner integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr, entity_registry as er

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
CONFIGENTRY_VERSION = 2

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

    if entry.version > CONFIGENTRY_VERSION:
        # Downgrade not supported
        _LOGGER.error(
            "Cannot downgrade config entry from version %s to %s",
            entry.version,
            CONFIGENTRY_VERSION,
        )
        return False

    if entry.version == 1:
        await _async_migrate_v1_to_v2(hass, entry)

    _LOGGER.info("Migration to version %s successful", CONFIGENTRY_VERSION)
    return True


async def _async_migrate_v1_to_v2(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Re-key entities and device from host-based to MAC-based identifiers.

    Version 1 derived entity unique ids (``{host}_{key}``) and the device
    identifier (``(DOMAIN, host)``) from the host/IP, which orphans entities
    when the miner IP changes. Version 2 uses the stable MAC address (stored
    as the config entry unique id). Idempotent: re-running finds nothing to
    rewrite once already on the MAC-based scheme.

    Args:
        hass: Home Assistant instance
        entry: Config entry being migrated

    """
    mac = entry.unique_id
    host = entry.data.get(CONF_HOST)

    if mac and host and mac != host:
        old_prefix = f"{host}_"

        @callback
        def _migrate_unique_id(
            registry_entry: er.RegistryEntry,
        ) -> dict[str, str] | None:
            if registry_entry.unique_id.startswith(old_prefix):
                suffix = registry_entry.unique_id[len(old_prefix) :]
                return {"new_unique_id": f"{mac}_{suffix}"}
            return None

        await er.async_migrate_entries(hass, entry.entry_id, _migrate_unique_id)

        # Re-key the device from (DOMAIN, host) to (DOMAIN, mac).
        device_registry = dr.async_get(hass)
        device = device_registry.async_get_device(identifiers={(DOMAIN, host)})
        if device is not None:
            device_registry.async_update_device(
                device.id, new_identifiers={(DOMAIN, mac)}
            )

    hass.config_entries.async_update_entry(entry, version=2)
