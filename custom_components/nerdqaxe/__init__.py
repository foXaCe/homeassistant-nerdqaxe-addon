"""The NerdQAxe+ Miner integration."""
from __future__ import annotations

import asyncio
import logging
import traceback
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    API_SYSTEM_INFO,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON, Platform.UPDATE, Platform.NUMBER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NerdQAxe+ Miner integration from a config entry.

    Creates the data update coordinator and initializes all platforms
    (sensors, binary sensors, buttons, updates, numbers).

    Args:
        hass: Home Assistant instance
        entry: Config entry containing host and options

    Returns:
        bool: True if setup was successful
    """
    host = entry.data[CONF_HOST]
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    _LOGGER.info("Setting up NerdQAxe+ integration for %s (scan interval: %ds)", host, scan_interval)

    coordinator = NerdQAxeDataUpdateCoordinator(
        hass,
        host=host,
        scan_interval=scan_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.debug("NerdQAxe+ integration setup completed for %s", host)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and cleanup resources.

    Args:
        hass: Home Assistant instance
        entry: Config entry to unload

    Returns:
        bool: True if unload was successful
    """
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info("Unloaded NerdQAxe+ integration for %s", coordinator.host)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change.

    Args:
        hass: Home Assistant instance
        entry: Config entry to reload
    """
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class NerdQAxeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NerdQAxe+ Miner data from API.

    Handles periodic polling of the miner's REST API endpoint and distributes
    data to all platform entities via the coordinator pattern.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        scan_interval: int,
    ) -> None:
        """Initialize the data update coordinator.

        Args:
            hass: Home Assistant instance
            host: Miner hostname or IP address
            scan_interval: Update interval in seconds
        """
        self.host = host
        self.session = async_get_clientsession(hass)
        self.base_url = f"http://{host}"

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    def get_device_info(self) -> dict:
        """Get device information dictionary for entity registration.

        Returns a consistent device info dict used by all entities to ensure
        they are grouped under the same device in Home Assistant.

        Returns:
            dict: Device information with identifiers, name, manufacturer, and model
        """
        from .const import ATTR_DEVICE_MODEL

        return {
            "identifiers": {(DOMAIN, self.host)},
            "name": f"NerdQAxe+ Miner ({self.host})",
            "manufacturer": "NerdQAxe",
            "model": self.data.get(ATTR_DEVICE_MODEL, "Unknown") if self.data else "Unknown",
        }

    async def _async_update_data(self) -> dict:
        """Fetch latest data from miner API.

        Polls the /api/system/info endpoint to retrieve current miner status,
        including hashrate, temperature, power metrics, and mining statistics.

        Returns:
            dict: Miner data with all sensor values

        Raises:
            UpdateFailed: If API communication fails or times out
        """
        try:
            async with asyncio.timeout(10):
                async with self.session.get(
                    f"{self.base_url}{API_SYSTEM_INFO}"
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    _LOGGER.debug("Received data from %s: %s", self.host, data)
                    return data
        except asyncio.TimeoutError:
            error_msg = f"Timeout connecting to miner at {self.host}"
            _LOGGER.warning(error_msg)
            raise UpdateFailed(error_msg)
        except aiohttp.ClientError as err:
            error_msg = f"Error communicating with API: {err}"
            _LOGGER.warning("Error communicating with miner API at %s: %s", self.host, err)
            raise UpdateFailed(error_msg)
        except Exception as err:
            error_msg = f"Unexpected error: {type(err).__name__}: {err}"
            _LOGGER.error(
                "Unexpected error fetching data from %s: %s\n%s",
                self.host,
                error_msg,
                traceback.format_exc()
            )
            raise UpdateFailed(error_msg)
