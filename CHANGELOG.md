# Changelog

All notable changes to the **SH Script Runner** extension will be documented in this file.

## [1.0.0] - 2026-02-04

### Added
- **Initial Release**: Core functionality to scan and execute `.sh` scripts from a custom directory.
- **Path Expansion Support**: Added ability to use `~/` and `$HOME` in the script directory configuration.
- **Auto-Permission**: Extension now automatically applies `chmod +x` to scripts before execution.
- **Terminal Integration**: Scripts are executed within a terminal emulator (configurable) to support interactive commands and output viewing.
- **Dynamic Formatting**: Script filenames are automatically cleaned for the Ulauncher UI (removes extensions, replaces dashes/underscores with spaces, and applies title casing).
- **Interactive Preferences**: Added configuration UI for Scripts Directory and Terminal Emulator choice.
- **Multiple Base Path**: Added support multiple base path.

### Fixed
- Fixed `ModuleNotFoundError` by updating imports to Ulauncher API v2.0.0 (`ExtensionResultItem`).
- Fixed process termination issues by using `start_new_session=True` for spawned processes.

### Technical Details
- Built with **Python 3**.
- Compatible with **Ulauncher API v2.0.0**.