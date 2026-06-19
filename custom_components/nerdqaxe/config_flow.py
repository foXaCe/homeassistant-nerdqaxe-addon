"""Config flow for NerdQAxe+ Miner integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import async_timeout
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol

from .const import (
    API_SYSTEM_INFO,
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .exceptions import NerdQAxeConnectionError

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect to the miner.

    Tests connection to the miner API and retrieves device information
    for config entry creation.

    Args:
        hass: Home Assistant instance
        data: User input data containing host

    Returns:
        dict: Device information (title, device_model, mac_addr)

    Raises:
        NerdQAxeConnectionError: If connection to miner fails

    """
    host = data[CONF_HOST]
    session = async_get_clientsession(hass)

    _LOGGER.debug("Validating connection to NerdQAxe+ miner at %s", host)

    try:
        async with async_timeout.timeout(10):
            async with session.get(f"http://{host}{API_SYSTEM_INFO}") as response:
                response.raise_for_status()
                result = await response.json()

                _LOGGER.info(
                    "Successfully connected to miner at %s (hostname: %s)",
                    host,
                    result.get("hostname", "unknown"),
                )

                return {
                    "title": result.get("hostname", DEFAULT_NAME),
                    "device_model": result.get("deviceModel", "Unknown"),
                    "mac_addr": result.get("macAddr", "Unknown"),
                }
    except aiohttp.ClientError as err:
        _LOGGER.error("Could not connect to NerdQAxe+ Miner at %s: %s", host, err)
        raise NerdQAxeConnectionError(f"Cannot connect to miner at {host}") from err
    except TimeoutError as err:
        _LOGGER.error("Timeout connecting to NerdQAxe+ Miner at %s", host)
        raise NerdQAxeConnectionError(f"Timeout connecting to miner at {host}") from err
    except Exception as err:
        _LOGGER.error("Unexpected exception during validation for %s: %s", host, err)
        raise NerdQAxeConnectionError(f"Unexpected error: {err}") from err


class NerdQAxeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NerdQAxe+ Miner integration.

    Provides UI-based configuration with miner host validation and
    unique device identification via MAC address.
    """

    VERSION = 2

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._host: str | None = None
        self._mac_addr: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial setup step.

        Args:
            user_input: User-provided configuration data

        Returns:
            ConfigFlowResult: Form to show or config entry to create

        """
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except NerdQAxeConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["mac_addr"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the miner.

        Allows changing the host/IP address without removing the config entry.

        Args:
            user_input: User-provided configuration data

        Returns:
            ConfigFlowResult: Form to show or reconfigured entry

        """
        reconfigure_entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except NerdQAxeConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during reconfigure")
                errors["base"] = "unknown"
            else:
                # Verify it's the same device by checking MAC address
                if info["mac_addr"] != reconfigure_entry.unique_id:
                    # Different device - update unique_id
                    await self.async_set_unique_id(info["mac_addr"])
                    self._abort_if_unique_id_configured()

                return self.async_update_reload_and_abort(
                    reconfigure_entry,
                    data={**reconfigure_entry.data, CONF_HOST: user_input[CONF_HOST]},
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=reconfigure_entry.data.get(CONF_HOST),
                    ): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Get the options flow for this handler.

        Args:
            config_entry: Config entry to manage options for

        Returns:
            OptionsFlow: Options flow handler instance

        """
        return NerdQAxeOptionsFlow()


class NerdQAxeOptionsFlow(OptionsFlow):
    """Handle options flow for NerdQAxe+ integration.

    Allows users to configure scan interval after initial setup.
    """

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the integration options.

        Args:
            user_input: User-provided options data

        Returns:
            ConfigFlowResult: Form to show or options entry to create

        """
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
                }
            ),
        )
