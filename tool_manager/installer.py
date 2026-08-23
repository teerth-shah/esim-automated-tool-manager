"""Tool installation module for the eSim Tool Manager.

Handles downloading and installing supported tools using configured
installation methods (winget, download, package manager, manual).
"""

import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from tool_manager.detector import detect_tool
from tool_manager.models import InstallResult, ToolStatus
from tool_manager.platform_utils import get_os
from tool_manager.version_checker import get_installed_version

logger = logging.getLogger("tool_manager")


def _is_winget_available() -> bool:
    """Check whether winget is available on the system."""
    return shutil.which("winget") is not None


def _install_via_winget(winget_id: str, tool_name: str) -> bool:
    """Install a tool using Windows Package Manager (winget).

    Args:
        winget_id: The winget package identifier.
        tool_name: Human-readable tool name for logging.

    Returns:
        True if the winget command exited successfully.
    """
    logger.info("Installing %s via winget (ID: %s)", tool_name, winget_id)
    print(f"\nRunning: winget install --id {winget_id}")
    print("This may take several minutes...\n")

    try:
        result = subprocess.run(
            [
                "winget", "install",
                "--id", winget_id,
                "--accept-source-agreements",
                "--accept-package-agreements",
            ],
            capture_output=False,
            text=True,
            timeout=600,
        )
        if result.returncode == 0:
            logger.info("winget install completed successfully for %s", tool_name)
            return True
        else:
            logger.warning(
                "winget install returned code %d for %s",
                result.returncode, tool_name,
            )
            return False
    except subprocess.TimeoutExpired:
        logger.error("winget install timed out for %s", tool_name)
        print("ERROR: Installation timed out after 10 minutes.")
        return False
    except FileNotFoundError:
        logger.error("winget executable not found")
        print("ERROR: winget not found on this system.")
        return False
    except subprocess.SubprocessError as exc:
        logger.error("winget install failed for %s: %s", tool_name, exc)
        print(f"ERROR: Installation failed: {exc}")
        return False


def _install_via_download(installer_config: dict, tool_name: str) -> bool:
    """Handle download-based installation by providing instructions.

    For security, we do not automatically download and execute arbitrary
    binaries. Instead, we provide the download URL and instructions.

    Args:
        installer_config: The installer configuration dict.
        tool_name: Human-readable tool name.

    Returns:
        True (the user is given instructions to proceed manually).
    """
    url = installer_config.get("url", "")
    instructions = installer_config.get("instructions", "")

    print(f"\n--- Manual Download Required for {tool_name} ---")
    if url:
        print(f"Download URL: {url}")
    if instructions:
        print(f"Instructions: {instructions}")
    print("---")
    print("\nAfter installing manually, run 'Verify Tool' to confirm.")
    logger.info(
        "Provided manual download instructions for %s (URL: %s)",
        tool_name, url,
    )
    return True


