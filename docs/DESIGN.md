eSim Automated Tool Manager - Design Document

1. Introduction

eSim is an open-source EDA tool used for circuit design, simulation and PCB design. It uses some external tools such as Ngspice and KiCad.
The purpose of this project is to make a small Tool Manager that can help the user check these tools, check their versions, install missing tools and verify them. The project is developed as a Python command-line application for FOSSEE eSim Task 5.

2. Problem Statement

Setting up the tools required by eSim can be difficult for a new user. The user may have to check whether a tool is installed, find its version and install it if it is missing.
Doing these steps manually can also lead to problems such as wrong versions or incorrect tool paths.
This project tries to put these operations in one place so that the user can manage the required tools from a simple interface.

3. Objectives
The main objectives of the project are:

Check whether the required tools are installed.
Check the installed version of a tool.
Identify tools that are missing or have an incorrect version.
Provide an option to install a required tool.
Verify a tool after installation.
Show the current status of the tools.
Keep logs of important operations and errors.
Provide a simple command-line interface for the user.

4. Proposed Solution
The proposed solution is a Python-based command-line Tool Manager.

The application uses a configuration file to store information about the tools that need to be managed. This keeps the tool information separate from the main program and makes it easier to add or update tools later.
When the program starts, it shows basic system information and then provides a menu to the user.

The current menu contains:
1. Check Tools
2. Check Versions
3. Install Tool
4. Verify Tool
5. Show Status
6. View Logs
7. Exit

The user can select the required operation from this menu.

5. System Architecture

The project is divided into different parts so that each part has a specific responsibility.

                  main.py
                     |
                     v
              Command Line Menu
                     |
        +------------+------------+
        |            |            |
        v            v            v
     Detector   Version Checker  Installer
        |            |            |
        +------------+------------+
                     |
                     v
                  Verifier
                     |
                     v
                   Logger

The main program handles the user interface, while the other modules perform the actual tool management operations.

6. Module Description

6.1 Detector

The detector checks whether a configured tool is available on the system. It can search for the executable using the system PATH and configured locations.

6.2 Version Checker

The version checker runs the required command for a tool and reads its output to find the installed version. It then compares the installed version with the required version.

6.3 Installer

The installer handles the installation of a missing tool. On Windows, the project can use the Windows Package Manager (winget) where it is configured and available.

The installation process may require confirmation or permissions from the user.

6.4 Verifier

The verifier checks the tool after installation. It confirms that the executable can be found and that the tool can be run successfully. It also checks the version when version information is available.

6.5 Logger

The logger records important events, errors and operations performed by the Tool Manager. These logs can help when troubleshooting a problem.

6.6 Configuration

The configuration part loads the tool information used by the application. Keeping this information separately makes it easier to add or modify tools without changing the complete program.

7. Workflow

The general workflow of the application is:

Start
  |
  v
Load configuration
  |
  v
Show system information
  |
  v
Show main menu
  |
  +----> Check Tools
  |
  +----> Check Versions
  |
  +----> Install Tool
  |
  +----> Verify Tool
  |
  +----> Show Status
  |
  +----> View Logs
  |
  +----> Exit

Check Tools

The application checks the configured tools and shows whether they are installed or missing.

Check Versions

The application checks the installed version and compares it with the required version.

Install Tool

The user selects a tool and the application starts the configured installation process.

Verify Tool

The application checks the selected tool again to make sure that it is available and working after installation.

Show Status

This option gives the user a quick view of the current state of the configured tools.

View Logs

This option allows the user to see previous operations and error information recorded by the application.

8. Technologies Used

Python

Python Standard Library

Command Line Interface

JSON configuration

Windows Package Manager (winget) where supported

Git

GitHub

Windows

Python was used because it provides useful built-in modules for running system commands, checking files and paths, handling configuration files and creating logs.

9. Implementation

The project is divided into separate modules instead of putting all the code in main.py.

The main program handles the menu and user input. The tool management modules perform detection, version checking, installation and verification.

The configuration is kept separately so that tool details can be changed without changing the complete application.

The project also contains a test directory for checking important parts of the application.

10. Testing

The application was tested by running:

python main.py

The program starts successfully and displays the system information and main menu.

The different menu options can then be tested individually, including tool detection, version checking, installation, verification, status checking and log viewing.

The project also contains tests for important parts of the Tool Manager. System operations can be tested without changing the actual system by using mocked system calls where required.

11. Project Structure

The repository is organized as follows:

esim-automated-tool-manager/
|
├── config/
├── docs/
├── tests/
├── tool_manager/
|
├── .gitignore
├── LICENSE
├── README.md
├── main.py
└── requirements.txt

The docs directory contains the project documentation and the tests directory contains the test files.

12. Limitations

The current version is a prototype, so there are some limitations:

The command-line interface is currently the main user interface.

Automatic installation depends on the operating system and available package manager.

The current installation flow is mainly intended for Windows.

Version checking depends on the output provided by the installed tool.

Administrator permissions may be required for some installations.

More tools and operating systems can be supported in future versions.

13. Future Improvements
The project can be improved further by:

Adding support for more eSim-related tools.
Adding better support for Linux and other operating systems.
Improving error messages and installation handling.
Adding dependency relationships between tools.
Adding more automated tests.
Improving the log and status reports.
Adding a graphical interface in the future if required.

15. Conclusion

The eSim Automated Tool Manager is a prototype for making the setup and checking of eSim-related tools easier.

The current application provides a simple command-line interface with options for checking tools, checking versions, installing tools, verifying tools, viewing status and viewing logs.

The project is divided into separate modules so that it can be maintained and extended more easily. The current implementation provides a base that can be improved with more tools, better cross-platform support and additional automation in the future.
