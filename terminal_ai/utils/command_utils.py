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
