"""Test the NerdQAxe+ Miner firmware update entity."""

from unittest.mock import MagicMock

import aiohttp
from multidict import CIMultiDict
import pytest
from yarl import URL

from custom_components.nerdqaxe.exceptions import NerdQAxeApiError, NerdQAxeError
from custom_components.nerdqaxe.update import (
    NerdQAxeUpdateEntity,
    normalize_device_model,
)

from .conftest import MOCK_ASIC_DATA, MOCK_HOST, MOCK_SYSTEM_INFO

_DOWNLOAD_URL = (
    "https://github.com/shufps/ESP-Miner-NerdQAxePlus/releases/download/"
    "v1.0.40/esp-miner-factory-NerdQAxe+-v1.0.40.bin"
)


def _client_response_error(status: int) -> aiohttp.ClientResponseError:
    """Build a realistic aiohttp.ClientResponseError for a given status."""
    request_info = aiohttp.RequestInfo(
        URL(f"http://{MOCK_HOST}/api/system/OTA/github"),
        "POST",
        CIMultiDict(),
        URL(f"http://{MOCK_HOST}/api/system/OTA/github"),
    )
    return aiohttp.ClientResponseError(request_info, (), status=status)


class _PostResponse:
    """Minimal async-aware stand-in for an aiohttp response."""

    def __init__(self, status: int, body: str = '{"status":"started"}') -> None:
        self.status = status
        self._body = body

    async def text(self) -> str:
        return self._body

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise _client_response_error(self.status)


class _PostCtx:
    """Async context manager returned by the mocked ``session.post``."""

    def __init__(
        self,
        response: _PostResponse | None = None,
        raise_on_enter: Exception | None = None,
    ) -> None:
        self._response = response
        self._raise_on_enter = raise_on_enter

    async def __aenter__(self) -> _PostResponse | None:
        if self._raise_on_enter is not None:
            raise self._raise_on_enter
        return self._response

    async def __aexit__(self, *exc: object) -> bool:
        return False


def _session_with_post(
    response: _PostResponse | None = None,
    raise_on_enter: Exception | None = None,
) -> MagicMock:
    session = MagicMock()
    session.post = MagicMock(return_value=_PostCtx(response, raise_on_enter))
    return session


def _make_update_entity(
    session: MagicMock, download_url: str | None = _DOWNLOAD_URL
) -> NerdQAxeUpdateEntity:
    coordinator = MagicMock()
    coordinator.host = MOCK_HOST
    coordinator.base_url = f"http://{MOCK_HOST}"
    coordinator.session = session
    coordinator.data = {**MOCK_SYSTEM_INFO, **MOCK_ASIC_DATA}
    entity = NerdQAxeUpdateEntity(coordinator)
    entity._download_url = download_url
    return entity


async def test_install_success_async_202() -> None:
    """A 202 'started' response from the async OTA endpoint succeeds."""
    entity = _make_update_entity(_session_with_post(_PostResponse(202)))
    await entity.async_install(None, False)


async def test_install_tolerates_reboot_disconnect() -> None:
    """A connection drop during flashing/reboot must NOT be a failed install."""
    session = _session_with_post(raise_on_enter=aiohttp.ServerDisconnectedError())
    entity = _make_update_entity(session)
    # Must not raise: the miner reboots and tears down the connection.
    await entity.async_install(None, False)


async def test_install_tolerates_timeout() -> None:
    """A timeout while the miner flashes must not be reported as a failure."""
    session = _session_with_post(raise_on_enter=TimeoutError())
    entity = _make_update_entity(session)
    await entity.async_install(None, False)


async def test_install_raises_when_busy_409() -> None:
    """A 409 'busy' response is surfaced as a real error."""
    session = _session_with_post(_PostResponse(409, '{"status":"busy"}'))
    entity = _make_update_entity(session)
    with pytest.raises(NerdQAxeError):
        await entity.async_install(None, False)


async def test_install_raises_on_http_error() -> None:
    """A 4xx rejection (bad/unsafe URL, auth) is a real error."""
    session = _session_with_post(_PostResponse(400, "bad request"))
    entity = _make_update_entity(session)
    with pytest.raises(NerdQAxeApiError):
        await entity.async_install(None, False)


async def test_install_raises_without_download_url() -> None:
    """No matching factory firmware -> explicit error instead of silent no-op."""
    entity = _make_update_entity(
        _session_with_post(_PostResponse(202)), download_url=None
    )
    with pytest.raises(NerdQAxeError):
        await entity.async_install(None, False)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("NerdQAxe+", "NerdQAxe+"),
        ("NerdQAxe++", "NerdQAxe++"),
        ("NerdOCTAXE-Gamma", "NerdOCTAXE-Gamma"),
        ("NerdAxe γ", "NerdAxeGamma"),  # noqa: RUF001 — greek gamma + space variant
    ],
)
def test_normalize_device_model(raw: str, expected: str) -> None:
    """Device model normalization resolves to the factory image name."""
    assert normalize_device_model(raw) == expected
