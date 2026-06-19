"""Test the NerdQAxe+ Miner binary sensor entities."""

from unittest.mock import MagicMock, patch

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nerdqaxe.binary_sensor import NerdQAxeStratumSensor
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


def _make_sensor(data: dict | None) -> NerdQAxeStratumSensor:
    """Build a stratum binary sensor backed by a mock coordinator."""
    coordinator = MagicMock()
    coordinator.host = MOCK_HOST
    coordinator.data = data
    coordinator.get_device_info.return_value = {"identifiers": {(DOMAIN, MOCK_HOST)}}
    return NerdQAxeStratumSensor(coordinator)


def test_is_on_with_connected_pool() -> None:
    """Modern firmware: any connected pool in stratum.pools marks it on."""
    sensor = _make_sensor(
        {"stratum": {"pools": [{"connected": True}]}},
    )
    assert sensor.is_on is True


def test_is_on_with_multiple_pools_one_connected() -> None:
    """Dual-pool: connected if at least one pool reports connected."""
    sensor = _make_sensor(
        {"stratum": {"pools": [{"connected": False}, {"connected": True}]}},
    )
    assert sensor.is_on is True


def test_is_off_with_all_pools_disconnected() -> None:
    """All pools disconnected means the sensor is off."""
    sensor = _make_sensor(
        {"stratum": {"pools": [{"connected": False}, {"connected": False}]}},
    )
    assert sensor.is_on is False


def test_is_off_with_empty_pools() -> None:
    """An empty pools array (no flat field) means off."""
    sensor = _make_sensor({"stratum": {"pools": []}})
    assert sensor.is_on is False


def test_is_on_legacy_flat_field() -> None:
    """Legacy firmware without stratum.pools falls back to the flat field."""
    sensor = _make_sensor({"isStratumConnected": True})
    assert sensor.is_on is True


def test_is_off_legacy_flat_field() -> None:
    """Legacy flat field set to False reports off."""
    sensor = _make_sensor({"isStratumConnected": False})
    assert sensor.is_on is False


def test_is_off_without_data() -> None:
    """No coordinator data means off rather than an error."""
    sensor = _make_sensor(None)
    assert sensor.is_on is False


async def test_binary_sensor_state_connected(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Full setup: the stratum binary sensor reflects the connected pool."""
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

    state = hass.states.get(f"binary_sensor.{MOCK_HOST}_stratum_connected")
    if state is None:
        # entity_id is slugified from the host; locate it dynamically
        ids = hass.states.async_entity_ids("binary_sensor")
        nerdqaxe = [e for e in ids if "stratum" in e]
        assert nerdqaxe, "stratum binary sensor was not created"
        state = hass.states.get(nerdqaxe[0])

    assert state is not None
    assert state.state == "on"
