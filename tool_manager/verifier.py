"""Verification module for eSim Automated Tool Manager."""

import logging
from tool_manager.models import VerificationResult, ToolStatus
from tool_manager.detector import detect_tool
from tool_manager.version_checker import get_installed_version, compare_versions

logger = logging.getLogger("tool_manager")

def verify_tool(tool_config: dict) -> VerificationResult:
    """Verifies a tool's installation thoroughly.
    
    Checks:
    1. Executable exists
    2. Executable can be invoked
    3. Version can be obtained
    4. Version satisfies requirement
    """
    tool_name = tool_config.get("display_name", "Unknown")
    required_version = tool_config.get("required_version")
    
    logger.info("Starting verification for %s", tool_name)
    
    # 1. Executable exists
    detection = detect_tool(tool_config)
    executable_found = detection.found
    
    can_invoke = False
    version_obtained = None
    version_satisfies = False
    message = ""
    
    if executable_found:
        # 2 & 3. Invoke & get version
        version_obtained = get_installed_version(tool_config)
        if version_obtained:
            can_invoke = True
            
            # 4. Check version satisfaction
            status = compare_versions(version_obtained, required_version)
            if status == ToolStatus.UP_TO_DATE or status == ToolStatus.INSTALLED:
                version_satisfies = True
                message = "VERIFIED SUCCESSFULLY"
            else:
                version_satisfies = False
                message = f"VERIFICATION FAILED: Version {version_obtained} does not meet requirement {required_version}"
        else:
            can_invoke = False
            message = "VERIFICATION FAILED: Executable found but could not invoke version command"
    else:
        message = "VERIFICATION FAILED: Executable not found"
        
    logger.info("Verification result for %s: %s", tool_name, message)
    
    return VerificationResult(
        tool_name=tool_name,
        executable_found=executable_found,
        can_invoke=can_invoke,
        version_obtained=version_obtained,
        required_version=required_version,
        version_satisfies=version_satisfies,
        message=message
    )
