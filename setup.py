from setuptools import setup, find_packages

setup(
    name="ai-terminator",  # Change the package name
    version="0.1.0",
    description="A terminal AI assistant that can execute system commands and provide general information.",
    author="Himanshu sanecha",
    author_email="himanshusanecha@gmail.com",
    packages=find_packages(),  # Automatically find packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",

    entry_points={
        "console_scripts": [
            "terminal-ai=terminal_ai.terminal:run_terminal",  # Change package reference
        ],
    },
)
