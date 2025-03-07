import os
import subprocess
import readline
import sys
from colorama import init, Fore, Style
import ollama
import re
import signal
import threading
import itertools
import time
from constants import constants

def check_dependency_installed(check_command):
    """Run the dependency check command and determine if dependencies are installed."""
    try:
        result = subprocess.run(check_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0  # Return True if dependencies are installed
    except subprocess.CalledProcessError:
        return False

def install_dependencies(install_command):
    """Install necessary dependencies."""
    try:
        subprocess.run(install_command, shell=True, check=True)
        print(constants.COLORS["success"] + "Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print(constants.COLORS["error"] + "Failed to install dependencies. Try manually.")


def execute_final_command(final_command):
    """Execute the final user command after confirming dependencies."""
    confirm = input(constants.COLORS["input"] + f"Do you want to execute the final command: {final_command}? (yes/no): ")

    if confirm.lower() == "yes":
        print(constants.COLORS["info"] + f"Executing: {final_command}")

        result = subprocess.run(final_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Print the command output
        if result.stdout:
            print(constants.COLORS["success"] + result.stdout)
        if result.stderr:
            print(constants.COLORS["error"] + result.stderr)

    else:
        print(constants.COLORS["warning"] + "Command execution aborted.")

def extract_commands(response):
    """Extract the check, install, and final command from LLaMA response."""
    check_cmd = response.split("check:")[-1].split("dependency:")[0].strip() if "check:" in response else None
    install_cmd = response.split("dependency:")[-1].split("command:")[0].strip() if "dependency:" in response else None
    final_cmd = response.split("command:")[-1].strip() if "command:" in response else None
    return check_cmd, install_cmd, final_cmd


import re


def is_dangerous_command(command, os_type):
    """
    Check if the provided command is potentially dangerous based on the OS.
    Returns True if the command matches any dangerous pattern.
    """
    dangerous_patterns = {
        "linux": [
            r"\brm\s+-rf\s+/\b",  # rm -rf /: Remove the root directory recursively
            r"\bsudo\s+rm\s+-rf\s+/\b",  # sudo rm -rf /: Same as above with sudo
            r"\bdd\s+if=.*of=/dev/sd[a-z]\b",  # dd writing directly to disk devices
            r"\bmkfs(\.\w+)?\b",  # Filesystem creation (formatting)
            r":\(\)\s*{:\|:&};:",  # Fork bomb pattern
            r"\bshutdown\s+-h\s+now\b",  # Immediate shutdown command
            r"\bfdisk\s+/dev/sd[a-z]\b",  # Direct disk manipulation using fdisk
            r"\bparted\s+/dev/sd[a-z]\b",  # Direct disk partitioning using parted
        ],
        "macos": [
            r"\brm\s+-rf\s+/\b",  # rm -rf /: Remove the root directory recursively
            r"\bsudo\s+rm\s+-rf\s+/\b",  # sudo rm -rf /: Same as above with sudo
            r"\bbrew\s+clean\s+all\b",  # brew clean all: Cleans Homebrew caches (can be destructive)
            r":\(\)\s*{:\|:&};:",  # Fork bomb pattern
            r"\bshutdown\s+-h\s+now\b",  # Immediate shutdown command
            r"\bfdisk\s+/dev/disk\d+\b",  # Disk manipulation on macOS using fdisk (if applicable)
            r"\bparted\s+/dev/disk\d+\b",  # Partition editor commands (if used)
        ],
        "windows": [
            r"\bDEL\s+/S\s+/Q\s+C:\\",  # Recursive delete command on drive C:
            r"\bformat\s+C:\b",  # Format drive C:
            r"\bshutdown\s+/s\b",  # Shutdown command
            r"\bPowerShell\s+Remove-Item\s+-Recurse\b",  # Potentially dangerous PowerShell deletion
        ]
    }

    patterns = dangerous_patterns.get(os_type, [])
    for pattern in patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False
