from setuptools import setup, find_packages
import subprocess

def pull_default_model():
    try:
        subprocess.run(["ollama", "pull", "llama3.2:3b"], check=True)
    except:
        print("Skipping model download. Run 'ollama pull mistral' manually.")

pull_default_model()

setup(
    name="ai-terminator",  # Change the package name
    version="1.0.0",
    description="A terminal AI assistant that can execute system commands and provide general information.",
    author="Himanshu sanecha",
    author_email="himanshusanecha@gmail.com",
    packages=find_packages(),  # Ensure submodules are included  # Automatically find packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[  # Add dependencies here
        "ollama",
        "colorama",
        "gnureadline"
    ],
    entry_points={
        "console_scripts": [
            "ai-terminator=terminal_ai.terminal:run_terminal",  # Change package reference
        ],
    },
)
