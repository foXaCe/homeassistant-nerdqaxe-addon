# NerdQAxe+ Miner - Home Assistant HACS Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

HACS integration to monitor and control your NerdQAxe+ Bitcoin Miner in Home Assistant.

## 💰 Soutenir le Projet

Si cette intégration vous est utile, vous pouvez soutenir son développement avec un don en Bitcoin :

**🪙 Adresse Bitcoin :** `bc1qhe4ge22x0anuyeg0fmts6rdmz3t735dnqwt3p7`

Vos contributions m'aident à continuer d'améliorer ce projet et à ajouter de nouvelles fonctionnalités. Merci ! 🙏


## Description

This custom integration allows you to integrate your NerdQAxe+ miner into Home Assistant. It automatically creates sensors to monitor performance, temperature, power consumption, and more.

**Integration type:** Custom Component HACS (not a Docker addon)

## Project Architecture

### NerdQAxe+ REST API

The NerdQAxe+ firmware already exposes a complete REST API (no firmware modifications needed):

**Available endpoints:**
- `GET /api/system/info` - Complete system information
- `GET /api/system/asic` - ASIC information
- `GET /api/swarm/info` - Swarm information
- `PATCH /api/system` - Modify configuration
- `POST /api/system/restart` - Restart the miner

**Data returned by `/api/system/info`:**
```json
{
  "hashRate": 1200.5,
  "hashRate_1m": 1185.2,
  "hashRate_1h": 1150.8,
  "temp": 65.3,
  "vrTemp": 58.7,
  "power": 15.2,
  "voltage": 12.1,
  "current": 1.25,
  "fanspeed": 75,
  "fanrpm": 4500,
  "sharesAccepted": 1234,
  "sharesRejected": 5,
  "isStratumConnected": true,
  "deviceModel": "NerdQAxePlus",
  "hostname": "nerdqaxe-123",
  "version": "2.0.3"
}
```

### Integration Structure

```
custom_components/nerdqaxe/
├── __init__.py          # Initialization and coordinator
├── manifest.json        # Integration metadata
├── const.py             # Constants
├── config_flow.py       # UI configuration
├── sensor.py            # Sensors (hashrate, temp, power, etc.)
├── binary_sensor.py     # Binary sensors (stratum connected)
├── button.py            # Restart button
├── number.py            # Number controls (frequency, voltage)
└── update.py            # Firmware update entity
```

## Created Sensors

The integration automatically creates the following sensors:

### Hashrate
- `sensor.nerdqaxe_hashrate` - Current hashrate (GH/s)
- `sensor.nerdqaxe_hashrate_1m` - 1-minute average hashrate (GH/s)
- `sensor.nerdqaxe_hashrate_10m` - 10-minute average hashrate (GH/s)
- `sensor.nerdqaxe_hashrate_1h` - 1-hour average hashrate (GH/s)
- `sensor.nerdqaxe_hashrate_1d` - 1-day average hashrate (GH/s)

### Temperature
- `sensor.nerdqaxe_temperature` - Chip temperature (°C)
- `sensor.nerdqaxe_vr_temperature` - Voltage regulator temperature (°C)

### Power
- `sensor.nerdqaxe_power` - Power consumption (W)
- `sensor.nerdqaxe_voltage` - Voltage (V)
- `sensor.nerdqaxe_current` - Current (A)
- `sensor.nerdqaxe_core_voltage` - Core voltage (mV)

### Cooling
- `sensor.nerdqaxe_fan_speed` - Fan speed (%)
- `sensor.nerdqaxe_fan_rpm` - Fan RPM

### Mining
- `sensor.nerdqaxe_shares_accepted` - Accepted shares
- `sensor.nerdqaxe_shares_rejected` - Rejected shares
- `sensor.nerdqaxe_best_difficulty` - Best difficulty found
- `sensor.nerdqaxe_best_session_difficulty` - Best session difficulty
- `sensor.nerdqaxe_found_blocks` - Blocks found (current session)
- `sensor.nerdqaxe_total_found_blocks` - Total blocks found
- `binary_sensor.nerdqaxe_stratum_connected` - Pool connection status

### Information
- `sensor.nerdqaxe_device_model` - Device model
- `sensor.nerdqaxe_hostname` - Miner hostname
- `sensor.nerdqaxe_wifi_rssi` - WiFi signal strength (dBm)
- `sensor.nerdqaxe_frequency` - ASIC frequency (MHz)
- `sensor.nerdqaxe_version` - Firmware version

### Control and Updates
- `button.nerdqaxe_restart` - Button to restart the miner
- `number.nerdqaxe_asic_frequency` - ASIC frequency control (400-575 MHz)
- `number.nerdqaxe_core_voltage` - Core voltage control (1000-1300 mV)
- `update.nerdqaxe_firmware_update` - Firmware update entity (automatically checks for new versions on GitHub)