def _install_via_package_manager(installer_config: dict, tool_name: str) -> bool:
    """Install a tool using a system package manager (Linux apt, etc.).

    Args:
        installer_config: The installer configuration dict.
        tool_name: Human-readable tool name.

    Returns:
        True if installation command succeeded.
    """
    command = installer_config.get("command", [])
    if not command:
        logger.error("No package manager command configured for %s", tool_name)
        print("ERROR: No installation command configured.")
        return False

    logger.info("Installing %s via package manager: %s", tool_name, " ".join(command))
    print(f"\nRunning: {' '.join(command)}")
    print("This may require administrator privileges.\n")

    try:
        result = subprocess.run(
            command,
            capture_output=False,
            text=True,
            timeout=300,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        logger.error("Package manager install timed out for %s", tool_name)
        print("ERROR: Installation timed out.")
        return False
    except FileNotFoundError:
        logger.error("Package manager command not found for %s", tool_name)
        print("ERROR: Package manager not found on this system.")
        return False
    except subprocess.SubprocessError as exc:
        logger.error("Package manager install failed for %s: %s", tool_name, exc)
        print(f"ERROR: Installation failed: {exc}")
        return False


def install_tool(tool_config: dict, key: str = "Unknown") -> InstallResult:
    """Install a single tool according to its configuration.

    The installation flow:
    1. Check if the tool is already installed.
    2. Determine the appropriate installer for the current platform.
    3. Ask the user for confirmation.
    4. Execute the installation.
    5. Verify the installation.

    Args:
        tool_config: Configuration dict for the tool from tools.json.
        key: The key identifier for the tool.

    Returns:
        InstallResult with success status and details.
    """
    tool_name = tool_config.get("display_name", key)
    logger.info("Starting installation process for %s", tool_name)

    # Step 1: Check if already installed
    detection = detect_tool(tool_config)
    if detection.found:
        version = get_installed_version(tool_config)
        msg = f"{tool_name} is already installed"
        if version:
            msg += f" (version {version})"
        if detection.path:
            msg += f" at {detection.path}"
        logger.info(msg)
        print(f"\n{msg}")
        return InstallResult(
            tool_name=tool_name,
            success=True,
            message=msg,
            version_after=version,
        )

    # Step 2: Determine platform and installer
    current_os = get_os()
    installer_config_all = tool_config.get("installer", {})
    installer_config = installer_config_all.get(current_os)

    if not installer_config:
        msg = f"No installer configured for {tool_name} on {current_os}."
        logger.warning(msg)
        print(f"\n{msg}")
        return InstallResult(
            tool_name=tool_name,
            success=False,
            message=msg,
            version_after=None,
        )

    install_type = installer_config.get("type", "manual")

    # Step 3: Show what will happen and ask for confirmation
    print(f"\n--- Install {tool_name} ---")
    print(f"Platform: {current_os}")
    print(f"Method: {install_type}")
    if installer_config.get("instructions"):
        print(f"Details: {installer_config['instructions']}")

    if install_type == "manual":
        _install_via_download(installer_config, tool_name)
        return InstallResult(
            tool_name=tool_name,
            success=False,
            message=f"Manual installation required for {tool_name}. Instructions provided.",
            version_after=None,
        )

    # For automated installs, confirm with user
    print("\nThis will modify your system by installing software.")
    if install_type == "winget":
        if not _is_winget_available():
            msg = "winget is not available. Cannot install automatically."
            logger.error(msg)
            print(f"\nERROR: {msg}")
            # Fall back to showing manual instructions
            _install_via_download(installer_config, tool_name)
            return InstallResult(
                tool_name=tool_name,
                success=False,
                message=msg,
                version_after=None,
            )

    try:
        confirm = input("Proceed with installation? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        confirm = "n"

    if confirm != "y":
        msg = f"Installation of {tool_name} cancelled by user."
        logger.info(msg)
        print(f"\n{msg}")
        return InstallResult(
            tool_name=tool_name,
            success=False,
            message=msg,
            version_after=None,
        )

    # Step 4: Execute installation
    logger.info("User confirmed installation of %s via %s", tool_name, install_type)
    success = False

    if install_type == "winget":
        winget_id = installer_config.get("winget_id", "")
        if not winget_id:
            msg = f"No winget ID configured for {tool_name}."
            logger.error(msg)
            print(f"\nERROR: {msg}")
            return InstallResult(
                tool_name=tool_name, success=False,
                message=msg, version_after=None,
            )
        success = _install_via_winget(winget_id, tool_name)

    elif install_type == "download":
        success = _install_via_download(installer_config, tool_name)

    elif install_type == "package_manager":
        success = _install_via_package_manager(installer_config, tool_name)

    else:
        msg = f"Unknown installer type '{install_type}' for {tool_name}."
        logger.error(msg)
        print(f"\nERROR: {msg}")
        return InstallResult(
            tool_name=tool_name, success=False,
            message=msg, version_after=None,
        )

    # Step 5: Verify installation
    if success and install_type not in ("download", "manual"):
        print(f"\nVerifying {tool_name} installation...")
        verification = detect_tool(tool_config)
        version_after = get_installed_version(tool_config) if verification.found else None

        if verification.found:
            msg = f"{tool_name} installed and verified successfully."
            if version_after:
                msg += f" Version: {version_after}"
            if verification.path:
                msg += f" Path: {verification.path}"
            logger.info(msg)
            print(f"\n{msg}")
            return InstallResult(
                tool_name=tool_name,
                success=True,
                message=msg,
                version_after=version_after,
            )
        else:
            msg = (
                f"{tool_name} installation command completed, "
                "but verification could not find the executable. "
                "You may need to restart your terminal or add the tool to PATH."
            )
            logger.warning(msg)
            print(f"\nWARNING: {msg}")
            return InstallResult(
                tool_name=tool_name,
                success=False,
                message=msg,
                version_after=None,
            )

    if not success:
        msg = f"Installation of {tool_name} did not complete successfully."
        logger.error(msg)
        print(f"\n{msg}")

    return InstallResult(
        tool_name=tool_name,
        success=success,
        message=f"{'Installation completed' if success else 'Installation failed'} for {tool_name}.",
        version_after=None,
    )


def get_installable_tools(config: dict) -> list[dict]:
    """Return a list of tools that have installer configurations for the current platform.

    Args:
        config: The full tools configuration dict.

    Returns:
        List of (key, tool_config) tuples for tools with available installers.
    """
    current_os = get_os()
    installable = []
    for key, tool_config in config.items():
        installer = tool_config.get("installer", {})
        if current_os in installer:
            installable.append((key, tool_config))
    return installable
