"""Platform utility functions for eSim Tool Manager."""

import platform


def get_os() -> str:
    """Return normalized operating system name ('windows', 'linux', or 'unknown')."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    if system == "linux":
        return "linux"
    return "unknown"


def is_windows() -> bool:
    """Check if the current operating system is Windows."""
    return get_os() == "windows"


def is_linux() -> bool:
    """Check if the current operating system is Linux."""
    return get_os() == "linux"


def is_supported() -> bool:
    """Check if the current operating system is supported (Windows or Linux)."""
    return get_os() in ("windows", "linux")


def get_python_version() -> str:
    """Return the current Python version string."""
    return platform.python_version()


def get_system_info() -> dict[str, str]:
    """Return a dictionary containing system and runtime information."""
    return {
        "os": get_os(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "python_version": get_python_version(),
    }
