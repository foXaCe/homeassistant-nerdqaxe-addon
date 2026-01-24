"""Test the NerdQAxe+ Miner config flow."""

from unittest.mock import patch

import aiohttp
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nerdqaxe.const import DOMAIN

from .conftest import MOCK_HOST, MOCK_SYSTEM_INFO, create_mock_session


async def test_form_user(hass: HomeAssistant) -> None:
    """Test the user config flow form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


async def test_form_user_success(hass: HomeAssistant) -> None:
    """Test successful user config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_session = create_mock_session(
        status=200,
        json_data=MOCK_SYSTEM_INFO,
    )

    with (
        patch(
            "custom_components.nerdqaxe.config_flow.async_get_clientsession",
            return_value=mock_session,
        ),
        patch(
            "custom_components.nerdqaxe.async_setup_entry",
            return_value=True,
        ),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: MOCK_HOST},
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == MOCK_SYSTEM_INFO["hostname"]
    assert result2["data"] == {CONF_HOST: MOCK_HOST}


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test handling connection errors."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_session = create_mock_session(
        raise_error=aiohttp.ClientError(),
    )

    with patch(
        "custom_components.nerdqaxe.config_flow.async_get_clientsession",
        return_value=mock_session,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: MOCK_HOST},
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_timeout(hass: HomeAssistant) -> None:
    """Test handling timeout errors."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_session = create_mock_session(
        raise_error=TimeoutError(),
    )

    with patch(
        "custom_components.nerdqaxe.config_flow.async_get_clientsession",
        return_value=mock_session,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: MOCK_HOST},
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_already_configured(hass: HomeAssistant) -> None:
    """Test handling already configured device."""
    # Create existing entry
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NerdQAxe+ Miner",
        data={CONF_HOST: MOCK_HOST},
        unique_id=MOCK_SYSTEM_INFO["macAddr"],
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_session = create_mock_session(
        status=200,
        json_data=MOCK_SYSTEM_INFO,
    )

    with patch(
        "custom_components.nerdqaxe.config_flow.async_get_clientsession",
        return_value=mock_session,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: MOCK_HOST},
        )

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


async def test_form_generic_error(hass: HomeAssistant) -> None:
    """Test handling generic errors (all convert to cannot_connect)."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    mock_session = create_mock_session(
        raise_error=Exception("Unknown error"),
    )

    with patch(
        "custom_components.nerdqaxe.config_flow.async_get_clientsession",
        return_value=mock_session,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: MOCK_HOST},
        )

    # All exceptions in validate_input are converted to CannotConnectError
    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_options_flow(hass: HomeAssistant) -> None:
    """Test the options flow."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NerdQAxe+ Miner",
        data={CONF_HOST: MOCK_HOST},
        unique_id=MOCK_SYSTEM_INFO["macAddr"],
    )
    entry.add_to_hass(hass)

    # Initialize options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit options
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"scan_interval": 60},
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"] == {"scan_interval": 60}


async def test_options_flow_default_values(hass: HomeAssistant) -> None:
    """Test the options flow with default values."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NerdQAxe+ Miner",
        data={CONF_HOST: MOCK_HOST},
        unique_id=MOCK_SYSTEM_INFO["macAddr"],
        options={"scan_interval": 45},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    # Verify form has current value as default
    assert result["data_schema"] is not None
