# eSim Automated Tool Manager - Design Document

## 1. Introduction
eSim is an open-source EDA tool for circuit design, simulation, analysis, and PCB design. It relies on external tools and libraries (e.g., Ngspice, KiCad). Manually managing these tools, ensuring they are installed, compatible, and up-to-date, is challenging. The Automated Tool Manager is a standalone Python utility designed to automate this process.

## 2. Problem Statement
Users often encounter issues where required external tools are missing, outdated, or installed in non-standard locations, causing eSim to fail. The lack of an automated way to detect, verify, and install these tools creates a high barrier to entry and ongoing maintenance friction.

## 3. Objectives
- Provide a unified interface to manage eSim dependencies.
- Automatically detect installed tools and their locations.
- Verify installed tool versions against known-good or required versions.
- Automate the installation of missing tools using system-native package managers where possible.
- Provide a robust, configurable, and extensible platform that does not require modifying code to support new tools.

## 4. Functional Requirements
- **Detection**: The system must verify if required executables exist on the system PATH or common installation directories.
- **Version Checking**: The system must execute tools to retrieve their version and compare it mathematically/lexicographically against a requirement.
- **Installation**: The system must be capable of installing missing tools (e.g., via `winget` on Windows).
- **Configuration**: Tool definitions must reside in an external JSON configuration file.
- **User Interface**: A simple command-line interface (CLI) menu system.

## 5. Non-functional Requirements
- **Compatibility**: Windows-first approach, with an architecture that allows for Linux/macOS support.
- **Dependencies**: Built entirely on the Python Standard Library to ensure easy deployment. No `pip install` required for core features.
- **Reliability**: Graceful error handling; the application must not crash due to missing tools or malformed configurations.
- **Security**: No arbitrary command execution. Safe `subprocess` usage without `shell=True`.

## 6. System Architecture
The application uses a modular, layered architecture.
1.  **Presentation Layer**: `main.py` (CLI Menu and display logic).
2.  **Business Logic Layer**: The `tool_manager/` package (`detector`, `version_checker`, `installer`).
3.  **Data Layer**: `config.py` and `tools.json`.

## 7. Configuration Design
Configuration is centralized in `config/tools.json`. This allows the tool manager to be entirely data-driven.

```json
{
    "ngspice": {
        "name": "Ngspice",
        "executable": "ngspice",
        "version_command": ["ngspice", "--version"],
        "required_version": "44",
        "installer": {
            "windows": { "type": "winget", "winget_id": "Ngspice.Ngspice" }
        }
    }
}
```
This design separates *what* tools need to be managed from *how* the manager works.

## 8. Tool Detection Flow
1. `detector.py` receives a tool configuration.
2. It attempts `shutil.which(executable)` to find the tool on the system PATH.
3. If not found, it iterates through optional `additional_paths` defined in the JSON.
4. Returns a `DetectionResult` object containing the status and resolved path.

## 9. Version Checking Flow
1. `version_checker.py` calls the detector to ensure the tool exists and to get its exact path.
2. It runs `subprocess.run(version_command)` with a timeout.
3. Both `stdout` and `stderr` are combined and scanned using a regular expression (`version_pattern`) to extract the version string.
4. The extracted string is parsed into an integer tuple (e.g., `(8, 1, 0)`) for safe mathematical comparison against the `required_version`.

## 10. Installation Flow
1. `installer.py` checks if the tool is already installed.
2. It determines the correct installation method based on the current OS and the tool's config.
3. The user is prompted for confirmation.
4. The installation subprocess is executed (e.g., `winget install --id ...`).
5. A post-installation verification (detection + version check) is run automatically to confirm success.

## 11. Security Considerations
- **Command Injection**: `subprocess` is used with a list of arguments, avoiding shell interpolation.
- **User Confirmation**: No system modifications (installations) happen without explicit user confirmation.
- **Downloads**: Automated downloading of arbitrary binaries is avoided in favor of trusted package managers (`winget`, `apt`) or manual download instructions.

## 12. Testing Strategy
Unit tests utilizing Python's `unittest` and `unittest.mock` libraries.
- Tests verify logic (version comparison, JSON parsing, error handling) without interacting with the actual operating system state or executing real installers.

## 13. Limitations & Future Improvements
- **Limitations**: Currently relies heavily on standard output parsing, which can break if a tool fundamentally changes how it prints its version.
- **Future Improvements**:
    - Add native support for Linux package managers (apt, dnf) and macOS (Homebrew).
    - Add a graphical user interface (GUI) using `tkinter` or `PyQt`.
    - Allow configuring alternative installation paths.
