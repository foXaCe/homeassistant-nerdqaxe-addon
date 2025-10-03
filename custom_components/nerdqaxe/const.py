"""Constants for the NerdQAxe+ Miner integration."""

DOMAIN = "nerdqaxe"

# Config
CONF_HOST = "host"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_NAME = "NerdQAxe+ Miner"

# API Endpoints
API_SYSTEM_INFO = "/api/system/info"
API_SYSTEM_ASIC = "/api/system/asic"
API_SYSTEM_RESTART = "/api/system/restart"
API_OTA_GITHUB = "/api/system/OTA/github"

# Attributes
ATTR_HASHRATE = "hashRate"
ATTR_HASHRATE_1M = "hashRate_1m"
ATTR_HASHRATE_10M = "hashRate_10m"
ATTR_HASHRATE_1H = "hashRate_1h"
ATTR_HASHRATE_1D = "hashRate_1d"
ATTR_TEMP = "temp"
ATTR_VR_TEMP = "vrTemp"
ATTR_POWER = "power"
ATTR_VOLTAGE = "voltage"
ATTR_CURRENT = "current"
ATTR_FAN_SPEED = "fanspeed"
ATTR_FAN_RPM = "fanrpm"
ATTR_SHARES_ACCEPTED = "sharesAccepted"
ATTR_SHARES_REJECTED = "sharesRejected"
ATTR_BEST_DIFF = "bestDiff"
ATTR_BEST_SESSION_DIFF = "bestSessionDiff"
ATTR_STRATUM_CONNECTED = "isStratumConnected"
ATTR_DEVICE_MODEL = "deviceModel"
ATTR_HOSTNAME = "hostname"
ATTR_MAC_ADDR = "macAddr"
ATTR_IP_ADDR = "hostip"
ATTR_WIFI_RSSI = "wifiRSSI"
ATTR_FOUND_BLOCKS = "foundBlocks"
ATTR_TOTAL_FOUND_BLOCKS = "totalFoundBlocks"
ATTR_CORE_VOLTAGE = "coreVoltage"
ATTR_FREQUENCY = "frequency"
ATTR_VERSION = "version"
ATTR_UPTIME = "uptimeSeconds"

# GitHub
GITHUB_REPO = "shufps/ESP-Miner-NerdQAxePlus"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases"

# Services
SERVICE_RESTART = "restart"
SERVICE_UPDATE_FIRMWARE = "update_firmware"
