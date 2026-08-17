"""Mining pool resolution helpers.

The miner reports its pool endpoints as flat fields (``stratumURL`` and
friends for the primary pool, ``fallbackStratum*`` for the fallback one) while
the nested ``stratum.pools[]`` array carries the runtime state — which pool is
connected and which one is actually mining — without any address. Reporting
"the pool currently in use" therefore means crossing the two, which is what
this module does for both the sensor and binary sensor platforms.
"""

from __future__ import annotations

from typing import Any

from .const import (
    ATTR_ACTIVE_POOL_MODE,
    ATTR_POOL_ACTIVE,
    ATTR_STRATUM,
    ATTR_STRATUM_POOLS,
    ATTR_USING_FALLBACK,
    ATTR_USING_FALLBACK_LEGACY,
    POOL_INDEX_FALLBACK,
    POOL_INDEX_PRIMARY,
    POOL_MODE_DUAL,
    POOL_MODE_FAILOVER,
    POOL_MODE_NAMES,
)


def clean_value(value: Any) -> Any:
    """Return ``None`` for unset string fields, the value otherwise.

    An unconfigured pool is reported as an empty string rather than being
    omitted, which would otherwise surface as an empty state instead of an
    honest "unknown".
    """
    if isinstance(value, str) and not value.strip():
        return None
    return value


def is_using_fallback(data: dict[str, Any] | None) -> bool:
    """Return True if the miner switched to its fallback pool.

    The failover manager exposes ``stratum.usingFallback``; older firmware used
    a flat ``isUsingFallbackStratum`` field. Neither is present in dual-pool
    mode, where both pools mine and no failover happens.
    """
    if not data:
        return False

    stratum = data.get(ATTR_STRATUM) or {}
    if ATTR_USING_FALLBACK in stratum:
        return bool(stratum[ATTR_USING_FALLBACK])

    return bool(data.get(ATTR_USING_FALLBACK_LEGACY, False))


def pool_mode(data: dict[str, Any] | None) -> int:
    """Return the pool mode the miner currently runs in.

    Falls back to failover, which is the firmware default and the only mode
    older firmware knows about.
    """
    if not data:
        return POOL_MODE_FAILOVER

    stratum = data.get(ATTR_STRATUM) or {}
    mode = stratum.get(ATTR_ACTIVE_POOL_MODE)
    return mode if mode in POOL_MODE_NAMES else POOL_MODE_FAILOVER


def pool_mode_name(data: dict[str, Any] | None) -> str:
    """Return the pool mode as a stable slug for use in entity attributes."""
    return POOL_MODE_NAMES[pool_mode(data)]


def active_pool_index(data: dict[str, Any] | None) -> int:
    """Return the index of the pool whose endpoint should be reported.

    In dual-pool mode both pools mine and both are flagged ``active``, so the
    primary is reported as the state and the secondary is exposed as an
    attribute of the pool URL sensor. In failover mode the ``active`` flag
    designates the single pool being mined; firmware that does not send the
    flag is resolved through the "using fallback" signal instead.
    """
    if not data:
        return POOL_INDEX_PRIMARY

    if pool_mode(data) == POOL_MODE_DUAL:
        return POOL_INDEX_PRIMARY

    stratum = data.get(ATTR_STRATUM) or {}
    pools = stratum.get(ATTR_STRATUM_POOLS) or []
    for index, pool in enumerate(pools):
        if isinstance(pool, dict) and pool.get(ATTR_POOL_ACTIVE):
            # Only two sets of flat fields exist, so anything past the primary
            # resolves to the fallback endpoint.
            return min(index, POOL_INDEX_FALLBACK)

    return POOL_INDEX_FALLBACK if is_using_fallback(data) else POOL_INDEX_PRIMARY


def active_pool_field(
    data: dict[str, Any] | None,
    primary_key: str,
    fallback_key: str,
) -> Any:
    """Return a pool field, picking the primary or fallback flat key.

    Args:
        data: Coordinator data
        primary_key: Flat field holding the primary pool's value
        fallback_key: Flat field holding the fallback pool's value

    Returns:
        The value for the pool currently in use, or None if unset

    """
    if not data:
        return None

    key = primary_key if active_pool_index(data) == POOL_INDEX_PRIMARY else fallback_key
    return clean_value(data.get(key))
