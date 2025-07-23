# Changelog

All notable changes to the MDA project will be documented in this file.

## [Unreleased] - 2025-07-23

### Added
- Separated Web UI as independent service (`pim-ui/`)
- Instance management functionality for running multiple model instances
- Real-time compilation progress feedback in UI
- Visual indicators for model compilation status
- Hard unload feature with complete file cleanup
- Type-safe instance models with Pydantic (`instance_models.py`)
- Background execution pattern documentation in CLAUDE.md

### Changed
- Moved compiler code from `pim-engine` to `pim-compiler` for clean separation
- Updated default port from 8001 to 8000 for PIM Engine
- Changed startup command from `./start.sh` to `./start_master.sh`
- Improved error handling for Optional fields in Python code
- Enhanced model upload UI with better user feedback

### Fixed
- API field mismatch between frontend and backend (name vs instance_id)
- Type checking errors for Optional fields in rule_engine.py and engine.py
- File deletion issue during hard unload operation
- Upload modal not closing immediately after upload
- Compilation progress not showing after model upload

### Architecture
- Clear separation of concerns:
  - `pim-engine/`: Runtime interpretation only
  - `pim-compiler/`: Code generation functionality
  - `pim-ui/`: Web interface
- Removed code generation endpoints from engine API
- Cleaned up cross-dependencies between components

## [2.0.0] - 2025-07-21

### Added
- PIM Execution Engine v2.0 with master-worker architecture
- Hot reload capability (5-second detection)
- Dynamic API generation from PIM models
- Flow debugging interface
- Gemini CLI integration for code generation

### Changed
- Switched from template-based to LLM-based code generation
- Migrated from Docker to standalone Python application
- Updated from single-process to multi-process architecture

## [1.0.0] - 2025-07-20

### Added
- Initial PIM Execution Engine implementation
- Basic model loading and interpretation
- REST API generation
- SQLite database support
- YAML and Markdown model formats