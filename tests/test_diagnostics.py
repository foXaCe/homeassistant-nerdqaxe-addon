"""Test the NerdQAxe+ Miner diagnostics."""

from unittest.mock import patch

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nerdqaxe.const import DOMAIN
from custom_components.nerdqaxe.diagnostics import async_get_config_entry_diagnostics

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


async def test_diagnostics(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test diagnostics output."""
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

        diagnostics = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    # Check structure
    assert "entry" in diagnostics
    assert "coordinator" in diagnostics
    assert "data" in diagnostics

    # Check that sensitive data is redacted
    assert diagnostics["entry"]["data"]["host"] == "**REDACTED**"

    # Check coordinator info
    assert "last_update_success" in diagnostics["coordinator"]
    assert "update_interval" in diagnostics["coordinator"]


async def test_diagnostics_redaction(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that sensitive data is properly redacted."""
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

        diagnostics = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    # Verify redacted fields in data
    if diagnostics["data"]:
        assert diagnostics["data"].get("macAddr") == "**REDACTED**"
        assert diagnostics["data"].get("hostname") == "**REDACTED**"
        assert diagnostics["data"].get("hostip") == "**REDACTED**"


async def test_diagnostics_no_data(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test diagnostics when coordinator has no data."""
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

        # Clear coordinator data to test null case
        mock_config_entry.runtime_data.coordinator.data = None

        diagnostics = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    # Should handle None data gracefully
    assert diagnostics["data"] is None


async def test_diagnostics_entry_info(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that entry info is included in diagnostics."""
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

        diagnostics = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    # Check entry info
    assert "entry_id" in diagnostics["entry"]
    assert "domain" in diagnostics["entry"]
    assert diagnostics["entry"]["domain"] == DOMAIN
