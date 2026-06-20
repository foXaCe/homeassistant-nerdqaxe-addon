"""Test the NerdQAxe+ Miner config flow."""

from unittest.mock import patch

import aiohttp
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nerdqaxe.const import DOMAIN

from .conftest import MOCK_HOST, MOCK_SYSTEM_INFO, create_mock_session

DHCP_DISCOVERY = DhcpServiceInfo(
    ip=MOCK_HOST,
    hostname="nerdaxe_gamma",
    macaddress="f09e9e1ee0f4",
)


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


async def test_form_unknown_error(hass: HomeAssistant) -> None:
    """Test that unexpected (non-connection) errors surface as 'unknown'."""
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

    # Unexpected errors are differentiated from connection errors
    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "unknown"}


async def test_reconfigure_success(hass: HomeAssistant) -> None:
    """Test reconfiguring the host of an existing miner."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NerdQAxe+ Miner",
        data={CONF_HOST: MOCK_HOST},
        unique_id=MOCK_SYSTEM_INFO["macAddr"],
        version=2,
    )
    entry.add_to_hass(hass)

    result = await entry.start_reconfigure_flow(hass)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    mock_session = create_mock_session(status=200, json_data=MOCK_SYSTEM_INFO)
    with (
        patch(
            "custom_components.nerdqaxe.config_flow.async_get_clientsession",
            return_value=mock_session,
        ),
        patch("custom_components.nerdqaxe.async_setup_entry", return_value=True),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.200"},
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "reconfigure_successful"
    assert entry.data[CONF_HOST] == "192.168.1.200"


async def test_reconfigure_cannot_connect(hass: HomeAssistant) -> None:
    """Test reconfigure shows an error when the new host is unreachable."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NerdQAxe+ Miner",
        data={CONF_HOST: MOCK_HOST},
        unique_id=MOCK_SYSTEM_INFO["macAddr"],
        version=2,
    )
    entry.add_to_hass(hass)

    result = await entry.start_reconfigure_flow(hass)

    mock_session = create_mock_session(raise_error=aiohttp.ClientError())
    with patch(
        "custom_components.nerdqaxe.config_flow.async_get_clientsession",
        return_value=mock_session,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.200"},
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_reconfigure_unknown_error(hass: HomeAssistant) -> None:
    """Test reconfigure surfaces unexpected (non-connection) errors as 'unknown'."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NerdQAxe+ Miner",
        data={CONF_HOST: MOCK_HOST},
        unique_id=MOCK_SYSTEM_INFO["macAddr"],
        version=2,
    )
    entry.add_to_hass(hass)

    result = await entry.start_reconfigure_flow(hass)

    mock_session = create_mock_session(raise_error=Exception("Unknown error"))
    with patch(
        "custom_components.nerdqaxe.config_flow.async_get_clientsession",
        return_value=mock_session,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.200"},
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "unknown"}


async def test_reconfigure_different_device_aborts(hass: HomeAssistant) -> None:
    """Test reconfiguring toward an already-configured *different* miner aborts.

    Covers the branch where the validated MAC differs from the entry's
    unique id and that MAC already belongs to another config entry.
    """
    other_mac = "11:22:33:44:55:66"

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NerdQAxe+ Miner",
        data={CONF_HOST: MOCK_HOST},
        unique_id=MOCK_SYSTEM_INFO["macAddr"],
        version=2,
    )
    entry.add_to_hass(hass)

    # A second miner already configured with the MAC the reconfigure will report.
    other_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Other NerdQAxe+ Miner",
        data={CONF_HOST: "192.168.1.50"},
        unique_id=other_mac,
        version=2,
    )
    other_entry.add_to_hass(hass)

    result = await entry.start_reconfigure_flow(hass)

    mock_session = create_mock_session(
        status=200,
        json_data={**MOCK_SYSTEM_INFO, "macAddr": other_mac},
    )
    with patch(
        "custom_components.nerdqaxe.config_flow.async_get_clientsession",
        return_value=mock_session,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: "192.168.1.50"},
        )

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


async def test_dhcp_discovery_success(hass: HomeAssistant) -> None:
    """Test a miner discovered via DHCP can be set up after confirmation."""
    mock_session = create_mock_session(status=200, json_data=MOCK_SYSTEM_INFO)
    with patch(
        "custom_components.nerdqaxe.config_flow.async_get_clientsession",
        return_value=mock_session,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_DHCP},
            data=DHCP_DISCOVERY,
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "discovery_confirm"

        with patch(
            "custom_components.nerdqaxe.async_setup_entry",
            return_value=True,
        ):
            result2 = await hass.config_entries.flow.async_configure(
                result["flow_id"], {}
            )
            await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == MOCK_SYSTEM_INFO["hostname"]
    assert result2["data"] == {CONF_HOST: MOCK_HOST}
    assert result2["result"].unique_id == MOCK_SYSTEM_INFO["macAddr"]


async def test_dhcp_discovery_already_configured_updates_host(
    hass: HomeAssistant,
) -> None:
    """Test DHCP discovery of a known miner refreshes its stored host."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="NerdQAxe+ Miner",
        data={CONF_HOST: "192.168.1.99"},
        unique_id=MOCK_SYSTEM_INFO["macAddr"],
        version=2,
    )
    entry.add_to_hass(hass)

    mock_session = create_mock_session(status=200, json_data=MOCK_SYSTEM_INFO)
    with patch(
        "custom_components.nerdqaxe.config_flow.async_get_clientsession",
        return_value=mock_session,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_DHCP},
            data=DHCP_DISCOVERY,
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    # The stored host is refreshed to the freshly discovered IP.
    assert entry.data[CONF_HOST] == MOCK_HOST


async def test_dhcp_discovery_cannot_connect(hass: HomeAssistant) -> None:
    """Test DHCP discovery aborts when the miner cannot be reached."""
    mock_session = create_mock_session(raise_error=aiohttp.ClientError())
    with patch(
        "custom_components.nerdqaxe.config_flow.async_get_clientsession",
        return_value=mock_session,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_DHCP},
            data=DHCP_DISCOVERY,
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "cannot_connect"


async def test_dhcp_discovery_unknown_error(hass: HomeAssistant) -> None:
    """Test DHCP discovery aborts on an unexpected error."""
    mock_session = create_mock_session(raise_error=Exception("boom"))
    with patch(
        "custom_components.nerdqaxe.config_flow.async_get_clientsession",
        return_value=mock_session,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_DHCP},
            data=DHCP_DISCOVERY,
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "unknown"


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
