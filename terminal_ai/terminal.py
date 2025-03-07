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

current_process = None

# Initialize Colorama for colored text output
init(autoreset=True)

# Color definitions for output
COLORS = {
    "success": Fore.GREEN,
    "error": Fore.RED,
    "info": Fore.CYAN,
    "warning": Fore.YELLOW,
    "input": Fore.MAGENTA,
    "prompt": Fore.WHITE + Style.BRIGHT,
}

# Load command history (Persistent across sessions)
HISTORY_FILE = os.path.expanduser("~/.terminal_ai_history")

# Register the exit and interrupt signal handlers
signal.signal(signal.SIGINT, handle_interrupt_signal)  # Ctrl+C
signal.signal(signal.SIGQUIT, handle_exit_signal)     # Ctrl+D

def run_terminal():
    
    utils.load_history()
    
    """Main function to handle terminal commands with NLP processing."""
    print(COLORS["info"] + "Welcome to Terminal-AI! Type 'exit' to quit.")

    while True:
        prompt = f"{COLORS['prompt']}➜ {os.getlogin()}@{os.uname().sysname}:~$ "
        user_input = input(prompt + COLORS["input"])
        
        if user_input.lower() == "exit":
            print(COLORS["info"] + "Exiting Terminal-AI...")
            break
        
        if user_input.strip():  # Avoid empty commands being saved
            readline.add_history(user_input)

        # Step 1: Try executing the command directly
        result = subprocess.run(user_input, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            print(COLORS["success"] + result.stdout.decode())
            continue
        
        # Step 2: Ask LLaMA for the user's intent
        intent_prompt = INTENT_PROMPT.format(query=user_input)
        intent = inference.query_llama(intent_prompt)
        
        if not intent:
            print(COLORS["error"] + "Failed to determine intent.")
            continue

        if intent.lower() == "execute":
            # Step 3: Get dependency check & installation commands
            dependency_prompt = DEPENDENCY_PROMPT.format(query=user_input)
            response = inference.query_llama(dependency_prompt)

            if not response:
                print(COLORS["error"] + "Failed to retrieve dependency information.")
                continue

            check_command, install_command, final_command = command_utils.extract_commands(response)

            print(f"Missing dependencies: {install_command}")
            print(f"Check command: {check_command}")
            # Step 4: Check and install dependencies
            if check_command and not command_utils.check_dependency_installed(check_command):
                print(COLORS["warning"] + "Missing dependencies. Installing now...")
                install_dependencies(install_command)

            # Step 5: Confirm and execute final command
            command_utils.execute_final_command(final_command)

    
        elif intent == "search":
            print(COLORS["info"] + "Searching the web is not implemented yet.")

        elif intent == "edit":
            print(COLORS["info"] + "Editing files is not implemented yet.")
        
        elif intent == "respond":
            query_llama_stream(user_input)
        
        elif intent == "code": 
            code_prompt = CODE_PROMPT.format(query=user_input)
            response = query_llama(code_prompt)

            if not response:
                print(COLORS["error"] + "Failed to retrieve dependency information.")
                continue
            else: 
                print(COLORS['success'] + response)
        
        else:
            print(COLORS["error"] + "Invalid intent detected. Try again.")

if __name__ == "__main__":
    run_terminal()