## Installation

### Method 1: Via HACS (recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the 3 dots in the top right → "Custom repositories"
4. Add URL: `https://github.com/foXaCe/homeassistant-nerdqaxe-addon`
5. Category: "Integration"
6. Click "Add"
7. Search for "NerdQAxe+" and install
8. Restart Home Assistant

### Method 2: Manual Installation

1. Download the `custom_components/nerdqaxe` folder
2. Copy to `<config>/custom_components/nerdqaxe`
3. Restart Home Assistant

## Configuration

### Via User Interface

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "NerdQAxe+"
4. Enter your miner's IP address (e.g., `192.168.1.100`)
5. The integration will connect and automatically create all sensors

### Options

After installation, you can configure:
- **Scan interval**: Update interval in seconds (5-300, default: 30)

To modify options:
1. Go to **Settings** → **Devices & Services**
2. Find "NerdQAxe+ Miner"
3. Click **Options**

## Usage

### Example Lovelace Card

```yaml
type: entities
title: NerdQAxe+ Miner
entities:
  - entity: sensor.nerdqaxe_hashrate
    name: Hashrate
  - entity: sensor.nerdqaxe_hashrate_1h
    name: Hashrate 1h
  - entity: sensor.nerdqaxe_temperature
    name: Temperature
  - entity: sensor.nerdqaxe_power
    name: Power
  - entity: sensor.nerdqaxe_shares_accepted
    name: Accepted Shares
  - entity: binary_sensor.nerdqaxe_stratum_connected
    name: Pool Connected
```

### Card with Graph

```yaml
type: vertical-stack
cards:
  - type: entities
    title: NerdQAxe+ Miner
    entities:
      - entity: sensor.nerdqaxe_hashrate_1h
        name: Hashrate 1h
      - entity: sensor.nerdqaxe_temperature
      - entity: sensor.nerdqaxe_power
      - entity: binary_sensor.nerdqaxe_stratum_connected

  - type: history-graph
    title: Hashrate
    hours_to_show: 24
    entities:
      - entity: sensor.nerdqaxe_hashrate_1h

  - type: history-graph
    title: Temperature
    hours_to_show: 24
    entities:
      - entity: sensor.nerdqaxe_temperature
```

### Automation Example - High Temperature Alert

```yaml
automation:
  - alias: "High Miner Temperature Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nerdqaxe_temperature
        above: 80
    action:
      - service: notify.mobile_app
        data:
          message: "⚠️ High miner temperature: {{ states('sensor.nerdqaxe_temperature') }}°C"
          title: "NerdQAxe+ Alert"
```

### Automation Example - Pool Disconnected

```yaml
automation:
  - alias: "Pool Disconnected Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.nerdqaxe_stratum_connected
        to: "off"
        for: "00:05:00"
    action:
      - service: notify.mobile_app
        data:
          message: "⚠️ NerdQAxe+ miner disconnected from pool for 5 minutes"
```

### Automation Example - Low Hashrate

```yaml
automation:
  - alias: "Low Hashrate Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nerdqaxe_hashrate_1h
        below: 1000
        for: "00:10:00"
    action:
      - service: notify.mobile_app
        data:
          message: "⚠️ Low hashrate: {{ states('sensor.nerdqaxe_hashrate_1h') }} GH/s"
```

### Miner Restart

The restart button is available in the interface:

```yaml
type: button
entity: button.nerdqaxe_restart
name: Restart Miner
icon: mdi:restart
```

Or in an automation:

```yaml
automation:
  - alias: "Auto Restart if Pool Disconnected"
    trigger:
      - platform: state
        entity_id: binary_sensor.nerdqaxe_stratum_connected
        to: "off"
        for: "00:15:00"
    action:
      - service: button.press
        target:
          entity_id: button.nerdqaxe_restart
      - service: notify.mobile_app
        data:
          message: "🔄 Restarting miner due to prolonged pool disconnection"
```

### Frequency and Voltage Control

Control your miner's performance by adjusting frequency and core voltage:

**In Lovelace:**

```yaml
type: entities
title: Miner Performance Control
entities:
  - entity: number.nerdqaxe_asic_frequency
    name: ASIC Frequency
  - entity: number.nerdqaxe_core_voltage
    name: Core Voltage
  - entity: sensor.nerdqaxe_power
    name: Current Power
  - entity: sensor.nerdqaxe_temperature
    name: Temperature
```

**Via Automation:**

```yaml
automation:
  - alias: "Reduce Power on High Temperature"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nerdqaxe_temperature
        above: 75
    action:
      - service: number.set_value
        target:
          entity_id: number.nerdqaxe_asic_frequency
        data:
          value: 450
      - service: notify.mobile_app
        data:
          message: "⚠️ Temperature high, reducing frequency to 450 MHz"
```

