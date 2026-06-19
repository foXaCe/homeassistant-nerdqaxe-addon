# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Entities and the device are now identified by the miner **MAC address**
  instead of its IP/host, so they survive IP changes. Existing setups are
  migrated automatically (config entry v1 → v2) — no entities or history are
  lost. Device info now also exposes `sw_version`, `configuration_url` and the
  network MAC connection
- Control actions (restart, ASIC frequency, core voltage) now surface a clear
  error in Home Assistant when the miner rejects the command, instead of a raw
  traceback

### Fixed
- Firmware update no longer reports a false failure. The miner now runs the
  factory OTA asynchronously (`POST` returns `202 Accepted` and the device
  flashes then reboots, dropping the HTTP connection). The update entity treats
  that expected disconnect/timeout as success and only surfaces genuine
  rejections — a busy miner (`409`) or an HTTP error status

## [2.1.0] - 2026-06-19

### Added
- `Core Voltage Actual` sensor exposing the measured ASIC voltage (`coreVoltageActual`),
  distinct from the commanded `Core Voltage` (#14)

### Changed
- Release workflow now sources its notes from `CHANGELOG.md` instead of PR labels

### Fixed
- `Stratum Connected` binary sensor always reported disconnected: it read a
  non-existent flat `isStratumConnected` field. It now reads the nested
  `stratum.pools[].connected` structure exposed by the firmware, with a legacy
  fallback for older firmware (#13)

## [2.0.1] - 2026-01-25

### Changed
- Bump `codecov/codecov-action` from 4 to 5
- Bump `actions/stale` from 9 to 10
- Bump `actions/checkout` from 4 to 6
- Bump `actions/setup-python` from 5 to 6
- Bump `mikepenz/release-changelog-builder-action` from 5 to 6

## [2.0.0] - 2026-01-24

### Added
- Combined factory OTA for firmware updates (firmware + www in single operation)
- Comprehensive test suite with 80%+ coverage
- GitHub Actions CI/CD pipeline (lint, test, hassfest, HACS validation)
- Pre-commit hooks (ruff, codespell)
- Diagnostics support with sensitive data redaction
- `runtime_data` pattern for modern Home Assistant architecture
- Type alias `NerdQAxeConfigEntry` for strict typing
- `Debouncer` in coordinator to prevent API hammering

### Changed
- **BREAKING**: Migrated from `hass.data[DOMAIN]` to `entry.runtime_data` pattern
- Refactored coordinator with typed exceptions (`NerdQAxeApiError`, `NerdQAxeConnectionError`, `NerdQAxeTimeoutError`)
- Added `__slots__` to all entity classes for memory optimization
- Added `suggested_display_precision` to numeric sensors
- Improved entity naming with `_attr_has_entity_name = True`
- Updated coordinator with generic type `DataUpdateCoordinator[dict[str, Any]]`
- Return `DeviceInfo` instead of dict for proper typing

### Fixed
- Manifest keys sorted alphabetically (hassfest compliance)
- Resolved all mypy type errors
- Reduced log spam for normal connection errors (debug level)
- Improved error handling with clearer messages
- Hashrate sensors device class error

## [1.3.5] - 2024-01-24

### Fixed
- Reduced log spam for normal connection errors (device offline)
- Connection errors now logged at debug level instead of warning

## [1.3.4] - 2024-01-20

### Fixed
- Improved error handling with better compatibility and clearer messages

## [1.3.3] - 2024-01-19

### Fixed
- Various bug fixes and improvements

## [1.3.0] - 2024-10-12

### Added
- Number entities for ASIC frequency and core voltage control
- Update entities for firmware and WWW OTA updates
- Localized uptime display (7 languages supported)

## [1.2.0] - 2024-10-05

### Added
- Button entity for miner restart
- Binary sensor for Stratum connection status

## [1.1.0] - 2024-10-03

### Added
- Options flow for configurable scan interval
- Additional sensors (found blocks, core voltage, frequency)

## [1.0.0] - 2024-10-03

### Added
- Initial release
- Config flow for device setup
- Sensor entities for hashrate, temperature, power, fan, mining stats
- Full French and English translations
- HACS compatibility
