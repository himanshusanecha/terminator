import subprocess
import os
import readline
import sys
from colorama import init, Fore, Style
import ollama
import re
import signal
import threading
import itertools
import time
from utils import utils, command_utils
from model import inference
from constants import prompts, constants
from config import config

current_process = None

# Initialize Colorama for colored text output
init(autoreset=True)

# Register the exit and interrupt signal handlers
signal.signal(signal.SIGINT, utils.handle_interrupt_signal)  # Ctrl+C
signal.signal(signal.SIGQUIT, utils.handle_exit_signal)     # Ctrl+D

def run_terminal():
    
    utils.load_history()
    
    """Main function to handle terminal commands with NLP processing."""
    print(constants.COLORS["info"] + "Welcome to Terminal-AI! Type 'exit' to quit.")

    while True:
        prompt = f"{constants.COLORS['prompt']}➜ {os.getlogin()}@{os.uname().sysname}:~$ "
        user_input = input(prompt + constants.COLORS["input"])
        
        if user_input.lower() == "exit":
            print(constants.COLORS["info"] + "Exiting Terminal-AI...")
            break
        
        if user_input.strip():  # Avoid empty commands being saved
            readline.add_history(user_input)

        # Step 1: Try executing the command directly
        result = subprocess.run(user_input, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            print(constants.COLORS["success"] + result.stdout.decode())
            continue
        
        # Step 2: Ask LLaMA for the user's intent
        intent_prompt = prompts.INTENT_PROMPT.format(query=user_input)
        intent = inference.query_llama(intent_prompt)
        
        if not intent:
            print(constants.COLORS["error"] + "Failed to determine intent.")
            continue

        if intent.lower() == "execute":
            # Step 3: Get dependency check & installation commands
            dependency_prompt = prompts.DEPENDENCY_PROMPT.format(query=user_input, os=config.os)
            response = inference.query_llama(dependency_prompt)

            if not response:
                print(constants.COLORS["error"] + "Failed to retrieve dependency information.")
                continue

            check_command, install_command, final_command = command_utils.extract_commands(response)

            print(f"Missing dependencies: {install_command}")
            print(f"Check command: {check_command}")

            # Step 4: Check and install dependencies
            if check_command and not command_utils.check_dependency_installed(check_command) and install_command is not None and command_utils.is_dangerous_command(install_command, config.os) is False:
                print(constants.COLORS["warning"] + "Missing dependencies. Installing now...")
                command_utils.install_dependencies(install_command)

            # Step 5: Confirm and execute final command
            command_utils.execute_final_command(final_command)

    
        elif intent == "search":
            print(constants.COLORS["info"] + "Searching the web is not implemented yet.")

        elif intent == "edit":
            print(constants.COLORS["info"] + "Editing files is not implemented yet.")
        
        elif intent == "respond":
            inference.query_llama_stream(user_input)
        
        elif intent == "code": 
            code_prompt = prompts.CODE_PROMPT.format(query=user_input)
            response = inference.query_llama(code_prompt)

            if not response:
                print(constants.COLORS["error"] + "Failed to retrieve dependency information.")
                continue
            else: 
                print(constants.COLORS['success'] + response)
        
        else:
            print(constants.COLORS["error"] + "Invalid intent detected. Try again.")

if __name__ == "__main__":
    config.os = utils.get_os_type()
    run_terminal()
