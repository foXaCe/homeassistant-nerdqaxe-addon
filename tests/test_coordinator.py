"""Test the NerdQAxe+ Miner coordinator."""

from unittest.mock import patch

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
import pytest

from custom_components.nerdqaxe import NerdQAxeDataUpdateCoordinator
from custom_components.nerdqaxe.const import DOMAIN

from .conftest import (
    MOCK_ASIC_DATA,
    MOCK_HOST,
    MOCK_SYSTEM_INFO,
    create_mock_session,
)


@pytest.fixture
def mock_coordinator(hass: HomeAssistant) -> NerdQAxeDataUpdateCoordinator:
    """Create a mock coordinator."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )

    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        coordinator = NerdQAxeDataUpdateCoordinator(
            hass,
            host=MOCK_HOST,
            scan_interval=30,
        )
        # Manually set session since patch is context-limited
        coordinator.session = mock_session
        return coordinator


async def test_coordinator_update_success(
    hass: HomeAssistant, mock_coordinator: NerdQAxeDataUpdateCoordinator
) -> None:
    """Test successful coordinator update."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )
    mock_coordinator.session = mock_session

    data = await mock_coordinator._async_update_data()

    assert data is not None
    assert data["hostname"] == MOCK_SYSTEM_INFO["hostname"]
    assert data["hashRate"] == MOCK_ASIC_DATA["hashRate"]


async def test_coordinator_update_connection_error(
    hass: HomeAssistant, mock_coordinator: NerdQAxeDataUpdateCoordinator
) -> None:
    """Test coordinator update with connection error."""
    mock_session = create_mock_session(
        raise_error=aiohttp.ClientConnectorError(None, OSError("Connection refused")),
    )
    mock_coordinator.session = mock_session

    with pytest.raises(UpdateFailed) as exc_info:
        await mock_coordinator._async_update_data()

    assert "Cannot connect to miner" in str(exc_info.value)


async def test_coordinator_update_timeout(
    hass: HomeAssistant, mock_coordinator: NerdQAxeDataUpdateCoordinator
) -> None:
    """Test coordinator update with timeout."""
    mock_session = create_mock_session(
        raise_error=TimeoutError(),
    )
    mock_coordinator.session = mock_session

    with pytest.raises(UpdateFailed) as exc_info:
        await mock_coordinator._async_update_data()

    assert "Cannot connect to miner" in str(exc_info.value)


async def test_coordinator_update_server_timeout(
    hass: HomeAssistant, mock_coordinator: NerdQAxeDataUpdateCoordinator
) -> None:
    """Test coordinator update with server timeout."""
    mock_session = create_mock_session(
        raise_error=aiohttp.ServerTimeoutError("Timeout"),
        raise_on_enter=True,  # ServerTimeoutError happens during request
    )
    mock_coordinator.session = mock_session

    with pytest.raises(UpdateFailed) as exc_info:
        await mock_coordinator._async_update_data()

    assert "Timeout connecting to miner" in str(exc_info.value)


async def test_coordinator_update_client_error(
    hass: HomeAssistant, mock_coordinator: NerdQAxeDataUpdateCoordinator
) -> None:
    """Test coordinator update with client error."""
    mock_session = create_mock_session(
        raise_error=aiohttp.ClientResponseError(None, (), status=500),
        raise_on_enter=True,  # ClientResponseError happens during request
    )
    mock_coordinator.session = mock_session

    with pytest.raises(UpdateFailed) as exc_info:
        await mock_coordinator._async_update_data()

    assert "Error communicating with miner API" in str(exc_info.value)


async def test_coordinator_update_unexpected_error(
    hass: HomeAssistant, mock_coordinator: NerdQAxeDataUpdateCoordinator
) -> None:
    """Test coordinator update with unexpected error."""
    mock_session = create_mock_session(
        raise_error=ValueError("Unexpected error"),
    )
    mock_coordinator.session = mock_session

    with pytest.raises(UpdateFailed) as exc_info:
        await mock_coordinator._async_update_data()

    assert "Unexpected error" in str(exc_info.value)


async def test_coordinator_get_device_info(
    hass: HomeAssistant, mock_coordinator: NerdQAxeDataUpdateCoordinator
) -> None:
    """Test coordinator device info."""
    mock_coordinator.data = {**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA}

    device_info = mock_coordinator.get_device_info()

    assert device_info["name"] == f"NerdQAxe+ Miner ({MOCK_HOST})"
    assert device_info["manufacturer"] == "NerdQAxe"
    assert device_info["model"] == MOCK_SYSTEM_INFO["deviceModel"]
    assert (DOMAIN, MOCK_HOST) in device_info["identifiers"]


async def test_coordinator_get_device_info_no_data(
    hass: HomeAssistant, mock_coordinator: NerdQAxeDataUpdateCoordinator
) -> None:
    """Test coordinator device info with no data."""
    mock_coordinator.data = None

    device_info = mock_coordinator.get_device_info()

    assert device_info["model"] == "Unknown"


async def test_coordinator_get_device_info_missing_model(
    hass: HomeAssistant, mock_coordinator: NerdQAxeDataUpdateCoordinator
) -> None:
    """Test coordinator device info with missing model field."""
    mock_coordinator.data = {"hostname": "test"}

    device_info = mock_coordinator.get_device_info()

    # Should use "Unknown" when deviceModel is not in data
    assert device_info["model"] == "Unknown"
