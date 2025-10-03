"""Support for NerdQAxe+ Miner sensors."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NerdQAxeDataUpdateCoordinator
from .const import (
    DOMAIN,
    ATTR_HASHRATE,
    ATTR_HASHRATE_1M,
    ATTR_HASHRATE_10M,
    ATTR_HASHRATE_1H,
    ATTR_HASHRATE_1D,
    ATTR_TEMP,
    ATTR_VR_TEMP,
    ATTR_POWER,
    ATTR_VOLTAGE,
    ATTR_CURRENT,
    ATTR_FAN_SPEED,
    ATTR_FAN_RPM,
    ATTR_SHARES_ACCEPTED,
    ATTR_SHARES_REJECTED,
    ATTR_BEST_DIFF,
    ATTR_BEST_SESSION_DIFF,
    ATTR_DEVICE_MODEL,
    ATTR_HOSTNAME,
    ATTR_WIFI_RSSI,
    ATTR_FOUND_BLOCKS,
    ATTR_TOTAL_FOUND_BLOCKS,
    ATTR_CORE_VOLTAGE,
    ATTR_FREQUENCY,
    ATTR_VERSION,
    ATTR_UPTIME,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NerdQAxe+ Miner sensors."""
    coordinator: NerdQAxeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        # Hashrate sensors
        NerdQAxeSensor(
            coordinator,
            "hashrate",
            "Hashrate",
            ATTR_HASHRATE,
            icon="mdi:speedometer",
            unit="GH/s",
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        NerdQAxeSensor(
            coordinator,
            "hashrate_1m",
            "Hashrate 1m",
            ATTR_HASHRATE_1M,
            icon="mdi:speedometer",
            unit="GH/s",
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        NerdQAxeSensor(
            coordinator,
            "hashrate_10m",
            "Hashrate 10m",
            ATTR_HASHRATE_10M,
            icon="mdi:speedometer",
            unit="GH/s",
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        NerdQAxeSensor(
            coordinator,
            "hashrate_1h",
            "Hashrate 1h",
            ATTR_HASHRATE_1H,
            icon="mdi:speedometer",
            unit="GH/s",
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        NerdQAxeSensor(
            coordinator,
            "hashrate_1d",
            "Hashrate 1d",
            ATTR_HASHRATE_1D,
            icon="mdi:speedometer",
            unit="GH/s",
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        # Temperature sensors
        NerdQAxeSensor(
            coordinator,
            "temperature",
            "Chip Temperature",
            ATTR_TEMP,
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        NerdQAxeSensor(
            coordinator,
            "vr_temperature",
            "VR Temperature",
            ATTR_VR_TEMP,
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        # Power sensors
        NerdQAxeSensor(
            coordinator,
            "power",
            "Power",
            ATTR_POWER,
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        NerdQAxeSensor(
            coordinator,
            "voltage",
            "Voltage",
            ATTR_VOLTAGE,
            unit=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        NerdQAxeSensor(
            coordinator,
            "current",
            "Current",
            ATTR_CURRENT,
            unit=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        NerdQAxeSensor(
            coordinator,
            "core_voltage",
            "Core Voltage",
            ATTR_CORE_VOLTAGE,
            unit=UnitOfElectricPotential.MILLIVOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        # Fan sensors
        NerdQAxeSensor(
            coordinator,
            "fan_speed",
            "Fan Speed",
            ATTR_FAN_SPEED,
            icon="mdi:fan",
            unit=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        NerdQAxeSensor(
            coordinator,
            "fan_rpm",
            "Fan RPM",
            ATTR_FAN_RPM,
            icon="mdi:fan",
            unit="RPM",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        # Mining stats
        NerdQAxeSensor(
            coordinator,
            "shares_accepted",
            "Shares Accepted",
            ATTR_SHARES_ACCEPTED,
            icon="mdi:check-circle",
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        NerdQAxeSensor(
            coordinator,
            "shares_rejected",
            "Shares Rejected",
            ATTR_SHARES_REJECTED,
            icon="mdi:close-circle",
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        NerdQAxeSensor(
            coordinator,
            "best_difficulty",
            "Best Difficulty",
            ATTR_BEST_DIFF,
            icon="mdi:trophy",
        ),
        NerdQAxeSensor(
            coordinator,
            "best_session_difficulty",
            "Best Session Difficulty",
            ATTR_BEST_SESSION_DIFF,
            icon="mdi:trophy-outline",
        ),
        NerdQAxeSensor(
            coordinator,
            "found_blocks",
            "Found Blocks (Session)",
            ATTR_FOUND_BLOCKS,
            icon="mdi:cube",
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        NerdQAxeSensor(
            coordinator,
            "total_found_blocks",
            "Total Found Blocks",
            ATTR_TOTAL_FOUND_BLOCKS,
            icon="mdi:cube-outline",
            state_class=SensorStateClass.TOTAL,
        ),
        # Device info
        NerdQAxeSensor(
            coordinator,
            "device_model",
            "Device Model",
            ATTR_DEVICE_MODEL,
            icon="mdi:chip",
        ),
        NerdQAxeSensor(
            coordinator,
            "hostname",
            "Hostname",
            ATTR_HOSTNAME,
            icon="mdi:server",
        ),
        NerdQAxeSensor(
            coordinator,
            "wifi_rssi",
            "WiFi RSSI",
            ATTR_WIFI_RSSI,
            icon="mdi:wifi",
            unit="dBm",
            device_class=SensorDeviceClass.SIGNAL_STRENGTH,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        NerdQAxeSensor(
            coordinator,
            "frequency",
            "ASIC Frequency",
            ATTR_FREQUENCY,
            icon="mdi:sine-wave",
            unit="MHz",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        NerdQAxeSensor(
            coordinator,
            "version",
            "Firmware Version",
            ATTR_VERSION,
            icon="mdi:information-outline",
        ),
        NerdQAxeUptimeSensor(coordinator),
    ]

    async_add_entities(entities)


class NerdQAxeSensor(CoordinatorEntity, SensorEntity):
    """Representation of a NerdQAxe+ Miner sensor."""

    def __init__(
        self,
        coordinator: NerdQAxeDataUpdateCoordinator,
        sensor_id: str,
        name: str,
        data_key: str,
        icon: str | None = None,
        unit: str | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_{sensor_id}"
        self._attr_name = f"NerdQAxe {name}"
        self._data_key = data_key
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": f"NerdQAxe+ Miner ({coordinator.host})",
            "manufacturer": "NerdQAxe",
            "model": coordinator.data.get(ATTR_DEVICE_MODEL, "Unknown") if coordinator.data else "Unknown",
        }

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        value = self.coordinator.data.get(self._data_key)

        # Round numeric values
        if isinstance(value, (int, float)):
            if self._data_key in [ATTR_HASHRATE, ATTR_HASHRATE_1M, ATTR_HASHRATE_10M, ATTR_HASHRATE_1H, ATTR_HASHRATE_1D]:
                return round(value, 2)
            elif self._data_key in [ATTR_TEMP, ATTR_VR_TEMP]:
                return round(value, 1)
            elif self._data_key in [ATTR_POWER, ATTR_VOLTAGE, ATTR_CURRENT]:
                return round(value, 2)

        return value


class NerdQAxeUptimeSensor(CoordinatorEntity, SensorEntity):
    """Representation of NerdQAxe+ uptime sensor with formatted display."""

    def __init__(self, coordinator: NerdQAxeDataUpdateCoordinator) -> None:
        """Initialize the uptime sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_uptime"
        self._attr_name = "NerdQAxe Uptime"
        self._attr_icon = "mdi:clock-outline"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": f"NerdQAxe+ Miner ({coordinator.host})",
            "manufacturer": "NerdQAxe",
            "model": coordinator.data.get(ATTR_DEVICE_MODEL, "Unknown") if coordinator.data else "Unknown",
        }

    @property
    def native_value(self):
        """Return formatted uptime."""
        if not self.coordinator.data:
            return None

        uptime_seconds = self.coordinator.data.get(ATTR_UPTIME)
        if uptime_seconds is None:
            return None

        # Convert seconds to days, hours, minutes
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60

        # Format display based on duration
        if days > 0:
            return f"{days}d {hours}h {minutes}min"
        elif hours > 0:
            return f"{hours}h {minutes}min"
        else:
            return f"{minutes}min"
