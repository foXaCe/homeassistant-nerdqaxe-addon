"""DataUpdateCoordinator for NerdQAxe+ Miner integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_SYSTEM_INFO,
    ATTR_DEVICE_MODEL,
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

    def get_device_info(self) -> dict[str, Any]:
        """Get device information dictionary for entity registration.

        Returns a consistent device info dict used by all entities to ensure
        they are grouped under the same device in Home Assistant.

        Returns:
            dict: Device information with identifiers, name, manufacturer, and model

        Note:
            TODO(v2.0.0): Use mac_addr instead of host for identifiers to ensure
            stability when device IP changes. This is a breaking change that will
            require users to reconfigure their dashboards/automations.
            See: ATTR_MAC_ADDR in const.py

        """
        # TODO(v2.0.0): Change to {(DOMAIN, self.data.get(ATTR_MAC_ADDR, self.host))}
        return {
            "identifiers": {(DOMAIN, self.host)},
            "name": f"NerdQAxe+ Miner ({self.host})",
            "manufacturer": "NerdQAxe",
            "model": self.data.get(ATTR_DEVICE_MODEL, "Unknown")
            if self.data
            else "Unknown",
        }

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
                return data
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
