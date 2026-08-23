# eSim Automated Tool Manager - Design Document

## 1. Introduction
eSim is an open-source EDA tool for circuit design, simulation, analysis, and PCB design. It integrates several external tools and libraries (such as Ngspice and KiCad) to provide a seamless environment for engineers. This project is a standalone utility designed to automate the management of these external dependencies.

## 2. Problem Statement
Managing eSim's external tools manually is tedious and error-prone. Users frequently encounter issues with compatibility, path configuration, and missing dependencies, which can cause the main eSim software to fail. There is a need for an automated system that handles installation, updates, and configuration checks with minimal manual intervention.

## 3. Objectives
*   Provide a unified interface to manage eSim dependencies.
*   Automatically detect installed tools and their locations on the system.
*   Check installed tool versions against known required versions.
*   Automate the installation of missing tools safely.
*   Verify tools post-installation to ensure they function correctly.

## 4. Proposed Solution
The proposed solution is a modular, Python-based Command Line Interface (CLI) application. It is entirely data-driven, using a central JSON configuration file (`tools.json`) to define tool metadata. This ensures the application can scale to support new tools in the future without requiring core code changes.

## 5. System Architecture
The application uses a layered architecture to separate concerns:
*   **Presentation Layer**: The CLI menu system that interacts with the user.
*   **Business Logic Layer**: A suite of independent modules handling detection, version comparison, installation, and verification.
*   **Data Layer**: Configuration management parsing the JSON tool registry.

## 6. Module Description
The core logic is divided into the following specialized modules:

*   **Detector (`detector.py`)**: Responsible for locating tool executables on the system. It primarily utilizes the system PATH (via `shutil.which`) but can fallback to specific candidate paths defined in the configuration.
*   **Version Checker (`version_checker.py`)**: Executes tools via secure subprocess calls, captures standard output and error streams, and extracts semantic version strings using regular expressions. It converts these strings into integer tuples for safe mathematical comparison.
*   **Installer (`installer.py`)**: Manages the installation flow. It detects the host OS, selects the appropriate installation backend (e.g., `winget` for Windows), prompts the user for confirmation, and executes the installation.
*   **Verifier (`verifier.py`)**: Performs a deep health check on a tool. It confirms the executable exists, can be successfully invoked, and perfectly satisfies the required version constraint.
*   **Logger (`logger.py`)**: Implements centralized logging using Python's built-in `logging` module, writing audit trails to `logs/tool_manager.log` for debugging and transparency.
*   **Configuration (`config.py`)**: Loads, parses, and validates the `tools.json` registry. It handles missing or malformed JSON files gracefully to prevent application crashes.

## 7. Workflow
1.  **Initialization**: The application starts, initializes the logger, and parses `tools.json`.
2.  **User Interaction**: The user is presented with a 1-7 menu options (Check Tools, Check Versions, Install Tool, etc.).
3.  **Routing**: The user's choice routes to the appropriate module (e.g., Option 3 routes to the Installer).
4.  **Execution**: The module performs system-level checks (finding files, running subprocesses).
5.  **Output**: The module returns structured data classes back to the main UI, which formats them into clean ASCII tables or reports for the user.

## 8. Technologies Used
*   **Language**: Python 3.8+
*   **Libraries**: Python Standard Library only (`subprocess`, `shutil`, `json`, `pathlib`, `logging`, `unittest`). No external dependencies are required for the core application, ensuring maximum portability.
*   **Data Format**: JSON for tool registry.
*   **Package Managers**: Integrates with `winget` (Windows Package Manager).

## 9. Implementation
The project is implemented with strict modularity. Data models (`DetectionResult`, `VersionResult`, `InstallResult`, `VerificationResult`) are used to pass information between modules reliably, avoiding the use of unstructured dictionaries. The CLI is kept completely separate from the system interaction logic.

## 10. Testing
The application uses the built-in `unittest` framework. Tests are designed to mock system calls (like `shutil.which` or `subprocess.run`) to verify the internal logic, version comparison algorithms, and configuration validation without actually modifying the host operating system.

## 11. Limitations
*   **OS Dependency**: Automated installation is currently optimized and tested for Windows using `winget`. Linux `apt` commands are structured but untested.
*   **Output Parsing**: Version checking relies on parsing console output. If a tool radically changes its output format in a future update, the regex patterns in the JSON configuration will need to be updated.
*   **Privileges**: The tool cannot automatically elevate its own privileges. If `winget` requires Administrator access, the user must approve the native Windows UAC prompt manually.

## 12. Future Improvements
*   **Graphical User Interface (GUI)**: Implement a frontend using `tkinter` or `PyQt` for users who prefer visual management over a CLI.
*   **Dependency Resolution**: Add capability in the JSON config to declare that Tool A depends on Tool B, ensuring they install in the correct order.
*   **Cross-Platform Expansion**: Full verification and testing of the Linux/macOS installation backends.

## 13. Conclusion
The eSim Automated Tool Manager successfully fulfills the requirements of automating the discovery, verification, and installation of external dependencies. By maintaining a clean architecture and relying strictly on the Python Standard Library, it provides a lightweight, resilient, and extensible solution for eSim users.
