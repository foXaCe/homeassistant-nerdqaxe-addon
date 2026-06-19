"""Fixtures for NerdQAxe+ Miner tests."""

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

from homeassistant.const import CONF_HOST
import pytest

# Test data
MOCK_HOST = "192.168.1.100"

MOCK_SYSTEM_INFO = {
    "deviceModel": "NerdQAxe+ Miner",
    "hostname": "nerdqaxe-miner",
    "macAddr": "AA:BB:CC:DD:EE:FF",
    "hostip": MOCK_HOST,
    "wifiRSSI": -55,
    "version": "2.0.0",
    "uptimeSeconds": 86400,
}

MOCK_ASIC_DATA = {
    "hashRate": 500000000000,
    "hashRate_1m": 495000000000,
    "hashRate_10m": 498000000000,
    "hashRate_1h": 499000000000,
    "hashRate_1d": 500000000000,
    "temp": 45.5,
    "vrTemp": 50.2,
    "power": 15.0,
    "voltage": 5.0,
    "current": 3.0,
    "fanspeed": 80,
    "fanrpm": 3500,
    "sharesAccepted": 1000,
    "sharesRejected": 5,
    "bestDiff": "1.5M",
    "bestSessionDiff": "500K",
    # Modern firmware exposes pool connection state inside stratum.pools[]
    "stratum": {
        "poolMode": 0,
        "activePoolMode": 0,
        "pools": [
            {
                "connected": True,
                "poolDifficulty": 10000,
                "accepted": 1000,
                "rejected": 5,
            }
        ],
    },
    "foundBlocks": 0,
    "totalFoundBlocks": 0,
    "coreVoltage": 1200,
    "coreVoltageActual": 1180,
    "frequency": 500,
}


class MockAiohttpResponse:
    """Mock aiohttp response that works with async context manager."""

    def __init__(
        self,
        status: int = 200,
        json_data: dict[str, Any] | None = None,
        raise_error: Exception | None = None,
    ) -> None:
        """Initialize mock response."""
        self.status = status
        self._json_data = json_data or {}
        self._raise_error = raise_error

    async def json(self) -> dict[str, Any]:
        """Return mock JSON data."""
        return self._json_data

    def raise_for_status(self) -> None:
        """Raise if error configured."""
        if self._raise_error:
            raise self._raise_error


class MockAiohttpContextManager:
    """Mock async context manager for aiohttp session.get()."""

    def __init__(
        self,
        response: MockAiohttpResponse | None = None,
        raise_on_enter: Exception | None = None,
    ) -> None:
        """Initialize the mock context manager."""
        self._response = response or MockAiohttpResponse()
        self._raise_on_enter = raise_on_enter

    async def __aenter__(self) -> MockAiohttpResponse:
        """Enter context and return response."""
        if self._raise_on_enter:
            raise self._raise_on_enter
        return self._response

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context."""
        pass


def create_mock_session(
    status: int = 200,
    json_data: dict[str, Any] | None = None,
    raise_error: Exception | None = None,
    raise_on_enter: bool = False,
) -> MagicMock:
    """Create a properly configured mock aiohttp session.

    Args:
        status: HTTP status code to return
        json_data: JSON data to return from response
        raise_error: Exception to raise
        raise_on_enter: If True, raise during __aenter__ (for ServerTimeoutError etc)
                       If False, raise on get() call (for ClientConnectorError etc)

    Returns:
        MagicMock: Configured mock session

    """
    mock_session = MagicMock()

    if raise_error:
        if raise_on_enter:
            # Raise during async with (e.g., ServerTimeoutError, ClientResponseError)
            ctx_manager = MockAiohttpContextManager(raise_on_enter=raise_error)
            mock_session.get = MagicMock(return_value=ctx_manager)
        else:
            # Raise on get() call (e.g., ClientConnectorError, TimeoutError)
            mock_session.get = MagicMock(side_effect=raise_error)
    else:
        response = MockAiohttpResponse(status=status, json_data=json_data)
        ctx_manager = MockAiohttpContextManager(response=response)
        mock_session.get = MagicMock(return_value=ctx_manager)

    return mock_session


@pytest.fixture
def mock_config_entry_data() -> dict:
    """Return mock config entry data."""
    return {
        CONF_HOST: MOCK_HOST,
    }


@pytest.fixture
def mock_api_response() -> dict:
    """Return combined mock API response."""
    return {
        **MOCK_SYSTEM_INFO,
        **MOCK_ASIC_DATA,
    }


@pytest.fixture
def mock_aiohttp_session() -> Generator[MagicMock, None, None]:
    """Provide a mock aiohttp session with proper async context manager support."""
    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA},
    )
    with patch(
        "custom_components.nerdqaxe.coordinator.async_get_clientsession",
        return_value=mock_session,
    ):
        yield mock_session


@pytest.fixture
def mock_config_flow_session() -> Generator[MagicMock, None, None]:
    """Provide a mock session for config flow tests."""
    mock_session = create_mock_session(
        status=200,
        json_data=MOCK_SYSTEM_INFO,
    )
    with patch(
        "custom_components.nerdqaxe.config_flow.async_get_clientsession",
        return_value=mock_session,
    ):
        yield mock_session


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable custom integrations for all tests."""
    return
