"""Support for NerdQAxe+ Miner update entity."""
from __future__ import annotations

import logging
from typing import Any
import re
from datetime import timedelta

import aiohttp
import async_timeout

from homeassistant.components.update import (
    UpdateEntity,
    UpdateEntityFeature,
    UpdateDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.event import async_track_time_interval

from . import NerdQAxeDataUpdateCoordinator
from .const import (
    DOMAIN,
    API_OTA_GITHUB,
    API_OTA_WWW_GITHUB,
    ATTR_DEVICE_MODEL,
    ATTR_VERSION,
    GITHUB_API_URL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NerdQAxe+ Miner update entity."""
    coordinator: NerdQAxeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        NerdQAxeUpdateEntity(coordinator),
        NerdQAxeWWWUpdateEntity(coordinator),
    ]

    async_add_entities(entities)


class NerdQAxeUpdateEntity(CoordinatorEntity, UpdateEntity):
    """Representation of a NerdQAxe+ update entity."""

    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = UpdateEntityFeature.INSTALL | UpdateEntityFeature.RELEASE_NOTES

    def __init__(self, coordinator: NerdQAxeDataUpdateCoordinator) -> None:
        """Initialize the update entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_update"
        self._attr_name = "NerdQAxe Firmware Update"
        self._latest_version: str | None = None
        self._release_notes: str | None = None
        self._download_url: str | None = None

        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": f"NerdQAxe+ Miner ({coordinator.host})",
            "manufacturer": "NerdQAxe",
            "model": coordinator.data.get(ATTR_DEVICE_MODEL, "Unknown") if coordinator.data else "Unknown",
        }

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        # Check for latest release immediately when added
        await self._async_check_latest_release()

        # Schedule periodic checks every 6 hours
        self.async_on_remove(
            async_track_time_interval(
                self.hass,
                self._async_periodic_update,
                timedelta(hours=6)
            )
        )

    async def _async_periodic_update(self, now) -> None:
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
                        r for r in releases
                        if not r.get("prerelease", False) and "-rc" not in r.get("tag_name", "")
                    ]

                    if stable_releases:
                        latest = stable_releases[0]
                        self._latest_version = latest.get("tag_name", "").lstrip("v")
                        self._release_notes = latest.get("body", "")

                        # Find the correct firmware file for this device model
                        if self.coordinator.data:
                            device_model = self.coordinator.data.get(ATTR_DEVICE_MODEL, "")
                            # Normalize device model (remove spaces, replace γ with Gamma)
                            normalized_model = device_model.replace("γ", "Gamma").replace(" ", "")
                            expected_filename = f"esp-miner-{normalized_model}.bin"

                            for asset in latest.get("assets", []):
                                if asset.get("name") == expected_filename:
                                    self._download_url = asset.get("browser_download_url")
                                    break

                        _LOGGER.debug(f"Latest version: {self._latest_version}, URL: {self._download_url}")

        except aiohttp.ClientError as err:
            _LOGGER.warning(f"Failed to check for updates: {err}")
        except Exception as err:
            _LOGGER.error(f"Unexpected error checking for updates: {err}")

    @property
    def installed_version(self) -> str | None:
        """Return the installed version."""
        if not self.coordinator.data:
            return None
        version = self.coordinator.data.get(ATTR_VERSION, "")
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
            return f"https://github.com/shufps/ESP-Miner-NerdQAxePlus/releases/tag/v{self._latest_version}"
        return None

    async def async_release_notes(self) -> str | None:
        """Return the release notes."""
        return self._release_notes

    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare two semantic versions.
        Returns: 1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        # Remove 'v' prefix if present
        clean_v1 = v1.lstrip("v")
        clean_v2 = v2.lstrip("v")

        # Extract version parts (handle both x.y.z and x.y formats)
        parts1 = [int(p) for p in re.findall(r'\d+', clean_v1)]
        parts2 = [int(p) for p in re.findall(r'\d+', clean_v2)]

        # Pad with zeros if needed
        max_len = max(len(parts1), len(parts2))
        parts1.extend([0] * (max_len - len(parts1)))
        parts2.extend([0] * (max_len - len(parts2)))

        for p1, p2 in zip(parts1, parts2):
            if p1 > p2:
                return 1
            if p1 < p2:
                return -1

        return 0

    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        """Install an update."""
        if not self._download_url:
            _LOGGER.error("No download URL available for update")
            return

        _LOGGER.info(f"Starting firmware update from {self._download_url}")

        try:
            async with async_timeout.timeout(300):  # 5 minute timeout for OTA
                async with self.coordinator.session.post(
                    f"{self.coordinator.base_url}{API_OTA_GITHUB}",
                    json={"url": self._download_url},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response.raise_for_status()
                    result = await response.text()
                    _LOGGER.info(f"Firmware update initiated: {result}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Failed to update firmware: {err}")
            raise


class NerdQAxeWWWUpdateEntity(CoordinatorEntity, UpdateEntity):
    """Representation of a NerdQAxe+ WWW update entity."""

    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = UpdateEntityFeature.INSTALL | UpdateEntityFeature.RELEASE_NOTES

    def __init__(self, coordinator: NerdQAxeDataUpdateCoordinator) -> None:
        """Initialize the update entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_www_update"
        self._attr_name = "NerdQAxe WWW Update"
        self._latest_version: str | None = None
        self._release_notes: str | None = None
        self._download_url: str | None = None

        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.host)},
            "name": f"NerdQAxe+ Miner ({coordinator.host})",
            "manufacturer": "NerdQAxe",
            "model": coordinator.data.get(ATTR_DEVICE_MODEL, "Unknown") if coordinator.data else "Unknown",
        }

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        # Check for latest release immediately when added
        await self._async_check_latest_release()

        # Schedule periodic checks every 6 hours
        self.async_on_remove(
            async_track_time_interval(
                self.hass,
                self._async_periodic_update,
                timedelta(hours=6)
            )
        )

    async def _async_periodic_update(self, now) -> None:
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
                        r for r in releases
                        if not r.get("prerelease", False) and "-rc" not in r.get("tag_name", "")
                    ]

                    if stable_releases:
                        latest = stable_releases[0]
                        self._latest_version = latest.get("tag_name", "").lstrip("v")
                        self._release_notes = latest.get("body", "")

                        # Find the www.bin file
                        for asset in latest.get("assets", []):
                            if asset.get("name") == "www.bin":
                                self._download_url = asset.get("browser_download_url")
                                break

                        _LOGGER.debug(f"Latest WWW version: {self._latest_version}, URL: {self._download_url}")

        except aiohttp.ClientError as err:
            _LOGGER.warning(f"Failed to check for WWW updates: {err}")
        except Exception as err:
            _LOGGER.error(f"Unexpected error checking for WWW updates: {err}")

    @property
    def installed_version(self) -> str | None:
        """Return the installed version."""
        if not self.coordinator.data:
            return None
        version = self.coordinator.data.get(ATTR_VERSION, "")
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
            return f"https://github.com/shufps/ESP-Miner-NerdQAxePlus/releases/tag/v{self._latest_version}"
        return None

    async def async_release_notes(self) -> str | None:
        """Return the release notes."""
        return self._release_notes

    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        """Install an update."""
        if not self._download_url:
            _LOGGER.error("No download URL available for WWW update")
            return

        _LOGGER.info(f"Starting WWW update from {self._download_url}")

        try:
            async with async_timeout.timeout(300):  # 5 minute timeout for OTA
                async with self.coordinator.session.post(
                    f"{self.coordinator.base_url}{API_OTA_WWW_GITHUB}",
                    json={"url": self._download_url},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response.raise_for_status()
                    result = await response.text()
                    _LOGGER.info(f"WWW update initiated: {result}")
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Failed to update WWW: {err}")
            raise
