"""Configuration loader and validator for eSim Tool Manager."""

import json
from pathlib import Path
from typing import Optional, Union

from tool_manager.logger import get_logger

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config" / "tools.json"
REQUIRED_TOOL_KEYS = {"display_name", "command", "version_command", "platforms"}


def load_config(config_path: Optional[Union[Path, str]] = None) -> dict:
    """Load tool configuration from a JSON file.

    Args:
        config_path: Optional path to the configuration file.
            Defaults to DEFAULT_CONFIG_PATH.

    Returns:
        Configuration dictionary, or an empty dict if loading fails.
    """
    logger = get_logger()
    target_path = Path(config_path) if config_path is not None else DEFAULT_CONFIG_PATH

    try:
        with open(target_path, "r", encoding="utf-8") as config_file:
            data = json.load(config_file)
            if not isinstance(data, dict):
                logger.error(f"Configuration file at {target_path} is not a JSON object")
                return {}
            return data
    except FileNotFoundError:
        logger.warning(f"Configuration file not found: {target_path}")
        return {}
    except json.JSONDecodeError as exc:
        logger.error(f"Invalid JSON in configuration file {target_path}: {exc}")
        return {}
    except Exception as exc:
        logger.error(f"Unexpected error reading configuration file {target_path}: {exc}")
        return {}


def get_tool_config(config: dict, tool_name: str) -> Optional[dict]:
    """Return configuration for a specific tool, or None if not found.

    Args:
        config: Loaded configuration dictionary.
        tool_name: Name of the tool to retrieve.

    Returns:
        Tool configuration dict or None.
    """
    if not isinstance(config, dict):
        return None

    tools = config.get("tools", config)
    if isinstance(tools, dict):
        tool = tools.get(tool_name)
        return tool if isinstance(tool, dict) else None

    if isinstance(tools, list):
        for entry in tools:
            if isinstance(entry, dict) and entry.get("name") == tool_name:
                return entry

    return None


def get_all_tool_names(config: dict) -> list[str]:
    """Return a list of tool names found in the configuration.

    Args:
        config: Loaded configuration dictionary.

    Returns:
        List of tool name strings.
    """
    if not isinstance(config, dict):
        return []

    tools = config.get("tools", config)
    if isinstance(tools, dict):
        return list(tools.keys())

    if isinstance(tools, list):
        return [
            entry["name"]
            for entry in tools
            if isinstance(entry, dict) and "name" in entry
        ]

    return []


def validate_tool_entry(entry: dict) -> bool:
    """Check that required keys exist in a tool configuration entry.

    Args:
        entry: Tool configuration entry dictionary.

    Returns:
        True if all required keys are present, False otherwise.
    """
    if not isinstance(entry, dict):
        return False
    return REQUIRED_TOOL_KEYS.issubset(entry.keys())
