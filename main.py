"""eSim Automated Tool Manager — CLI Entry Point."""

import sys
import os
from pathlib import Path

from tool_manager.config import load_config, get_all_tool_names
from tool_manager.detector import detect_all_tools
from tool_manager.installer import install_tool, get_installable_tools
from tool_manager.logger import setup_logger, get_logger
from tool_manager.models import ToolStatus
from tool_manager.platform_utils import get_os, get_system_info
from tool_manager.version_checker import check_all_versions
from tool_manager.verifier import verify_tool

BANNER = """========================================
eSim TOOL MANAGER
================="""

MENU = """
1. Check Tools
2. Check Versions
3. Install Tool
4. Verify Tool
5. Show Status
6. View Logs
7. Exit
"""

def display_menu() -> None:
    print(BANNER)
    print(MENU)

def get_user_choice() -> str:
    try:
        return input("Select an option: ").strip()
    except (EOFError, KeyboardInterrupt):
        return "7"

def action_check_tools(config: dict) -> None:
    logger = get_logger()
    logger.info("User selected: Check Tools")
    print("\n--- TOOL DETECTION ---\n")
    results = detect_all_tools(config)
    for result in results:
        status_str = "YES" if result.found else "NO"
        print(f"{result.tool_name}")
        print(f"Installed: {status_str}\n")

def action_check_versions(config: dict) -> None:
    logger = get_logger()
    logger.info("User selected: Check Versions")
    print("\n--- VERSION CHECK ---\n")
    results = check_all_versions(config)
    for result in results:
        print(f"{result.tool_name}")
        installed = result.installed_version or "--"
        required = result.required_version or "--"
        print(f"Installed Version: {installed}")
        print(f"Required Version: {required}")
        print(f"Status: {result.status.value}\n")

def action_install_tool(config: dict) -> None:
    logger = get_logger()
    logger.info("User selected: Install Tool")
    print("\n--- INSTALL TOOL ---\n")
    
    installable = get_installable_tools(config)
    if not installable:
        print("Automatic installation is not available for this platform.")
        print("Please follow the documented installation instructions.")
        logger.warning("No installable tools found for OS")
        return

    print("Available tools:\n")
    for i, (key, tool_config) in enumerate(installable, 1):
        name = tool_config.get("display_name", key)
        print(f"{i}. {name}")
    print("0. Cancel\n")

    try:
        choice = input("Select tool: ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    if choice == "0":
        return
    try:
        index = int(choice) - 1
        if index < 0 or index >= len(installable):
            print("\nInvalid selection.")
            return
    except ValueError:
        print("\nInvalid input.")
        return

    key, tool_config = installable[index]
    
    # Exact Install Sequence from Step 6
    install_result = install_tool(tool_config, key)
    
    # Run Verifier right after installation
    if install_result.success:
        print("\nVerifying installation...\n")
        v_res = verify_tool(tool_config)
        print("SUCCESS")
        print(f"{install_result.tool_name} installed successfully.")
        print(f"Installed Version: {v_res.version_obtained or '--'}")

def action_verify_tool(config: dict) -> None:
    logger = get_logger()
    logger.info("User selected: Verify Tool")
    print("\n--- VERIFICATION ---\n")
    
    tool_names = get_all_tool_names(config)
    for i, name in enumerate(tool_names, 1):
        display_name = config[name].get("display_name", name)
        print(f"{i}. {display_name}")
    print("0. Cancel\n")
    
    try:
        choice = input("Select a tool to verify: ").strip()
    except:
        return
    if choice == "0":
        return
    try:
        index = int(choice) - 1
        key = tool_names[index]
    except:
        return

    tool_config = config[key]
    result = verify_tool(tool_config)
    
    print(f"\nTool: {result.tool_name}\n")
    print(f"Executable: {'FOUND' if result.executable_found else 'NOT FOUND'}")
    print(f"Executable Test: {'PASSED' if result.can_invoke else 'FAILED'}")
    print(f"Version: {result.version_obtained or '--'}")
    print(f"Required Version: {result.required_version or '--'}\n")
    
    if result.version_satisfies:
        print("Result: VERIFIED SUCCESSFULLY")
    else:
        print("Result: VERIFICATION FAILED")
        print(f"Reason: {result.message}")

def action_show_status(config: dict) -> None:
    logger = get_logger()
    logger.info("User selected: Show Status")
    
    version_results = check_all_versions(config)
    
    print("\n========================================")
    print("eSim TOOL MANAGER STATUS")
    print("========================")
    print()
    print(f"{'Tool':<15} {'Version':<13} {'Required':<13} {'Status'}")
    print("-" * 55)
    
    ok_count = 0
    missing_count = 0
    
    for vr in version_results:
        display_status = "OK" if vr.status in (ToolStatus.UP_TO_DATE, ToolStatus.INSTALLED) else vr.status.value
        
        if display_status == "OK":
            ok_count += 1
        else:
            missing_count += 1
            if display_status == ToolStatus.MISSING.value:
                display_status = "MISSING"
            
        ver_str = vr.installed_version or "--"
        req_str = vr.required_version or "--"
        print(f"{vr.tool_name:<15} {ver_str:<13} {req_str:<13} {display_status}")
    
    print("-" * 55)
    print(f"Summary: {ok_count} OK | {missing_count} Missing\n")

def action_view_logs() -> None:
    logger = get_logger()
    logger.info("User selected: View Logs")
    log_path = Path("logs") / "tool_manager.log"
    print(f"\n--- LOGS: {log_path} ---\n")
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            print("".join(f.readlines()[-30:]))
    except Exception as e:
        print(f"Could not read logs: {e}")

def main() -> None:
    logger = setup_logger()
    logger.info("Program start")
    
    config = load_config()
    
    while True:
        display_menu()
        choice = get_user_choice()
        
        try:
            if choice == "1":
                action_check_tools(config)
            elif choice == "2":
                action_check_versions(config)
            elif choice == "3":
                action_install_tool(config)
            elif choice == "4":
                action_verify_tool(config)
            elif choice == "5":
                action_show_status(config)
            elif choice == "6":
                action_view_logs()
            elif choice == "7":
                print("\nExiting...")
                sys.exit(0)
            else:
                print("\nInvalid option. Please enter 1-7.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"\nERROR: An unexpected error occurred: {e}")
            print("Please check the logs for details.")

if __name__ == "__main__":
    main()
