"""Test the NerdQAxe+ Miner sensor entities."""

from unittest.mock import MagicMock, patch

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nerdqaxe.const import DOMAIN
from custom_components.nerdqaxe.sensor import SENSORS, NerdQAxeSensor

from .conftest import (
    MOCK_ASIC_DATA,
    MOCK_HOST,
    MOCK_SYSTEM_INFO,
    create_mock_session,
)


@pytest.fixture
def mock_config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Create a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NerdQAxe+ Miner",
        data={CONF_HOST: MOCK_HOST},
        unique_id="AA:BB:CC:DD:EE:FF",
    )
    entry.add_to_hass(hass)
    return entry


async def test_sensor_entities_created(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that sensor entities are created."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Get all sensor entities for this domain
    entity_registry = hass.states.async_entity_ids("sensor")
    nerdqaxe_sensors = [e for e in entity_registry if "nerdqaxe" in e or MOCK_HOST in e]

    # Should have created sensor entities
    assert len(nerdqaxe_sensors) > 0


async def test_sensor_state_values(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test sensor state values are correct."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Verify coordinator has data
    coordinator = mock_config_entry.runtime_data.coordinator
    assert coordinator.data is not None
    assert coordinator.data.get("hashRate") == MOCK_ASIC_DATA["hashRate"]
    assert coordinator.data.get("temp") == MOCK_ASIC_DATA["temp"]


async def test_core_voltage_actual_sensor(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the Core Voltage Actual sensor reports the measured voltage."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    coordinator = mock_config_entry.runtime_data.coordinator
    assert coordinator.data.get("coreVoltageActual") == 1180

    # The dedicated sensor entity is created and exposes the measured value
    ids = hass.states.async_entity_ids("sensor")
    actual = [e for e in ids if "core_voltage_actual" in e]
    assert actual, "core_voltage_actual sensor was not created"
    assert hass.states.get(actual[0]).state == "1180"


async def test_binary_sensor_entities_created(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that binary sensor entities are created."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Get all binary_sensor entities
    entity_registry = hass.states.async_entity_ids("binary_sensor")
    nerdqaxe_binary = [e for e in entity_registry if "nerdqaxe" in e or MOCK_HOST in e]

    # Should have created binary sensor entities (at least stratum connected)
    assert len(nerdqaxe_binary) > 0


async def test_button_entities_created(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that button entities are created."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Get all button entities
    entity_registry = hass.states.async_entity_ids("button")
    nerdqaxe_buttons = [e for e in entity_registry if "nerdqaxe" in e or MOCK_HOST in e]

    # Should have created button entities
    assert len(nerdqaxe_buttons) > 0


async def test_number_entities_created(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that number entities are created."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Get all number entities
    entity_registry = hass.states.async_entity_ids("number")
    nerdqaxe_numbers = [e for e in entity_registry if "nerdqaxe" in e or MOCK_HOST in e]

    # Should have created number entities
    assert len(nerdqaxe_numbers) > 0


async def test_update_entities_created(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that update entities are created."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Get all update entities
    entity_registry = hass.states.async_entity_ids("update")
    nerdqaxe_updates = [e for e in entity_registry if "nerdqaxe" in e or MOCK_HOST in e]

    # Should have created update entities
    assert len(nerdqaxe_updates) > 0


async def test_coordinator_data_propagation(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that coordinator data is properly propagated to entities."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    coordinator = mock_config_entry.runtime_data.coordinator

    # Verify all expected data keys are present
    expected_keys = ["hostname", "hashRate", "temp", "power", "fanspeed"]
    for key in expected_keys:
        assert key in coordinator.data, f"Missing key: {key}"


async def test_second_fan_sensors_created_on_dual_fan(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Dual-fan boards (e.g. NerdQAxe++) expose fan_speed_2 / fan_rpm_2."""
    dual_fan = {
        **MOCK_SYSTEM_INFO,
        **MOCK_ASIC_DATA,
        "fanCount": 2,
        "fanspeed2": 100,
        "fanrpm2": 2474,
    }
    mock_session = create_mock_session(status=200, json_data=dual_fan)
    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    ent_reg = er.async_get(hass)
    entries = er.async_entries_for_config_entry(ent_reg, mock_config_entry.entry_id)

    rpm2 = next((e for e in entries if e.unique_id.endswith("_fan_rpm_2")), None)
    speed2 = next((e for e in entries if e.unique_id.endswith("_fan_speed_2")), None)
    assert rpm2 is not None, "fan_rpm_2 sensor not created"
    assert speed2 is not None, "fan_speed_2 sensor not created"
    assert hass.states.get(rpm2.entity_id).state == "2474"
    assert hass.states.get(speed2.entity_id).state == "100"


async def test_second_fan_sensors_absent_on_single_fan(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Single-fan boards do not expose the second-fan sensors.

    Real single-fan firmware still sends ``fanspeed2``/``fanrpm2`` as ``0`` with
    ``fanCount: 1``, so presence of those keys must not create phantom sensors.
    """
    single_fan = {
        **MOCK_SYSTEM_INFO,
        **MOCK_ASIC_DATA,
        "fanCount": 1,
        "fanspeed2": 0,
        "fanrpm2": 0,
    }
    mock_session = create_mock_session(status=200, json_data=single_fan)
    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    ent_reg = er.async_get(hass)
    entries = er.async_entries_for_config_entry(ent_reg, mock_config_entry.entry_id)
    assert not any(
        e.unique_id.endswith(("_fan_rpm_2", "_fan_speed_2")) for e in entries
    )


async def test_per_asic_temp_sensors_created(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Multi-ASIC boards (e.g. NerdQX) expose one temperature sensor per chip."""
    multi_asic = {
        **MOCK_SYSTEM_INFO,
        **MOCK_ASIC_DATA,
        "asicCount": 3,
        "asicTemps": [58.5, 60, 59],
    }
    mock_session = create_mock_session(status=200, json_data=multi_asic)
    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    ent_reg = er.async_get(hass)
    entries = er.async_entries_for_config_entry(ent_reg, mock_config_entry.entry_id)
    asic_temps = [e for e in entries if "_asic_temp_" in e.unique_id]
    assert len(asic_temps) == 3

    first = next(e for e in entries if e.unique_id.endswith("_asic_temp_0"))
    assert float(hass.states.get(first.entity_id).state) == 58.5


async def test_per_asic_temp_sensors_absent_when_zero(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Boards reporting asicTemps as all-zero get no per-ASIC sensors."""
    single = {
        **MOCK_SYSTEM_INFO,
        **MOCK_ASIC_DATA,
        "asicCount": 1,
        "asicTemps": [0],
    }
    mock_session = create_mock_session(status=200, json_data=single)
    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    ent_reg = er.async_get(hass)
    entries = er.async_entries_for_config_entry(ent_reg, mock_config_entry.entry_id)
    assert not any("_asic_temp_" in e.unique_id for e in entries)


def _make_sensor(key: str, data: dict | None) -> NerdQAxeSensor:
    """Build a sensor backed by a mock coordinator."""
    coordinator = MagicMock()
    coordinator.host = MOCK_HOST
    coordinator.data = data
    coordinator.get_device_info.return_value = {"identifiers": {(DOMAIN, MOCK_HOST)}}
    description = next(d for d in SENSORS if d.key == key)
    return NerdQAxeSensor(coordinator, description)


def test_extra_attributes_without_data() -> None:
    """A sensor with attributes reports none while the miner is unreachable."""
    assert _make_sensor("pool_url", None).extra_state_attributes is None


def test_extra_attributes_absent_on_plain_sensors() -> None:
    """Sensors that declare no attributes_fn expose no extra attributes."""
    sensor = _make_sensor("hashrate", {**MOCK_ASIC_DATA})
    assert sensor.extra_state_attributes is None


async def test_pool_sensors_report_active_pool(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """The pool sensors report the endpoint of the pool being mined."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )
    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    ent_reg = er.async_get(hass)
    entries = er.async_entries_for_config_entry(ent_reg, mock_config_entry.entry_id)

    url = next(e for e in entries if e.unique_id.endswith("_pool_url"))
    port = next(e for e in entries if e.unique_id.endswith("_pool_port"))
    assert hass.states.get(url.entity_id).state == "public-pool.io"
    assert hass.states.get(port.entity_id).state == "21496"

    # Failover mode: no second pool is being mined, so no secondary attribute.
    attributes = hass.states.get(url.entity_id).attributes
    assert attributes["pool_mode"] == "failover"
    assert "secondary_url" not in attributes


async def test_pool_user_sensor_disabled_by_default(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """The pool user embeds the payout address and stays opt-in."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )
    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    ent_reg = er.async_get(hass)
    entries = er.async_entries_for_config_entry(ent_reg, mock_config_entry.entry_id)

    user = next(e for e in entries if e.unique_id.endswith("_pool_user"))
    assert user.disabled_by is er.RegistryEntryDisabler.INTEGRATION
    assert hass.states.get(user.entity_id) is None


async def test_pool_sensors_follow_failover(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """After a failover the sensors report the fallback endpoint."""
    failed_over = {
        **MOCK_SYSTEM_INFO,
        **MOCK_ASIC_DATA,
        "stratum": {
            "activePoolMode": 0,
            "usingFallback": True,
            "pools": [
                {"active": False, "connected": False},
                {"active": True, "connected": True},
            ],
        },
    }
    mock_session = create_mock_session(status=200, json_data=failed_over)
    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    ent_reg = er.async_get(hass)
    entries = er.async_entries_for_config_entry(ent_reg, mock_config_entry.entry_id)

    url = next(e for e in entries if e.unique_id.endswith("_pool_url"))
    port = next(e for e in entries if e.unique_id.endswith("_pool_port"))
    assert hass.states.get(url.entity_id).state == "solo.ckpool.org"
    assert hass.states.get(port.entity_id).state == "3333"


async def test_pool_url_exposes_second_pool_in_dual_mode(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Dual-pool mode mines both pools; the second one is an attribute."""
    dual = {
        **MOCK_SYSTEM_INFO,
        **MOCK_ASIC_DATA,
        "stratum": {
            "activePoolMode": 1,
            "pools": [
                {"active": True, "connected": True},
                {"active": True, "connected": True},
            ],
        },
    }
    mock_session = create_mock_session(status=200, json_data=dual)
    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    ent_reg = er.async_get(hass)
    entries = er.async_entries_for_config_entry(ent_reg, mock_config_entry.entry_id)

    url = next(e for e in entries if e.unique_id.endswith("_pool_url"))
    state = hass.states.get(url.entity_id)
    assert state.state == "public-pool.io"
    assert state.attributes["pool_mode"] == "dual"
    assert state.attributes["secondary_url"] == "solo.ckpool.org"
    assert state.attributes["secondary_port"] == 3333
