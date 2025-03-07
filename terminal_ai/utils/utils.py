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
from config import config

# Load command history (Persistent across sessions)
HISTORY_FILE = os.path.expanduser("~/.terminal_ai_history")

def show_loading_spinner(message="Processing..."):
    """Display a loading spinner while LLaMA is processing."""
    spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    sys.stdout.write(constants.COLORS["info"] + message + " ")
    sys.stdout.flush()

    while not config.stop_loading.is_set():
        sys.stdout.write(next(spinner) + " ")
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write("\b\b")  # Erase previous spinner


def load_history():
    """Load command history from a file."""
    if os.path.exists(HISTORY_FILE):
        readline.read_history_file(HISTORY_FILE)


def save_history():
    """Save command history to a file."""
    readline.write_history_file(HISTORY_FILE)


# Function to handle termination via Ctrl+D (exit the terminal)
def handle_exit_signal(signal, frame):
    print("\nExiting AI Terminal...")
    sys.exit(0)


# Function to handle interruption via Ctrl+C (terminate current running command)
def handle_interrupt_signal(signal, frame):
    global current_process
    if current_process:
        print("\nInterrupting the current command...")
        current_process.terminate()  # Kill the current running command
        current_process = None
    else:
        print("\nNo command is currently running to interrupt.")


def clean_markdown(content):
    """Remove or format markdown content for terminal display."""
    # Remove code blocks (backticks)
    content = re.sub(r'```(.*?)```', '', content, flags=re.DOTALL)

    # Remove inline code (single backticks)
    content = re.sub(r'`(.*?)`', r'\1', content)

    # Convert bold (**text**) to terminal-friendly format
    content = re.sub(r'\*\*(.*?)\*\*', r'\033[1m\1\033[0m', content)

    # Convert italics (*text*) to terminal-friendly format
    content = re.sub(r'\*(.*?)\*', r'\033[3m\1\033[0m', content)

    # Remove headers (###, ##, #)
    content = re.sub(r'^(#{1,6})\s*(.*?)\s*$', r'\2', content, flags=re.MULTILINE)

    # Remove links (markdown style)
    content = re.sub(r'\[.*?\]\(.*?\)', '', content)

    return content