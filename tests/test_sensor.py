"""Test the NerdQAxe+ Miner sensor entities."""

from unittest.mock import patch

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nerdqaxe.const import DOMAIN

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
