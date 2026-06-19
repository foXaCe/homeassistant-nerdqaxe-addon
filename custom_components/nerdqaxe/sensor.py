"""Support for NerdQAxe+ Miner sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NerdQAxeConfigEntry, NerdQAxeDataUpdateCoordinator
from .const import (
    ATTR_BEST_DIFF,
    ATTR_BEST_SESSION_DIFF,
    ATTR_CORE_VOLTAGE,
    ATTR_CORE_VOLTAGE_ACTUAL,
    ATTR_CURRENT,
    ATTR_DEVICE_MODEL,
    ATTR_FAN_RPM,
    ATTR_FAN_SPEED,
    ATTR_FOUND_BLOCKS,
    ATTR_FREQUENCY,
    ATTR_HASHRATE,
    ATTR_HASHRATE_1D,
    ATTR_HASHRATE_1H,
    ATTR_HASHRATE_1M,
    ATTR_HASHRATE_10M,
    ATTR_HOSTNAME,
    ATTR_POWER,
    ATTR_SHARES_ACCEPTED,
    ATTR_SHARES_REJECTED,
    ATTR_TEMP,
    ATTR_TOTAL_FOUND_BLOCKS,
    ATTR_UPTIME,
    ATTR_VERSION,
    ATTR_VOLTAGE,
    ATTR_VR_TEMP,
    ATTR_WIFI_RSSI,
)

_LOGGER = logging.getLogger(__name__)

# All entities read from a single coordinator; updates are not per-entity.
PARALLEL_UPDATES = 0

# Custom units not provided by Home Assistant constants
UNIT_GIGAHASH_PER_SECOND = "GH/s"
UNIT_REVOLUTIONS_PER_MINUTE = "RPM"
UNIT_MEGAHERTZ = "MHz"
UNIT_DECIBEL_MILLIWATT = "dBm"


def _clean_version(data: dict[str, Any]) -> StateType:
    """Return the firmware version without its leading ``v`` prefix."""
    version = data.get(ATTR_VERSION)
    if isinstance(version, str):
        return version.lstrip("v")
    return version


@dataclass(frozen=True, kw_only=True)
class NerdQAxeSensorEntityDescription(SensorEntityDescription):
    """Describes a NerdQAxe+ sensor entity.

    ``value_fn`` extracts the native value from the coordinator data dict, which
    keeps all per-sensor logic declarative and in one place.
    """

    value_fn: Callable[[dict[str, Any]], StateType]


SENSORS: tuple[NerdQAxeSensorEntityDescription, ...] = (
    # Hashrate
    NerdQAxeSensorEntityDescription(
        key="hashrate",
        icon="mdi:speedometer",
        native_unit_of_measurement=UNIT_GIGAHASH_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: data.get(ATTR_HASHRATE),
    ),
    NerdQAxeSensorEntityDescription(
        key="hashrate_1m",
        icon="mdi:speedometer",
        native_unit_of_measurement=UNIT_GIGAHASH_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: data.get(ATTR_HASHRATE_1M),
    ),
    NerdQAxeSensorEntityDescription(
        key="hashrate_10m",
        icon="mdi:speedometer",
        native_unit_of_measurement=UNIT_GIGAHASH_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: data.get(ATTR_HASHRATE_10M),
    ),
    NerdQAxeSensorEntityDescription(
        key="hashrate_1h",
        icon="mdi:speedometer",
        native_unit_of_measurement=UNIT_GIGAHASH_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: data.get(ATTR_HASHRATE_1H),
    ),
    NerdQAxeSensorEntityDescription(
        key="hashrate_1d",
        icon="mdi:speedometer",
        native_unit_of_measurement=UNIT_GIGAHASH_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: data.get(ATTR_HASHRATE_1D),
    ),
    # Temperature
    NerdQAxeSensorEntityDescription(
        key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.get(ATTR_TEMP),
    ),
    NerdQAxeSensorEntityDescription(
        key="vr_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.get(ATTR_VR_TEMP),
    ),
    # Power
    NerdQAxeSensorEntityDescription(
        key="power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: data.get(ATTR_POWER),
    ),
    NerdQAxeSensorEntityDescription(
        key="voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: data.get(ATTR_VOLTAGE),
    ),
    NerdQAxeSensorEntityDescription(
        key="current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: data.get(ATTR_CURRENT),
    ),
    NerdQAxeSensorEntityDescription(
        key="core_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.get(ATTR_CORE_VOLTAGE),
    ),
    NerdQAxeSensorEntityDescription(
        key="core_voltage_actual",
        native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.get(ATTR_CORE_VOLTAGE_ACTUAL),
    ),
    # Fan
    NerdQAxeSensorEntityDescription(
        key="fan_speed",
        icon="mdi:fan",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(ATTR_FAN_SPEED),
    ),
    NerdQAxeSensorEntityDescription(
        key="fan_rpm",
        icon="mdi:fan",
        native_unit_of_measurement=UNIT_REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(ATTR_FAN_RPM),
    ),
    # Mining statistics
    NerdQAxeSensorEntityDescription(
        key="shares_accepted",
        icon="mdi:check-circle",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get(ATTR_SHARES_ACCEPTED),
    ),
    NerdQAxeSensorEntityDescription(
        key="shares_rejected",
        icon="mdi:close-circle",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get(ATTR_SHARES_REJECTED),
    ),
    NerdQAxeSensorEntityDescription(
        key="best_difficulty",
        icon="mdi:trophy",
        value_fn=lambda data: data.get(ATTR_BEST_DIFF),
    ),
    NerdQAxeSensorEntityDescription(
        key="best_session_difficulty",
        icon="mdi:trophy-outline",
        value_fn=lambda data: data.get(ATTR_BEST_SESSION_DIFF),
    ),
    NerdQAxeSensorEntityDescription(
        key="found_blocks",
        icon="mdi:cube",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get(ATTR_FOUND_BLOCKS),
    ),
    NerdQAxeSensorEntityDescription(
        key="total_found_blocks",
        icon="mdi:cube-outline",
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: data.get(ATTR_TOTAL_FOUND_BLOCKS),
    ),
    # Device information
    NerdQAxeSensorEntityDescription(
        key="device_model",
        icon="mdi:chip",
        value_fn=lambda data: data.get(ATTR_DEVICE_MODEL),
    ),
    NerdQAxeSensorEntityDescription(
        key="hostname",
        icon="mdi:server",
        value_fn=lambda data: data.get(ATTR_HOSTNAME),
    ),
    NerdQAxeSensorEntityDescription(
        key="wifi_rssi",
        icon="mdi:wifi",
        native_unit_of_measurement=UNIT_DECIBEL_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(ATTR_WIFI_RSSI),
    ),
    NerdQAxeSensorEntityDescription(
        key="frequency",
        icon="mdi:sine-wave",
        native_unit_of_measurement=UNIT_MEGAHERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get(ATTR_FREQUENCY),
    ),
    NerdQAxeSensorEntityDescription(
        key="version",
        icon="mdi:information-outline",
        value_fn=_clean_version,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NerdQAxeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NerdQAxe+ Miner sensors from a config entry.

    Creates all sensor entities including hashrate, temperature, power,
    fan, mining statistics, and device information sensors.

    Args:
        hass: Home Assistant instance
        entry: Config entry
        async_add_entities: Callback to add entities

    """
    coordinator = entry.runtime_data.coordinator

    entities: list[SensorEntity] = [
        NerdQAxeSensor(coordinator, description) for description in SENSORS
    ]
    entities.append(NerdQAxeUptimeSensor(coordinator))

    async_add_entities(entities)
    _LOGGER.info(
        "Successfully set up %d sensor entities for %s",
        len(entities),
        coordinator.host,
    )


