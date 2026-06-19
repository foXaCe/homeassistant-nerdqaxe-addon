"""DataUpdateCoordinator for NerdQAxe+ Miner integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any, cast

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_SYSTEM_INFO,
    ATTR_DEVICE_MODEL,
    ATTR_VERSION,
    DOMAIN,
)
from .exceptions import (
    NerdQAxeApiError,
    NerdQAxeConnectionError,
    NerdQAxeTimeoutError,
)

if TYPE_CHECKING:
    from aiohttp import ClientSession

    from .const import NerdQAxeConfigEntry

_LOGGER = logging.getLogger(__name__)

# Debounce requests by 1 second to avoid hammering the device
REQUEST_REFRESH_DEBOUNCE = 1.0

# Timeout configuration (seconds)
TIMEOUT_CONNECT = 10  # Time to establish connection
TIMEOUT_TOTAL = 30  # Total request time including response


class NerdQAxeDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching NerdQAxe+ Miner data from API.

    Handles periodic polling of the miner's REST API endpoint and distributes
    data to all platform entities via the coordinator pattern.
    """

    config_entry: NerdQAxeConfigEntry

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
        self.session: ClientSession = async_get_clientsession(hass)
        self.base_url = f"http://{host}"

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
            request_refresh_debouncer=Debouncer(
                hass,
                _LOGGER,
                cooldown=REQUEST_REFRESH_DEBOUNCE,
                immediate=False,
            ),
        )

    @property
    def unique_id_base(self) -> str:
        """Return the stable id base (device MAC) for entities and device.

        The config entry's unique id is the miner MAC address, which is stable
        across IP changes. Falls back to the host on legacy/edge setups where
        the entry has no unique id, so entities keep a deterministic id.

        Returns:
            str: MAC address if available, otherwise the host

        """
        entry: NerdQAxeConfigEntry | None = getattr(self, "config_entry", None)
        if entry is not None and entry.unique_id:
            return entry.unique_id
        return self.host

    def get_device_info(self) -> DeviceInfo:
        """Get device information dictionary for entity registration.

        Returns a consistent device info dict used by all entities to ensure
        they are grouped under the same device in Home Assistant. The device is
        identified by its MAC address (stable across IP changes).

        Returns:
            DeviceInfo: Device info (identifiers, connections, metadata)

        """
        entry: NerdQAxeConfigEntry | None = getattr(self, "config_entry", None)
        mac = entry.unique_id if entry is not None else None

        sw_version: str | None = None
        model = "Unknown"
        if self.data:
            model = self.data.get(ATTR_DEVICE_MODEL, "Unknown")
            version = self.data.get(ATTR_VERSION)
            if isinstance(version, str):
                sw_version = version.lstrip("v")

        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id_base)},
            connections={(CONNECTION_NETWORK_MAC, mac)} if mac else set(),
            name=f"NerdQAxe+ Miner ({self.host})",
            manufacturer="NerdQAxe",
            model=model,
            sw_version=sw_version,
            configuration_url=f"http://{self.host}",
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest data from miner API.

        Polls the /api/system/info endpoint to retrieve current miner status,
        including hashrate, temperature, power metrics, and mining statistics.

        Returns:
            dict: Miner data with all sensor values

        Raises:
            UpdateFailed: If API communication fails or times out

        """
        url = f"{self.base_url}{API_SYSTEM_INFO}"
        timeout = aiohttp.ClientTimeout(
            total=TIMEOUT_TOTAL,
            connect=TIMEOUT_CONNECT,
        )

        try:
            async with self.session.get(url, timeout=timeout) as response:
                response.raise_for_status()
                data = await response.json()
                _LOGGER.debug("Received data from %s: %s", self.host, data)
                return cast(dict[str, Any], data)
        except aiohttp.ServerTimeoutError as err:
            # Server timeout - must come before TimeoutError (it inherits from it)
            error_msg = f"Timeout connecting to miner at {self.host}"
            _LOGGER.debug("%s: %s", error_msg, type(err).__name__)
            raise UpdateFailed(error_msg) from NerdQAxeTimeoutError(error_msg)
        except (aiohttp.ClientConnectorError, TimeoutError) as err:
            # Normal connection errors (device offline) - log as debug
            error_msg = (
                f"Cannot connect to miner at {self.host} (device may be offline)"
            )
            _LOGGER.debug("%s: %s", error_msg, type(err).__name__)
            raise UpdateFailed(error_msg) from NerdQAxeConnectionError(error_msg)
        except aiohttp.ClientResponseError as err:
            # HTTP errors (4xx, 5xx) - log as warning
            error_msg = f"Error communicating with miner API: {type(err).__name__}"
            _LOGGER.warning(
                "Error communicating with miner at %s: %s (status=%s)",
                self.host,
                type(err).__name__,
                err.status,
            )
            raise UpdateFailed(error_msg) from NerdQAxeApiError(error_msg)
        except aiohttp.ClientError as err:
            # Other client errors - log as warning
            error_msg = f"Error communicating with miner API: {type(err).__name__}"
            _LOGGER.warning(
                "Error communicating with miner at %s: %s",
                self.host,
                type(err).__name__,
            )
            raise UpdateFailed(error_msg) from NerdQAxeApiError(error_msg)
        except Exception as err:
            # Truly unexpected errors - log as error with full traceback
            error_msg = f"Unexpected error: {type(err).__name__}: {err!s}"
            _LOGGER.error(
                "Unexpected error fetching data from %s: %s",
                self.host,
                error_msg,
                exc_info=True,
            )
            raise UpdateFailed(error_msg) from err
