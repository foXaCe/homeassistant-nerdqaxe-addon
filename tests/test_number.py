"""Test the NerdQAxe+ Miner number entities."""

from unittest.mock import MagicMock, patch

import aiohttp
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nerdqaxe.const import DOMAIN
from custom_components.nerdqaxe.exceptions import NerdQAxeApiError

from .conftest import (
    MOCK_ASIC_DATA,
    MOCK_HOST,
    MOCK_SYSTEM_INFO,
    MockAiohttpContextManager,
    MockAiohttpResponse,
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


async def test_number_set_frequency_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test setting frequency successfully."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    # Setup PATCH mock for the settings endpoint
    patch_response = MockAiohttpResponse(status=200)
    patch_ctx = MockAiohttpContextManager(response=patch_response)
    mock_session.patch = MagicMock(return_value=patch_ctx)

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        # Find the frequency number entity
        number_entities = hass.states.async_entity_ids("number")
        freq_entity = [e for e in number_entities if "frequency" in e.lower()]

        assert len(freq_entity) > 0

        # Set new value
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": freq_entity[0], "value": 450},
            blocking=True,
        )

        # Verify PATCH /api/system was called (POST /api/system/asic returns 405)
        mock_session.patch.assert_called()
        assert mock_session.patch.call_args.args[0].endswith("/api/system")


async def test_number_set_frequency_failure(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test setting frequency failure handling."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    # Setup PATCH mock to raise error
    mock_session.patch = MagicMock(side_effect=aiohttp.ClientError("Connection failed"))

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        # Find the frequency number entity
        number_entities = hass.states.async_entity_ids("number")
        freq_entity = [e for e in number_entities if "frequency" in e.lower()]

        assert len(freq_entity) > 0

        # Set new value - should raise error
        with pytest.raises(NerdQAxeApiError):
            await hass.services.async_call(
                "number",
                "set_value",
                {"entity_id": freq_entity[0], "value": 450},
                blocking=True,
            )


async def test_number_set_core_voltage_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test setting core voltage successfully."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    # Setup PATCH mock for the settings endpoint
    patch_response = MockAiohttpResponse(status=200)
    patch_ctx = MockAiohttpContextManager(response=patch_response)
    mock_session.patch = MagicMock(return_value=patch_ctx)

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        # Find the voltage number entity
        number_entities = hass.states.async_entity_ids("number")
        voltage_entity = [e for e in number_entities if "voltage" in e.lower()]

        assert len(voltage_entity) > 0

        # Set new value
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": voltage_entity[0], "value": 1150},
            blocking=True,
        )

        # Verify PATCH /api/system was called (POST /api/system/asic returns 405)
        mock_session.patch.assert_called()
        assert mock_session.patch.call_args.args[0].endswith("/api/system")


async def test_number_set_core_voltage_failure(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test setting core voltage failure handling."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    # Setup PATCH mock to raise error
    mock_session.patch = MagicMock(side_effect=aiohttp.ClientError("Connection failed"))

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        # Find the voltage number entity
        number_entities = hass.states.async_entity_ids("number")
        voltage_entity = [e for e in number_entities if "voltage" in e.lower()]

        assert len(voltage_entity) > 0

        # Set new value - should raise error
        with pytest.raises(NerdQAxeApiError):
            await hass.services.async_call(
                "number",
                "set_value",
                {"entity_id": voltage_entity[0], "value": 1150},
                blocking=True,
            )


async def test_number_native_value_no_data(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test number native_value when coordinator has no data."""
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

        # Clear data to test None case
        coordinator.data = None

        # Trigger entity state update
        coordinator.async_set_updated_data(None)
        await hass.async_block_till_done()

        # Entities should handle None gracefully
        number_entities = hass.states.async_entity_ids("number")
        assert len(number_entities) > 0
