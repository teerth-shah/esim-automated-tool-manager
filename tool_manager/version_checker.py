"""Version checking module for eSim Automated Tool Manager."""

import logging
import re
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Union

from tool_manager.detector import detect_tool
from tool_manager.models import ToolStatus, VersionResult

logger = logging.getLogger("tool_manager")

DEFAULT_VERSION_PATTERN = r"(\d+\.\d+[\.\d]*)"


def _parse_version_tuple(version_str: str) -> tuple[int, ...]:
    """Parse a version string into a tuple of integers.

    Splits the version string on '.' and converts each part to an integer.
    Falls back to 0 for non-numeric parts.

    Args:
        version_str: Version string to parse (e.g., '8.1.0').

    Returns:
        Tuple of integers.
    """
    if not version_str:
        return ()
    parts: list[int] = []
    for part in version_str.strip().split("."):
        try:
            parts.append(int(part.strip()))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def compare_versions(
    installed: Optional[str], required: Optional[str]
) -> ToolStatus:
    """Compare an installed version string against a required version string.

    Args:
        installed: The installed version string, or None if unknown/missing.
        required: The required minimum version string, or None/empty if unconstrained.

    Returns:
        ToolStatus.VERSION_UNKNOWN if installed is None.
        ToolStatus.INSTALLED if required is None or empty.
        ToolStatus.UP_TO_DATE if installed >= required.
        ToolStatus.UPDATE_AVAILABLE if installed < required.
    """
    if installed is None:
        return ToolStatus.VERSION_UNKNOWN

    if required is None or not str(required).strip():
        return ToolStatus.INSTALLED

    inst_str = str(installed).strip()
    req_str = str(required).strip()

    try:
        inst_tuple = _parse_version_tuple(inst_str)
        req_tuple = _parse_version_tuple(req_str)

        # Pad shorter tuple with trailing zeros for accurate comparison
        max_len = max(len(inst_tuple), len(req_tuple))
        inst_padded = inst_tuple + (0,) * (max_len - len(inst_tuple))
        req_padded = req_tuple + (0,) * (max_len - len(req_tuple))

        if inst_padded >= req_padded:
            return ToolStatus.UP_TO_DATE
        return ToolStatus.UPDATE_AVAILABLE
    except (ValueError, TypeError):
        # Fall back to lexicographical string comparison
        if inst_str >= req_str:
            return ToolStatus.UP_TO_DATE
        return ToolStatus.UPDATE_AVAILABLE


def get_installed_version(tool_config: dict) -> Optional[str]:
    """Execute the configured version command and extract the version string.

    Args:
        tool_config: Dictionary containing tool configuration details,
            specifically 'version_command' and optional 'version_pattern'.

    Returns:
        Extracted version string if found, otherwise None.
    """
    tool_name = tool_config.get("display_name", "Unknown")
    version_command = tool_config.get("version_command")

    if not version_command:
        logger.debug("No version_command defined for '%s'", tool_name)
        return None

    if isinstance(version_command, str):
        cmd = shlex.split(version_command)
    elif isinstance(version_command, list):
        cmd = [str(arg) for arg in version_command]
    else:
        logger.warning(
            "Invalid version_command format for '%s': %s", tool_name, type(version_command)
        )
        return None

    if not cmd:
        return None

    # If the executable path is provided in config or detected path, use it
    configured_path = tool_config.get("path")
    if configured_path and Path(configured_path).is_file():
        cmd[0] = configured_path
    elif not shutil.which(cmd[0]):
        detection = detect_tool(tool_config)
        if detection.found and detection.path:
            cmd[0] = detection.path

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
            shell=False,
            check=False,
        )
        combined_output = f"{proc.stdout or ''}\n{proc.stderr or ''}"
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as exc:
        logger.warning("Failed to run version command for '%s': %s", tool_name, exc)
        return None
    except Exception as exc:
        logger.error("Unexpected error executing version command for '%s': %s", tool_name, exc)
        return None

    pattern = tool_config.get("version_pattern") or DEFAULT_VERSION_PATTERN

    try:
        match = re.search(pattern, combined_output)
        if match:
            if match.groups():
                version_str = match.group(1).strip()
            else:
                version_str = match.group(0).strip()
            logger.debug("Extracted version for '%s': %s", tool_name, version_str)
            return version_str
    except re.error as exc:
        logger.error("Invalid regex pattern '%s' for '%s': %s", pattern, tool_name, exc)
        return None

    logger.debug("No version matched pattern '%s' in output for '%s'", pattern, tool_name)
    return None