class NerdQAxeSensor(CoordinatorEntity[NerdQAxeDataUpdateCoordinator], SensorEntity):
    """Representation of a NerdQAxe+ Miner sensor.

    Generic sensor entity driven by a :class:`NerdQAxeSensorEntityDescription`
    that reads its value from the coordinator data via ``value_fn``.
    """

    entity_description: NerdQAxeSensorEntityDescription

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NerdQAxeDataUpdateCoordinator,
        description: NerdQAxeSensorEntityDescription,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: Data update coordinator instance
            description: Sensor description (key, units, value_fn, ...)

        """
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_id_base}_{description.key}"
        self._attr_translation_key = description.key
        self._attr_device_info = coordinator.get_device_info()

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor.

        Returns:
            Sensor value, or None if unavailable

        """
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(self.coordinator.data)


class NerdQAxeUptimeSensor(
    CoordinatorEntity[NerdQAxeDataUpdateCoordinator], SensorEntity
):
    """Representation of NerdQAxe+ uptime sensor with formatted display.

    Displays miner uptime with localized time units based on Home Assistant
    language configuration. Supports 7 languages with appropriate abbreviations.
    """

    __slots__ = ()

    _attr_has_entity_name = True

    def __init__(self, coordinator: NerdQAxeDataUpdateCoordinator) -> None:
        """Initialize the uptime sensor.

        Args:
            coordinator: Data update coordinator instance

        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id_base}_uptime"
        self._attr_translation_key = "uptime"
        self._attr_icon = "mdi:clock-outline"
        self._attr_device_info = coordinator.get_device_info()

    def _get_time_units(self) -> dict[str, str]:
        """Get localized time unit abbreviations based on Home Assistant language.

        Returns:
            dict: Time unit abbreviations (day, hour, minute) for current language

        """
        language = self.hass.config.language if self.hass else "en"

        # Time unit abbreviations per language
        units = {
            "fr": {"day": "j", "hour": "h", "minute": "min"},
            "en": {"day": "d", "hour": "h", "minute": "min"},
            "de": {"day": "T", "hour": "Std", "minute": "Min"},
            "es": {"day": "d", "hour": "h", "minute": "min"},
            "it": {"day": "g", "hour": "h", "minute": "min"},
            "nl": {"day": "d", "hour": "u", "minute": "min"},
            "pt": {"day": "d", "hour": "h", "minute": "min"},
        }

        return units.get(language, units["en"])

    @property
    def native_value(self) -> str | None:
        """Return formatted uptime with localized time units.

        Converts uptime seconds to a human-readable format (e.g., "5d 12h 30min")
        using language-specific abbreviations.

        Returns:
            Formatted uptime string, or None if unavailable

        """
        if not self.coordinator.data:
            return None

        uptime_seconds = self.coordinator.data.get(ATTR_UPTIME)
        if uptime_seconds is None:
            return None

        # Convert seconds to days, hours, minutes
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60

        # Get localized time units
        units = self._get_time_units()

        # Format display based on duration
        if days > 0:
            return (
                f"{days}{units['day']} {hours}{units['hour']} "
                f"{minutes}{units['minute']}"
            )
        elif hours > 0:
            return f"{hours}{units['hour']} {minutes}{units['minute']}"
        else:
            return f"{minutes}{units['minute']}"
