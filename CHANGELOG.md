# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `diagnostics.py` for debug support with sensitive data redaction
- `runtime_data` pattern for modern Home Assistant architecture
- `Debouncer` in coordinator to prevent API hammering
- `_attr_has_entity_name = True` on all entities for proper naming
- Type alias `NerdQAxeConfigEntry` for strict typing
- `@dataclass(slots=True)` for `NerdQAxeRuntimeData`

### Changed
- Migrated from `hass.data[DOMAIN]` to `entry.runtime_data` pattern
- Improved entity naming to follow Home Assistant conventions
- Updated coordinator with generic type `DataUpdateCoordinator[dict]`

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
