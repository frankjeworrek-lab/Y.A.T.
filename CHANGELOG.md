# Changelog

All notable changes to Y.A.T. (Yet Another Talk) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.2.15] - 2026-01-04
### Changed
- **UI Status Refinement:** Replaced "Bubble" design with "Tech-Chip" aesthetic (Dark Capsule, Monospace-style text, Frameless).
- **Control Layout:** Unified right-side controls with context-aware animations (e.g., spinning refresh icon).
- **Guidelines:** Added "Feedback Reflection Protocol" to prevent impulsive scope creep.

## [v0.2.14] - 2026-01-04
### Added
- **Active Assistance UI (Status Matrix v2):** Comprehensive status indicator system with "Problem ➜ Solution" logic.
- **Contextual Status:** Provider-specific error messages (e.g., "[Mistral]: Auth Failed").
- **Verification Flow:** Clickable status badge triggers self-check and verification.
- **Guidelines Update:** New protocols for Work Packages and State Safety.



---

## [v0.2.13] - 2026-01-03
### Added
- **Active User Assistance:** Interactive status badges with "Trust through Verification" workflow.
  - Clicking a Green badge verifies the connection (Peace of Mind).
  - Clicking a Yellow/Red badge triggers a smart repair/retry loop.
  - Visual Pulse animation for "Action Required" states (Yellow/Red).
- **UX Philosophy:** New documentation (`docs/UX_PHILOSOPHY.md`) defining the "Active Assistance" concept.
- **Guidelines:** Added "Work Packet Definition Protocol" to AI Collaboration Guidelines.

## [v0.2.12] - 2026-01-03

### Added
- **Mac Build Automation:**
  - GitHub Actions workflow for macOS builds (`.github/workflows/build_mac.yml`)
  - Automated creation of `.app` bundle and `.dmg` disk image
  - Parallel builds: Windows + Mac triggered by single tag push

- **Smart Build Auto-Download:**
  - New `tools/auto_download_builds.sh` script
  - Automatically waits for GitHub Actions completion
  - Downloads all platform artifacts to `./builds/` directory
  - Desktop notification on completion (macOS)
  - No manual artifact retrieval needed

### Changed
- **AI Collaboration Guidelines:**
  - Added Principle #9: Build & Distribution Automation
  - Updated release workflow documentation
  - AI now automatically triggers build downloads after tag push

### Technical
- Extended `.gitignore` to exclude `./builds/` directory
- Multi-platform build pipeline fully automated

---

## [v0.2.11] - 2026-01-03

### Fixed
- **Factory Reset Feature Completion:**
  - Fixed missing "Restart/Close" choice dialog after factory reset execution
  - Dialog now correctly recycles container instead of creating new one
  - Eliminated `SystemExit` tracebacks using `os._exit()` with async delays
  - Added PyWebView window closure support for desktop mode
  - Factory Reset now fully functional: Warning → Reset → Choice (Restart/Close)

### Removed
- Obsolete standalone reset scripts (`tools/reset_data.py`, `tools/reset_windows.bat`)
  - In-app Factory Reset feature replaces external tools

---

## [v0.2.10] - 2026-01-03

### Added
- **Version number display** in window title (`Y.A.T. v0.2.10`)
  - Visible in both desktop and web modes
  - Available in `main.py` as `APP_VERSION` constant

### Fixed
- Version number now correctly appears in PyWebView window title
- Version number now correctly appears in browser tab title

### Technical
- Centralized version management in `main.py::APP_VERSION`

---

## [v0.2.9] - 2026-01-03

### Added
- Initial version number implementation (partial)

### Fixed
- Attempted to add version to UI (incomplete implementation)

### Known Issues
- Version only visible in page title, not in window title (fixed in v0.2.10)

---

## [v0.2.8] - 2026-01-03

### Added
- **Interactive Connection Repair:** Click on status badge to retry failed connections
  - Status badge is now clickable when provider has errors
  - Optimistic UI feedback (spinner) during retry attempt
  - Success/failure notifications after retry

- **Connection Monitor (Wächter):**
  - Passive internet connectivity monitoring (checks every 30s)
  - Visual indicator in sidebar footer ("System Online" / "Network Error")
  - Helps distinguish between provider issues and internet problems

- **Optimistic UI:**
  - Immediate visual feedback when saving provider settings
  - Status badge shows "Connecting..." spinner before async operations complete
  - Eliminates "frozen UI" perception on slower systems

### Fixed
- **Phantom yellow state:** Status badge now correctly updates to green after successful connection
  - Added UI refresh in `_handle_status_click` for "healthy" connections
  - Ensures visual state matches internal provider status

- **UnicodeEncodeError on Windows console:**
  - Replaced Unicode characters (✓, ✗) with ASCII equivalents ([OK], [ERR])
  - Prevents crash during provider re-initialization on Windows (cp1252 encoding)

### Changed
- **Actionable error messages:**
  - Status text now reads "Failed: Click to Retry" instead of generic errors
  - "Connection Lost (Retry)" replaces "No Active Provider" in certain cases
  - Clear call-to-action for users when issues occur

### Performance
- **Windows-specific optimizations:**
  - Force IPv4 loopback (`host='127.0.0.1'`) to avoid 1-second IPv6 timeout
  - Added `multiprocessing.freeze_support()` for PyInstaller stability

### Technical
- Added `ui_nicegui/components/connection_status.py` (ConnectionMonitor)
- Enhanced `_handle_status_click()` async handler in Sidebar
- Implemented `set_optimistic_state()` method for immediate UI feedback

---

## [v0.2.7-ux-fix] - 2026-01-03

### Fixed
- Refinement of retry interaction texts
- Additional phantom state handling

---

## [v0.2.6-interactive] - 2026-01-03

### Added
- Initial implementation of interactive status repair

---

## [v0.2.5-ui-polish] - 2026-01-03

### Added
- Initial UX improvements for connection handling

---

## Earlier Versions

For versions prior to v0.2.5, please refer to Git commit history.

---

## Legend

- **Added:** New features
- **Changed:** Changes to existing functionality
- **Deprecated:** Soon-to-be removed features
- **Removed:** Removed features
- **Fixed:** Bug fixes
- **Security:** Security improvements
- **Performance:** Performance improvements
- **Technical:** Internal/developer-facing changes
