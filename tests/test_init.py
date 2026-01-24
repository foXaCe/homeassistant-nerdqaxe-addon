"""Test the NerdQAxe+ Miner integration initialization."""

from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
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


async def test_setup_entry_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test successful setup of config entry."""
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

    assert mock_config_entry.state == ConfigEntryState.LOADED
    assert mock_config_entry.runtime_data is not None
    assert mock_config_entry.runtime_data.coordinator is not None


async def test_setup_entry_connection_error(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test setup when connection fails."""
    import aiohttp

    mock_session = create_mock_session(
        raise_error=aiohttp.ClientConnectorError(None, OSError("Connection refused")),
    )

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Should go to retry state when connection fails
    assert mock_config_entry.state == ConfigEntryState.SETUP_RETRY


async def test_unload_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test unloading a config entry."""
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

        assert mock_config_entry.state == ConfigEntryState.LOADED

        result = await hass.config_entries.async_unload(mock_config_entry.entry_id)

    assert result is True
    assert mock_config_entry.state == ConfigEntryState.NOT_LOADED


async def test_reload_entry_on_options_update(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that entry reloads when options change."""
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

        assert mock_config_entry.state == ConfigEntryState.LOADED

        # Update options
        hass.config_entries.async_update_entry(
            mock_config_entry,
            options={"scan_interval": 60},
        )
        await hass.async_block_till_done()

    # Entry should still be loaded after reload
    assert mock_config_entry.state == ConfigEntryState.LOADED


async def test_migrate_entry_current_version(
    hass: HomeAssistant,
) -> None:
    """Test migration with current config entry version."""
    from custom_components.nerdqaxe import CONFIGENTRY_VERSION, async_migrate_entry

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NerdQAxe+ Miner",
        data={CONF_HOST: MOCK_HOST},
        unique_id="AA:BB:CC:DD:EE:FF",
        version=CONFIGENTRY_VERSION,
    )
    entry.add_to_hass(hass)

    # Current version should migrate successfully (no-op)
    result = await async_migrate_entry(hass, entry)
    assert result is True


async def test_migrate_entry_future_version(
    hass: HomeAssistant,
) -> None:
    """Test migration with future config entry version (downgrade)."""
    from custom_components.nerdqaxe import CONFIGENTRY_VERSION, async_migrate_entry

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NerdQAxe+ Miner",
        data={CONF_HOST: MOCK_HOST},
        unique_id="AA:BB:CC:DD:EE:FF",
        version=CONFIGENTRY_VERSION + 1,  # Future version
    )
    entry.add_to_hass(hass)

    # Downgrade should fail
    result = await async_migrate_entry(hass, entry)
    assert result is False
