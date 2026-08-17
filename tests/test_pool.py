"""Test the NerdQAxe+ Miner mining pool resolution helpers."""

from typing import Any

import pytest

from custom_components.nerdqaxe.const import (
    ATTR_FALLBACK_STRATUM_URL,
    ATTR_STRATUM_URL,
    POOL_INDEX_FALLBACK,
    POOL_INDEX_PRIMARY,
)
from custom_components.nerdqaxe.pool import (
    active_pool_field,
    active_pool_index,
    clean_value,
    is_using_fallback,
    pool_mode_name,
)

ENDPOINTS: dict[str, Any] = {
    "stratumURL": "public-pool.io",
    "stratumPort": 21496,
    "stratumUser": "bc1qprimary.nerdqaxe",
    "fallbackStratumURL": "solo.ckpool.org",
    "fallbackStratumPort": 3333,
    "fallbackStratumUser": "bc1qfallback.nerdqaxe",
}


def _failover(active_index: int, **stratum: Any) -> dict[str, Any]:
    """Build a failover-mode payload with the given pool marked active."""
    return {
        **ENDPOINTS,
        "stratum": {
            "activePoolMode": 0,
            "pools": [
                {"active": index == active_index, "connected": True} for index in (0, 1)
            ],
            **stratum,
        },
    }


def test_active_index_primary() -> None:
    """The pool flagged active designates the endpoint to report."""
    assert active_pool_index(_failover(POOL_INDEX_PRIMARY)) == POOL_INDEX_PRIMARY


def test_active_index_fallback() -> None:
    """A failover switches the reported endpoint to the fallback pool."""
    assert active_pool_index(_failover(POOL_INDEX_FALLBACK)) == POOL_INDEX_FALLBACK


def test_active_index_dual_mode_reports_primary() -> None:
    """Dual-pool mode flags both pools active; the primary is reported."""
    data = {
        **ENDPOINTS,
        "stratum": {
            "activePoolMode": 1,
            "pools": [
                {"active": True, "connected": True},
                {"active": True, "connected": True},
            ],
        },
    }
    assert active_pool_index(data) == POOL_INDEX_PRIMARY
    assert active_pool_field(data, ATTR_STRATUM_URL, ATTR_FALLBACK_STRATUM_URL) == (
        "public-pool.io"
    )


def test_active_index_without_active_flag_uses_fallback_signal() -> None:
    """Firmware not sending ``active`` is resolved via ``usingFallback``."""
    data = {
        **ENDPOINTS,
        "stratum": {"pools": [{"connected": True}], "usingFallback": True},
    }
    assert active_pool_index(data) == POOL_INDEX_FALLBACK


def test_active_index_legacy_flat_payload() -> None:
    """Legacy firmware exposes neither pools[] nor a nested stratum object."""
    data = {**ENDPOINTS, "isUsingFallbackStratum": True}
    assert active_pool_index(data) == POOL_INDEX_FALLBACK
    assert active_pool_field(data, ATTR_STRATUM_URL, ATTR_FALLBACK_STRATUM_URL) == (
        "solo.ckpool.org"
    )


def test_active_index_beyond_fallback_clamps() -> None:
    """More than two pools still resolve onto the two flat endpoint sets."""
    data = {
        **ENDPOINTS,
        "stratum": {
            "pools": [
                {"active": False},
                {"active": False},
                {"active": True},
            ]
        },
    }
    assert active_pool_index(data) == POOL_INDEX_FALLBACK


def test_active_index_without_data() -> None:
    """Missing data resolves to the primary pool rather than raising."""
    assert active_pool_index(None) == POOL_INDEX_PRIMARY
    assert active_pool_field(None, ATTR_STRATUM_URL, ATTR_FALLBACK_STRATUM_URL) is None


def test_active_field_unconfigured_pool_is_unknown() -> None:
    """An unconfigured pool reports an empty string, surfaced as None."""
    data = {
        "stratumURL": "",
        "stratum": {"pools": [{"active": True}]},
    }
    assert active_pool_field(data, ATTR_STRATUM_URL, ATTR_FALLBACK_STRATUM_URL) is None


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ({"stratum": {"usingFallback": True}}, True),
        ({"stratum": {"usingFallback": False}}, False),
        ({"isUsingFallbackStratum": True}, True),
        ({"isUsingFallbackStratum": False}, False),
        # Dual-pool mode reports neither field: no failover is happening.
        ({"stratum": {"activePoolMode": 1}}, False),
        ({}, False),
        (None, False),
    ],
)
def test_is_using_fallback(data: dict[str, Any] | None, expected: bool) -> None:
    """The nested flag wins, with the legacy flat field as a fallback."""
    assert is_using_fallback(data) is expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ({"stratum": {"activePoolMode": 0}}, "failover"),
        ({"stratum": {"activePoolMode": 1}}, "dual"),
        # Unknown or missing modes fall back to the firmware default.
        ({"stratum": {"activePoolMode": 7}}, "failover"),
        ({}, "failover"),
        (None, "failover"),
    ],
)
def test_pool_mode_name(data: dict[str, Any] | None, expected: str) -> None:
    """The pool mode is exposed as a stable slug for automations."""
    assert pool_mode_name(data) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [("pool.example.com", "pool.example.com"), ("", None), ("   ", None), (0, 0)],
)
def test_clean_value(value: Any, expected: Any) -> None:
    """Blank strings become None; other values pass through untouched."""
    assert clean_value(value) == expected
