"""Tool detection module for eSim Automated Tool Manager."""

import logging
import os
import shutil
from pathlib import Path
from typing import Optional, Union

from tool_manager.models import DetectionResult, ToolStatus
from tool_manager.platform_utils import get_os

logger = logging.getLogger("tool_manager")


def detect_tool(tool_config: dict) -> DetectionResult:
    """Detect whether a specified tool is installed on the system.

    Searches the system PATH using shutil.which for the configured executable.
    If not found on PATH, checks any additional candidate paths specified
    in the tool configuration.

    Args:
        tool_config: Dictionary containing tool configuration details,
            including 'name', 'executable', and optional 'additional_paths'.

    Returns:
        DetectionResult containing tool name, found status, path, and ToolStatus.
    """
    tool_name = tool_config.get("display_name", "Unknown")
    executable = tool_config.get("command")

    try:
        if not executable:
            logger.warning("No executable specified for tool '%s'", tool_name)
            return DetectionResult(
                tool_name=tool_name,
                found=False,
                path=None,
                status=ToolStatus.MISSING,
            )

        # 1. Check system PATH via shutil.which
        found_path = shutil.which(executable)
        if found_path:
            resolved_path = str(Path(found_path).resolve())
            logger.debug("Tool '%s' found in PATH: %s", tool_name, resolved_path)
            return DetectionResult(
                tool_name=tool_name,
                found=True,
                path=resolved_path,
                status=ToolStatus.INSTALLED,
            )

        # 2. Check additional candidate paths if provided
        additional_paths = tool_config.get("additional_paths")
        candidate_paths: list[str] = []

        if isinstance(additional_paths, list):
            candidate_paths.extend(str(p) for p in additional_paths)
        elif isinstance(additional_paths, dict):
            current_os = get_os()
            os_paths = additional_paths.get(current_os, [])
            if isinstance(os_paths, list):
                candidate_paths.extend(str(p) for p in os_paths)
            elif isinstance(os_paths, str):
                candidate_paths.append(os_paths)

        for raw_path in candidate_paths:
            expanded = Path(os.path.expandvars(os.path.expanduser(raw_path)))
            if expanded.is_file():
                resolved_path = str(expanded.resolve())
                logger.debug(
                    "Tool '%s' found at candidate path: %s", tool_name, resolved_path
                )
                return DetectionResult(
                    tool_name=tool_name,
                    found=True,
                    path=resolved_path,
                    status=ToolStatus.INSTALLED,
                )
            if expanded.is_dir():
                direct_which = shutil.which(executable, path=str(expanded))
                if direct_which:
                    resolved_path = str(Path(direct_which).resolve())
                    logger.debug(
                        "Tool '%s' found in candidate directory %s: %s",
                        tool_name,
                        raw_path,
                        resolved_path,
                    )
                    return DetectionResult(
                        tool_name=tool_name,
                        found=True,
                        path=resolved_path,
                        status=ToolStatus.INSTALLED,
                    )
                direct_exec = expanded / executable
                if direct_exec.is_file():
                    resolved_path = str(direct_exec.resolve())
                    logger.debug("Tool '%s' found at %s", tool_name, resolved_path)
                    return DetectionResult(
                        tool_name=tool_name,
                        found=True,
                        path=resolved_path,
                        status=ToolStatus.INSTALLED,
                    )

        logger.debug("Tool '%s' was not found on the system", tool_name)
        return DetectionResult(
            tool_name=tool_name,
            found=False,
            path=None,
            status=ToolStatus.MISSING,
        )

    except Exception as exc:
        logger.error("Error during detection of tool '%s': %s", tool_name, exc)
        return DetectionResult(
            tool_name=tool_name,
            found=False,
            path=None,
            status=ToolStatus.ERROR,
        )


def detect_all_tools(config: dict) -> list[DetectionResult]:
    """Detect all configured tools.

    Iterates over all tool entries in the configuration dictionary, performs
    detection for each, and logs the result.

    Args:
        config: Configuration dictionary containing tool definitions.

    Returns:
        List of DetectionResult instances for all configured tools.
    """
    results: list[DetectionResult] = []
    if not isinstance(config, dict):
        logger.error("Invalid configuration format provided to detect_all_tools")
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
        result = detect_tool(tool_config)
        logger.info(
            "Detection - %s: status=%s, found=%s, path=%s",
            result.tool_name,
            result.status.value,
            result.found,
            result.path,
        )
        results.append(result)

    return results
