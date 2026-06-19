"""Support for NerdQAxe+ Miner update entity."""

from __future__ import annotations

from datetime import timedelta
from http import HTTPStatus
import logging
from typing import Any

import aiohttp
import async_timeout
from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NerdQAxeConfigEntry, NerdQAxeDataUpdateCoordinator
from .const import (
    API_OTA_GITHUB,
    ATTR_DEVICE_MODEL,
    ATTR_VERSION,
    GITHUB_API_URL,
)
from .exceptions import NerdQAxeApiError, NerdQAxeError

_LOGGER = logging.getLogger(__name__)

# Only one firmware update entity, and the OTA endpoint must not be hammered.
PARALLEL_UPDATES = 1

# Greek letter gamma for device model normalization
GREEK_GAMMA = "\u03b3"

# Factory OTA timeout (firmware + www combined, can be slow)
OTA_TIMEOUT_SECONDS = 600  # 10 minutes

# Device model to factory filename mapping
# Format: esp-miner-factory-{model}-v{version}.bin
# Note: Some models use Greek gamma in their names
DEVICE_MODEL_MAP = {
    "NerdAxe": "NerdAxe",
    "NerdAxeγ": "NerdAxeGamma",  # noqa: RUF001
    "NerdAxe γ": "NerdAxeGamma",  # noqa: RUF001
    "NerdAxeGamma": "NerdAxeGamma",
    "NerdEKO": "NerdEKO",
    "NerdHaxe-Gamma": "NerdHaxe-Gamma",
    "NerdHaxeGamma": "NerdHaxe-Gamma",
    "NerdHaxe γ": "NerdHaxe-Gamma",  # noqa: RUF001
    "NerdOCTAXE+": "NerdOCTAXE+",
    "NerdOCTAXE-Gamma": "NerdOCTAXE-Gamma",
    "NerdOCTAXEγ": "NerdOCTAXE-Gamma",  # noqa: RUF001
    "NerdOCTAXE γ": "NerdOCTAXE-Gamma",  # noqa: RUF001
    "NerdQAxe+": "NerdQAxe+",
    "NerdQAxe++": "NerdQAxe++",
    "NerdQX": "NerdQX",
}


