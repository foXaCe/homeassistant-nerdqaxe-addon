"""Diagnostics support for NerdQAxe+ Miner."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import NerdQAxeConfigEntry

# Keys to redact from diagnostics output
TO_REDACT = {
    "host",
    "hostip",
    "macAddr",
    "hostname",
    "wifiSSID",
    "stratumUser",
    "stratumPassword",
    "stratumURL",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: NerdQAxeConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry.

    Provides debug information for troubleshooting while redacting
    sensitive data like IP addresses, MAC addresses, and credentials.

    Args:
        hass: Home Assistant instance
        entry: Config entry to get diagnostics for

    Returns:
        dict: Diagnostic data with sensitive information redacted

    """
    coordinator = entry.runtime_data.coordinator

    return {
        "entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "domain": entry.domain,
            "title": entry.title,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": async_redact_data(dict(entry.options), TO_REDACT),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
        },
        "data": async_redact_data(coordinator.data, TO_REDACT)
        if coordinator.data
        else None,
    }
