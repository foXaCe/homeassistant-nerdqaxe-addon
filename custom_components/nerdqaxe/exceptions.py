"""Exceptions for the NerdQAxe+ Miner integration."""

from homeassistant.exceptions import HomeAssistantError


class NerdQAxeError(HomeAssistantError):
    """Base exception for NerdQAxe+ integration."""


class NerdQAxeConnectionError(NerdQAxeError):
    """Exception raised when connection to miner fails."""


class NerdQAxeApiError(NerdQAxeError):
    """Exception raised when API returns an error."""


class NerdQAxeTimeoutError(NerdQAxeError):
    """Exception raised when connection times out."""
