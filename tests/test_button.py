"""Test the NerdQAxe+ Miner button entities."""

from unittest.mock import MagicMock, patch

import aiohttp
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nerdqaxe.const import DOMAIN

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


async def test_button_press_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test successful button press."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    # Setup POST mock for restart endpoint
    post_response = MockAiohttpResponse(status=200)
    post_ctx = MockAiohttpContextManager(response=post_response)
    mock_session.post = MagicMock(return_value=post_ctx)

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        # Find the restart button
        button_entities = hass.states.async_entity_ids("button")
        restart_button = [e for e in button_entities if "restart" in e.lower()]

        assert len(restart_button) > 0

        # Press the button
        await hass.services.async_call(
            "button",
            "press",
            {"entity_id": restart_button[0]},
            blocking=True,
        )

        # Verify POST was called
        mock_session.post.assert_called_once()


async def test_button_press_failure(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test button press failure handling."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    # Setup POST mock to raise error
    mock_session.post = MagicMock(side_effect=aiohttp.ClientError("Connection failed"))

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        # Find the restart button
        button_entities = hass.states.async_entity_ids("button")
        restart_button = [e for e in button_entities if "restart" in e.lower()]

        assert len(restart_button) > 0

        # Press the button - should raise error
        with pytest.raises(aiohttp.ClientError):
            await hass.services.async_call(
                "button",
                "press",
                {"entity_id": restart_button[0]},
                blocking=True,
            )
