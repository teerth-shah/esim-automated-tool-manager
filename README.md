# eSim Automated Tool Manager

An automated utility to detect, check versions, and install external tools required by eSim (an open-source EDA tool from FOSSEE).

## Problem Statement
eSim integrates several external tools and libraries (like Ngspice, KiCad, etc.) to provide a seamless environment for engineers and researchers. Managing these tools manually can be tedious, especially when considering updates, compatibility, and user-specific configurations. The eSim Automated Tool Manager solves this by providing a unified interface to detect installed tools, compare versions, and automatically install missing tools.

## Features
### Implemented
- **Tool Detection**: Dynamically locates tools on the system PATH or configured candidate paths.
- **Version Checking**: Executes tool-specific version commands, parses outputs using regex, and safely compares against required versions.
- **Automated Installation**: Supports installing missing tools via `winget` (Windows Package Manager), system package managers (apt), or providing manual download instructions.
- **Post-Install Verification**: Automatically detects tools and checks their versions immediately after installation.
- **Status Dashboard**: Provides a comprehensive summary of all configured tools, their installed versions, and their status (OK, MISSING, UPDATE_AVAILABLE).
- **Configuration Management**: Uses a centralized `config/tools.json` file for all tool metadata, making it easy to add new tools without modifying code.
- **Logging**: Maintains detailed logs in `logs/tool_manager.log` for debugging and auditing.

### Planned/Future
- Full cross-platform testing on macOS and various Linux distributions (architecture is designed to support them, but currently Windows-first).
- Automated dependency resolution between tools.
- Rich GUI interface.

## Architecture
The project follows a modular architecture:
- `main.py`: The entry point and interactive Command-Line Interface (CLI).
- `tool_manager/detector.py`: Handles finding tool executables on the system.
- `tool_manager/version_checker.py`: Handles executing version commands and comparing versions.
- `tool_manager/installer.py`: Handles the installation process via various backends (winget, apt, manual).
- `tool_manager/config.py`: Manages reading and validating the tool configuration JSON.
- `tool_manager/platform_utils.py`: Isolates all OS-specific checks and system information retrieval.

## Technology Stack
- **Language**: Python 3.8+ (Standard Library Only - No external dependencies for core functionality)
- **Data Format**: JSON
- **Platform**: Windows 10/11 (Primary), Linux (Designed for compatibility)
- **Installers**: `winget` (Windows Package Manager)

## Requirements
- Python 3.8 or higher.
- Windows 10 or 11 (for `winget` support) or a Linux distribution.
- No third-party Python packages are strictly required for the core application to run.

## Installation & Running

This project uses the Python Standard Library and requires no external dependencies for its core functionality.

1. **Ensure Python is installed** (Python 3.8+ recommended).
2. **Open a terminal/command prompt** and navigate to the project folder.
3. **Run the application**:
   ```bash
   python main.py
   ```

## Usage
Once the application starts, you will see an interactive CLI menu:

1. **Check Tools**: Detects which configured tools are currently installed on your system.
2. **Check Versions**: Detects tools and compares their installed versions against the recommended versions.
3. **Install Tool**: Presents a list of missing tools and guides you through the installation process (uses `winget` on Windows).
4. **Verify Tool**: Perform a deep check of a specific tool's installation status and version.
5. **Show Status**: Displays a comprehensive dashboard showing all tools, their installation status, and version status.
6. **View Logs**: Shows the most recent entries from the application log.
7. **Exit**: Closes the application.

## Configuration
Tools are defined in `config/tools.json`. To add a new tool, simply add a new JSON object to the file:

```json
{
    "new_tool": {
        "name": "New Tool",
        "executable": "newtool_executable",
        "version_command": ["newtool", "--version"],
        "required_version": "1.0.0",
        "platforms": ["windows", "linux"],
        "installer": {
            "windows": {
                "type": "winget",
                "winget_id": "Publisher.NewTool"
            }
        }
    }
}
```

## Logging
Logs are automatically written to `logs/tool_manager.log`. This file records all tool detections, version checks, installation attempts, and any errors encountered during execution.

## Testing
The project includes a suite of automated tests using the standard `unittest` framework. Note: Tests are designed to mock system calls and will not actually modify your system or install software.

To run the tests:
```bash
python -m unittest discover -s tests -v
```

## Limitations
- **Windows-First**: While the architecture supports Linux package managers (like `apt`), testing has primarily been focused on Windows 10/11 using `winget`.
- **Privileges**: Automated installation via `winget` or `apt` may prompt for administrator/sudo privileges. The Tool Manager does not automatically elevate privileges; it relies on the system's native prompts.
- **Version Parsing**: Version output from different tools can vary wildly. The current regex-based approach handles standard semantic versioning but may need custom tweaks for tools with highly unconventional version strings.