def check_version(tool_config: dict) -> VersionResult:
    """Check the installed version of a tool against required version.

    Combines tool detection and version checking. Checks whether the tool
    is installed, retrieves its version, and compares it to required_version.

    Args:
        tool_config: Dictionary containing tool configuration details.

    Returns:
        VersionResult containing tool name, installed version, required version,
        status enum, and a summary message.
    """
    tool_name = tool_config.get("display_name", "Unknown")
    required_version = tool_config.get("required_version")

    try:
        detection = detect_tool(tool_config)
        if not detection.found:
            msg = f"{tool_name} is not installed"
            logger.info(
                "Version check - %s: %s (status=%s)",
                tool_name,
                msg,
                ToolStatus.MISSING.value,
            )
            return VersionResult(
                tool_name=tool_name,
                installed_version=None,
                required_version=required_version,
                status=ToolStatus.MISSING,
                message=msg,
            )

        cfg_with_path = dict(tool_config)
        if detection.path:
            cfg_with_path["path"] = detection.path

        installed_version = get_installed_version(cfg_with_path)
        status = compare_versions(installed_version, required_version)

        if status == ToolStatus.UP_TO_DATE:
            msg = f"{tool_name} is up to date ({installed_version})"
        elif status == ToolStatus.UPDATE_AVAILABLE:
            msg = (
                f"{tool_name} update available: installed {installed_version}, "
                f"required {required_version}"
            )
        elif status == ToolStatus.INSTALLED:
            msg = f"{tool_name} is installed ({installed_version})"
        elif status == ToolStatus.VERSION_UNKNOWN:
            msg = f"{tool_name} is installed, but version could not be determined"
        else:
            msg = f"{tool_name} status: {status.value}"

        logger.info(
            "Version check - %s: installed=%s, required=%s, status=%s",
            tool_name,
            installed_version,
            required_version,
            status.value,
        )

        return VersionResult(
            tool_name=tool_name,
            installed_version=installed_version,
            required_version=required_version,
            status=status,
            message=msg,
        )

    except Exception as exc:
        logger.error("Error checking version for '%s': %s", tool_name, exc)
        return VersionResult(
            tool_name=tool_name,
            installed_version=None,
            required_version=required_version,
            status=ToolStatus.ERROR,
            message=f"Error checking version for {tool_name}: {exc}",
        )


def check_all_versions(config: dict) -> list[VersionResult]:
    """Check versions for all tools defined in the configuration.

    Iterates over all tools in config, runs check_version for each,
    and returns a list of results.

    Args:
        config: Configuration dictionary containing tool definitions.

    Returns:
        List of VersionResult instances for all configured tools.
    """
    results: list[VersionResult] = []
    if not isinstance(config, dict):
        logger.error("Invalid configuration format provided to check_all_versions")
        return results

    tools = config.get("tools", config)
    tool_entries: list[dict] = []

    if isinstance(tools, dict):
        for key, entry in tools.items():
            if isinstance(entry, dict):
                if "display_name" not in entry:
                    entry = {**entry, "display_name": key}
                tool_entries.append(entry)
    elif isinstance(tools, list):
        for entry in tools:
            if isinstance(entry, dict):
                tool_entries.append(entry)

    for tool_config in tool_entries:
        result = check_version(tool_config)
        results.append(result)

    return results