### Firmware Updates

The `update.nerdqaxe_firmware_update` entity automatically checks for new versions on GitHub:

**Display in Lovelace:**

```yaml
type: update
entity: update.nerdqaxe_firmware_update
show_title: true
show_current_version: true
show_latest_version: true
```

**Installing an Update:**

The update entity automatically appears in the Home Assistant dashboard when a new version is available. Simply click "Install" to download and flash the new version directly from GitHub.

**Important note:** The miner will automatically restart after the update installation.

## Development

### Technical Architecture

#### `__init__.py`
Main file that:
- Initializes the integration
- Creates the `DataUpdateCoordinator` to manage updates
- Configures platforms (sensor, binary_sensor, button, update)

**`NerdQAxeDataUpdateCoordinator` Class:**
- Connects to `http://<host>/api/system/info` every X seconds
- Parses JSON data
- Distributes data to sensors via the Coordinator pattern

#### `config_flow.py`
Handles UI configuration:
- Validates miner connection
- Configures scan interval
- Automatic detection of hostname and model

#### `sensor.py`
Defines all sensors:
- Uses `CoordinatorEntity` for automatic updates
- Appropriate device classes for Energy Dashboard
- State classes for long-term statistics

#### `binary_sensor.py`
Binary sensor for Stratum pool connection status.

#### `button.py`
Defines the restart button:
- Calls the miner's `POST /api/system/restart` API
- Restarts the miner instantly

#### `number.py`
Number entities for performance control:
- ASIC frequency control (400-575 MHz)
- Core voltage control (1000-1300 mV)
- Calls the miner's `POST /api/system/asic` API
- Automatically refreshes coordinator after changes

#### `update.py`
Firmware update entity:
- Automatically checks GitHub releases
- Compares installed version with latest available version
- Filters pre-releases and RC versions
- Downloads and installs firmware directly from GitHub
- Uses the `POST /api/system/OTA/github` endpoint with firmware URL
- Displays release notes in Home Assistant
- Checks for updates every 6 hours

### Adding a New Sensor

1. In `const.py`, add the constant:
```python
ATTR_NEW_FIELD = "newField"
```

2. In `sensor.py`, add to the `entities` list:
```python
NerdQAxeSensor(
    coordinator,
    "new_sensor",
    "Sensor Name",
    ATTR_NEW_FIELD,
    icon="mdi:icon-name",
    unit="unit",
    device_class=SensorDeviceClass.XXX,
    state_class=SensorStateClass.MEASUREMENT,
),
```

### Local Testing

1. Copy `custom_components/nerdqaxe` to your HA config
2. Restart HA
3. Add the integration via UI
4. Check logs: **Settings** → **System** → **Logs**

### Debug

Enable debug logs in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.nerdqaxe: debug
```

## Roadmap / Future Features

### ✅ Implemented Features:
- [x] Miner restart button
- [x] Update entity with automatic GitHub version checking
- [x] Firmware version sensor
- [x] HA Energy Dashboard integration (power, voltage, current sensors)
- [x] Uptime sensors (via 1d hashrate)
- [x] Periodic update checks (every 6 hours)
- [x] Number entities to dynamically modify frequency/voltage

### 🔜 Features to Add:
- [ ] WebSocket support for real-time hashrate updates
- [ ] Multi-miner support (multiple devices in one integration)
- [ ] Network auto-discovery of miners (mDNS)
- [ ] Pre-configured Lovelace dashboard with all cards
- [ ] Pool difficulty sensor
- [ ] Configurable alerts via UI
- [ ] Update available notifications
- [ ] Miner configuration backup/restore

### Possible Improvements:
- Add Home Assistant services to control the miner
- Support multiple miners with a single entry
- Integrated performance graphs
- Configurable push notifications via UI
- Support for NerdAxeGamma boards and other variants

## Contributing

Contributions are welcome! Feel free to:
- Open an issue for a bug or feature request
- Submit a pull request
- Improve documentation

## License

MIT

## Credits

- **NerdQAxe+ Firmware**: https://github.com/shufps/ESP-Miner-NerdQAxePlus
- **NerdQAxe+ Hardware**: https://github.com/shufps/qaxe
- **BitAxe devs**: @skot (ESP-Miner), @ben, @jhonny
- **NerdAxe dev**: @BitMaker

## Support

- **HA Integration Issues**: [GitHub Issues](https://github.com/foXaCe/homeassistant-nerdqaxe-addon/issues)
- **Firmware Issues**: [ESP-Miner-NerdQAxePlus Issues](https://github.com/shufps/ESP-Miner-NerdQAxePlus/issues)
- **NerdMiner Discord**: [![Discord](https://dcbadge.vercel.app/api/server/3E8ca2dkcC)](https://discord.gg/3E8ca2dkcC)
