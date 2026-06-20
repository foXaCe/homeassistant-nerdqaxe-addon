"""Constants for the NerdQAxe+ Miner integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .coordinator import NerdQAxeDataUpdateCoordinator

DOMAIN: Final = "nerdqaxe"

# ConfigEntry typé (Platinum)
type NerdQAxeConfigEntry = ConfigEntry[NerdQAxeRuntimeData]


@dataclass(slots=True)
class NerdQAxeRuntimeData:
    """Runtime data stored on the config entry."""

    coordinator: NerdQAxeDataUpdateCoordinator


# Config
CONF_HOST: Final = "host"
CONF_SCAN_INTERVAL: Final = "scan_interval"

# Defaults
DEFAULT_SCAN_INTERVAL: Final = 30
DEFAULT_NAME: Final = "NerdQAxe+ Miner"
MIN_SCAN_INTERVAL: Final = 5
MAX_SCAN_INTERVAL: Final = 300

# API Endpoints
API_SYSTEM_INFO: Final = "/api/system/info"
API_SYSTEM_ASIC: Final = "/api/system/asic"
API_SYSTEM_RESTART: Final = "/api/system/restart"
API_OTA_GITHUB: Final = "/api/system/OTA/github"  # Combined factory OTA (fw + www)

# Attributes
ATTR_HASHRATE: Final = "hashRate"
ATTR_HASHRATE_1M: Final = "hashRate_1m"
ATTR_HASHRATE_10M: Final = "hashRate_10m"
ATTR_HASHRATE_1H: Final = "hashRate_1h"
ATTR_HASHRATE_1D: Final = "hashRate_1d"
ATTR_TEMP: Final = "temp"
ATTR_VR_TEMP: Final = "vrTemp"
ATTR_POWER: Final = "power"
ATTR_VOLTAGE: Final = "voltage"
ATTR_CURRENT: Final = "current"
ATTR_FAN_SPEED: Final = "fanspeed"
ATTR_FAN_RPM: Final = "fanrpm"
# Second fan, present on dual-fan boards (NerdQAxe++, NerdOCTAXE, ...)
ATTR_FAN_SPEED_2: Final = "fanspeed2"
ATTR_FAN_RPM_2: Final = "fanrpm2"
ATTR_FAN_COUNT: Final = "fanCount"
ATTR_SHARES_ACCEPTED: Final = "sharesAccepted"
ATTR_SHARES_REJECTED: Final = "sharesRejected"
ATTR_BEST_DIFF: Final = "bestDiff"
ATTR_BEST_SESSION_DIFF: Final = "bestSessionDiff"
# Legacy flat field, kept for backward compatibility. Modern firmware exposes
# the connection state inside the nested ``stratum.pools[].connected`` structure.
ATTR_STRATUM_CONNECTED: Final = "isStratumConnected"
ATTR_STRATUM: Final = "stratum"
ATTR_STRATUM_POOLS: Final = "pools"
ATTR_POOL_CONNECTED: Final = "connected"
ATTR_DEVICE_MODEL: Final = "deviceModel"
ATTR_HOSTNAME: Final = "hostname"
ATTR_WIFI_RSSI: Final = "wifiRSSI"
ATTR_FOUND_BLOCKS: Final = "foundBlocks"
ATTR_TOTAL_FOUND_BLOCKS: Final = "totalFoundBlocks"
ATTR_CORE_VOLTAGE: Final = "coreVoltage"
ATTR_CORE_VOLTAGE_ACTUAL: Final = "coreVoltageActual"
ATTR_FREQUENCY: Final = "frequency"
ATTR_VERSION: Final = "version"
ATTR_UPTIME: Final = "uptimeSeconds"

# GitHub
GITHUB_REPO: Final = "shufps/ESP-Miner-NerdQAxePlus"
GITHUB_API_URL: Final = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
