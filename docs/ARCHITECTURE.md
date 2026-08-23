# System Architecture

The eSim Automated Tool Manager is designed as a modular, lightweight Python command-line utility. It strictly adheres to using the Python Standard Library to minimize dependencies and ensure maximum compatibility across different user environments.

## Directory Structure

```
esim-tool-manager/
├── main.py                     # Entry point and CLI UI
├── tool_manager/               # Core application logic
│   ├── __init__.py
│   ├── config.py               # JSON configuration loading and validation
│   ├── detector.py             # Tool discovery and path resolution
│   ├── installer.py            # Automated installation logic
│   ├── logger.py               # Centralized logging setup
│   ├── models.py               # Data classes and Enums (ToolStatus, etc.)
│   ├── platform_utils.py       # OS detection and platform abstraction
│   └── version_checker.py      # Version command execution and comparison
├── config/
│   └── tools.json              # Central tool registry
├── logs/
│   └── tool_manager.log        # Application logs
├── tests/                      # Unit tests
│   ├── test_config.py
│   ├── test_detector.py
│   ├── test_installer.py
│   └── test_version_checker.py
├── docs/                       # Project documentation
│   ├── ARCHITECTURE.md
│   └── DESIGN.md
├── requirements.txt            # Project dependencies
├── .gitignore
├── LICENSE
└── README.md
```

## Module Responsibilities

- **`main.py`**: Manages the user interface, displays the interactive menu, routes user selections to the appropriate `tool_manager` functions, and formats the output for the console.
- **`config.py`**: Reads `tools.json`, handles JSON parsing errors, and provides safe access methods to retrieve tool configurations.
- **`detector.py`**: Locates tool executables using `shutil.which`. If a tool isn't found in the standard system PATH, it checks secondary candidate paths defined in the configuration.
- **`version_checker.py`**: Executes the configured version commands via `subprocess`, parses the output using regex, and safely compares the extracted version against the required minimum version.
- **`installer.py`**: Handles the installation flow. It checks current status, determines the appropriate platform installer (`winget`, `apt`, or manual download), prompts the user for confirmation, executes the install, and finally verifies success by triggering the detector.
- **`platform_utils.py`**: Isolates all OS-specific checks (`platform.system()`) to ensure platform logic is not scattered throughout the codebase.
- **`models.py`**: Defines structured data types (`DetectionResult`, `VersionResult`, `InstallResult`, `ToolStatus`) to ensure consistent data flow between modules, eliminating reliance on unstructured dictionaries.

## Data Flow

1. **Initialization**: `main.py` initializes the logger (`logger.py`) and loads the configuration (`config.py`).
2. **User Action**: The user selects an action (e.g., "Check Versions").
3. **Execution**: `main.py` calls `check_all_versions` in `version_checker.py`.
4. **Resolution**: `version_checker.py` first calls `detector.py` to find the executable path.
5. **Subprocess**: If found, `version_checker.py` runs the command, parses the version, and compares it.
6. **Result**: A list of `VersionResult` objects is returned to `main.py`.
7. **Display**: `main.py` formats these objects into a human-readable status table.

## Configuration Flow

The entire system is driven by `config/tools.json`. This decouples the Tool Manager's logic from the specific tools it manages. Adding support for a new tool (like a new simulator) requires zero code changes; it only requires adding a new JSON block detailing its executable name, version command, and installation method.

## Subprocess Flow

System commands (like getting versions or running installers) are executed using the `subprocess` module.
- **Security**: Commands are passed as lists of arguments (e.g., `["ngspice", "--version"]`). `shell=True` is strictly avoided to prevent shell injection vulnerabilities.
- **Safety**: Timeouts are enforced to prevent hanging processes. Both `stdout` and `stderr` are captured, as different tools output version information to different streams.

## Error Handling Flow

The application is designed to be resilient.
- **Missing Tools**: A missing tool is a valid state, not an exception. It is handled gracefully and reported as `MISSING`.
- **Command Failures**: If a version command fails or returns a non-zero exit code, the error is caught, logged, and the version is marked as `VERSION_UNKNOWN`.
- **Invalid Config**: If `tools.json` is malformed, `config.py` catches the `JSONDecodeError`, logs it, and returns an empty configuration, allowing the application to start and report the issue rather than crashing.
