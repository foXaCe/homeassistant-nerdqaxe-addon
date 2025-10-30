"""Config flow for NerdQAxe+ Miner integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_NAME,
    API_SYSTEM_INFO,
)

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
        CannotConnect: If connection to miner fails
    """
    host = data[CONF_HOST]
    session = async_get_clientsession(hass)

    _LOGGER.debug("Validating connection to NerdQAxe+ miner at %s", host)

    try:
        async with async_timeout.timeout(10):
            async with session.get(f"http://{host}{API_SYSTEM_INFO}") as response:
                response.raise_for_status()
                result = await response.json()

                _LOGGER.info("Successfully connected to miner at %s (hostname: %s)", host, result.get("hostname", "unknown"))

                # Return info that you want to store in the config entry.
                return {
                    "title": result.get("hostname", DEFAULT_NAME),
                    "device_model": result.get("deviceModel", "Unknown"),
                    "mac_addr": result.get("macAddr", "Unknown"),
                }
    except aiohttp.ClientError as err:
        _LOGGER.error("Could not connect to NerdQAxe+ Miner at %s: %s", host, err)
        raise CannotConnect
    except Exception as err:
        _LOGGER.error("Unexpected exception during validation for %s: %s", host, err)
        raise CannotConnect


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NerdQAxe+ Miner integration.

    Provides UI-based configuration with miner host validation and
    unique device identification via MAC address.
    """

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step.

        Args:
            user_input: User-provided configuration data

        Returns:
            FlowResult: Form to show or config entry to create
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
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

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler.

        Args:
            config_entry: Config entry to manage options for

        Returns:
            OptionsFlowHandler: Options flow handler instance
        """
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for NerdQAxe+ integration.

    Allows users to configure scan interval after initial setup.
    """

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow.

        Args:
            config_entry: Config entry to manage options for
        """
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the integration options.

        Args:
            user_input: User-provided options data

        Returns:
            FlowResult: Form to show or options entry to create
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


class CannotConnect(Exception):
    """Exception raised when connection to miner fails."""
