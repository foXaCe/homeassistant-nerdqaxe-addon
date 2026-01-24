"""Test the NerdQAxe+ Miner sensor entities."""

from unittest.mock import patch

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
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