def normalize_device_model(device_model: str) -> str:
    """Normalize device model name for factory filename matching.

    Args:
        device_model: Raw device model from API

    Returns:
        Normalized model name for factory image filename

    """
    # Try direct mapping first
    if device_model in DEVICE_MODEL_MAP:
        return DEVICE_MODEL_MAP[device_model]

    # Normalize: replace greek gamma, remove spaces
    normalized = device_model.replace(GREEK_GAMMA, "Gamma").replace(" ", "")

    # Check if normalized version is in map
    for key, value in DEVICE_MODEL_MAP.items():
        if key.replace(GREEK_GAMMA, "Gamma").replace(" ", "") == normalized:
            return value

    # Fallback: return normalized version
    return normalized


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NerdQAxeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NerdQAxe+ Miner update entity."""
    coordinator = entry.runtime_data.coordinator

    entities = [
        NerdQAxeUpdateEntity(coordinator),
    ]

    async_add_entities(entities)


class NerdQAxeUpdateEntity(
    CoordinatorEntity[NerdQAxeDataUpdateCoordinator], UpdateEntity
):
    """Representation of a NerdQAxe+ combined firmware update entity.

    Uses factory images that include both firmware and web interface (www).
    Update is performed via /api/system/OTA/github endpoint which downloads
    and flashes both partitions in a single operation.
    """

    __slots__ = ("_download_url", "_latest_version", "_release_notes")

    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = (
        UpdateEntityFeature.INSTALL | UpdateEntityFeature.RELEASE_NOTES
    )
    _attr_has_entity_name = True

    def __init__(self, coordinator: NerdQAxeDataUpdateCoordinator) -> None:
        """Initialize the update entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.unique_id_base}_update"
        self._attr_translation_key = "update"
        self._latest_version: str | None = None
        self._release_notes: str | None = None
        self._download_url: str | None = None

        self._attr_device_info = coordinator.get_device_info()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        # Check for latest release immediately when added
        await self._async_check_latest_release()

        # Schedule periodic checks every 6 hours
        self.async_on_remove(
            async_track_time_interval(
                self.hass, self._async_periodic_update, timedelta(hours=6)
            )
        )

    async def _async_periodic_update(self, now: Any) -> None:
        """Periodic update to check for new releases."""
        await self._async_check_latest_release()
        self.async_write_ha_state()

    async def _async_check_latest_release(self) -> None:
        """Check GitHub for the latest release."""
        try:
            async with async_timeout.timeout(10):
                async with self.coordinator.session.get(GITHUB_API_URL) as response:
                    response.raise_for_status()
                    releases = await response.json()

                    # Filter out pre-releases and rc versions
                    stable_releases = [
                        r
                        for r in releases
                        if not r.get("prerelease", False)
                        and "-rc" not in r.get("tag_name", "")
                    ]

                    if stable_releases:
                        latest = stable_releases[0]
                        tag_name = latest.get("tag_name", "")
                        self._latest_version = tag_name.lstrip("v")
                        self._release_notes = latest.get("body", "")

                        # Find the correct factory firmware file for this device
                        if self.coordinator.data:
                            device_model = self.coordinator.data.get(
                                ATTR_DEVICE_MODEL, ""
                            )
                            normalized_model = normalize_device_model(device_model)

                            # Factory image: esp-miner-factory-{model}-{tag}.bin
                            expected_filename = (
                                f"esp-miner-factory-{normalized_model}-{tag_name}.bin"
                            )

                            for asset in latest.get("assets", []):
                                if asset.get("name") == expected_filename:
                                    self._download_url = asset.get(
                                        "browser_download_url"
                                    )
                                    break
                            else:
                                # No matching firmware found
                                available = [
                                    a.get("name")
                                    for a in latest.get("assets", [])
                                    if a.get("name", "").startswith("esp-miner-factory")
                                ]
                                _LOGGER.warning(
                                    "No factory firmware for model '%s' "
                                    "(expected: %s). Available: %s",
                                    device_model,
                                    expected_filename,
                                    available,
                                )

                        _LOGGER.debug(
                            "Latest firmware version: %s, URL: %s",
                            self._latest_version,
                            self._download_url,
                        )

        except aiohttp.ClientError as err:
            _LOGGER.warning("Failed to check for firmware updates: %s", err)
        except Exception as err:
            _LOGGER.error("Unexpected error checking for firmware updates: %s", err)

    @property
    def installed_version(self) -> str | None:
        """Return the installed version."""
        if not self.coordinator.data:
            return None
        version: str = self.coordinator.data.get(ATTR_VERSION, "")
        # Remove 'v' prefix if present
        return version.lstrip("v")

    @property
    def latest_version(self) -> str | None:
        """Return the latest version."""
        return self._latest_version

    @property
    def release_url(self) -> str | None:
        """Return the URL for release notes."""
        if self._latest_version:
            return (
                "https://github.com/shufps/ESP-Miner-NerdQAxePlus/"
                f"releases/tag/v{self._latest_version}"
            )
        return None

    async def async_release_notes(self) -> str | None:
        """Return the release notes."""
        return self._release_notes

    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        """Install a firmware update via the combined factory OTA endpoint.

        The miner runs the OTA asynchronously: the POST returns
        ``202 Accepted`` (``{"status": "started"}``) and a background task
        flashes both firmware and web interface before rebooting. The reboot
        tears down the HTTP connection, so a connection error *after* the
        request has been accepted is expected and must not be reported as a
        failed install. Only a response the miner actively rejects (e.g. a
        busy ``409`` or a ``4xx``/``5xx`` status) is a real failure.
        """
        if not self._download_url:
            raise NerdQAxeError(
                "No matching factory firmware was found for this device model; "
                "cannot start the update"
            )

        _LOGGER.info(
            "Starting combined firmware update from %s on %s",
            self._download_url,
            self.coordinator.host,
        )

        url = f"{self.coordinator.base_url}{API_OTA_GITHUB}"
        try:
            async with (
                async_timeout.timeout(OTA_TIMEOUT_SECONDS),
                self.coordinator.session.post(
                    url,
                    json={"url": self._download_url},
                    headers={"Content-Type": "application/json"},
                ) as response,
            ):
                # The miner already runs an OTA; nothing to do.
                if response.status == HTTPStatus.CONFLICT:
                    raise NerdQAxeError(
                        "A firmware update is already in progress on the miner"
                    )
                # Real rejection (bad/unsafe URL, auth, server error, ...).
                response.raise_for_status()
                result = await response.text()
                _LOGGER.info(
                    "Firmware update accepted by %s (HTTP %s): %s",
                    self.coordinator.host,
                    response.status,
                    result,
                )
        except aiohttp.ClientResponseError as err:
            # The miner answered with an error status: genuine failure.
            raise NerdQAxeApiError(
                f"Miner rejected the firmware update (HTTP {err.status})"
            ) from err
        except (aiohttp.ClientError, TimeoutError) as err:
            # Connection dropped/timed out while the miner was flashing and
            # rebooting. The OTA runs on the device itself, so this is the
            # expected outcome — the new version shows up once it is back.
            _LOGGER.info(
                "Connection to %s closed during OTA (expected while the miner "
                "reboots): %s",
                self.coordinator.host,
                err,
            )
