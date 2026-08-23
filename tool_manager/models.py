"""Data models and enums for eSim Tool Manager."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ToolStatus(Enum):
    """Enumeration of possible tool statuses."""

    INSTALLED = "INSTALLED"
    MISSING = "MISSING"
    UP_TO_DATE = "UP_TO_DATE"
    UPDATE_AVAILABLE = "UPDATE_AVAILABLE"
    VERSION_UNKNOWN = "VERSION_UNKNOWN"
    ERROR = "ERROR"


@dataclass
class DetectionResult:
    """Result of detecting a tool on the system."""

    tool_name: str
    found: bool
    path: Optional[str] = None
    status: ToolStatus = ToolStatus.MISSING


@dataclass
class VersionResult:
    """Result of checking a tool's installed version against requirements."""

    tool_name: str
    installed_version: Optional[str]
    required_version: Optional[str]
    status: ToolStatus
    message: str = ""


@dataclass
class InstallResult:
    """Result of an installation or update operation."""

    tool_name: str
    success: bool
    message: str
    version_after: Optional[str] = None

@dataclass
class VerificationResult:
    """Result of the detailed verification process."""
    
    tool_name: str
    executable_found: bool
    can_invoke: bool
    version_obtained: Optional[str]
    required_version: Optional[str]
    version_satisfies: bool
    message: str
