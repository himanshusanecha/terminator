import threading
from terminal_ai.utils import utils
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
from terminal_ai.constants import constants
from terminal_ai.config import config

def query_llama(prompt):
    """Send a request to LLaMA via Ollama and return the response."""
    config.stop_loading = threading.Event()
    loading_thread = threading.Thread(target=utils.show_loading_spinner, args=("Querying LLaMA...",))
    loading_thread.start()

    try:
        response = ollama.chat(model="llama3.2:3b", messages=[{"role": "user", "content": prompt}])
        return response.get('message', {}).get('content', '').strip()
    except Exception as e:
        print(constants.COLORS["error"] + f"Error querying LLaMA: {str(e)}")
        return None
    finally:
        config.stop_loading.set()
        loading_thread.join()
        sys.stdout.write("\n")  # Move to the next line
        sys.stdout.flush()


def query_llama_stream(prompt):
    """Send a request to LLaMA via Ollama and stream the response, formatting markdown for the terminal."""
    try:
        # Start the chat request with streaming enabled
        stream_response = ollama.chat(model="llama3.2:3b", messages=[{"role": "user", "content": prompt}], stream=True)

        # Iterate through the response and print it as it's received
        for chunk in stream_response:
            content = chunk.get('message', {}).get('content', '').strip()
            if content:
                formatted_content = utils.clean_markdown(content)  # Clean markdown for terminal
                print(constants.COLORS["success"] + formatted_content + " ", end='',
                      flush=True)  # Print each chunk as it's received

        # Return the final response content (optional, or you can return after finishing streaming)
        print()  # Ensures a newline after the stream is completed
        return "Streaming completed."

    except Exception as e:
        print(constants.COLORS["error"] + f"Error querying LLaMA: {str(e)}")
        return None

    except Exception as e:
        print(constants.COLORS["error"] + f"Error querying LLaMA: {str(e)}")
        return None
