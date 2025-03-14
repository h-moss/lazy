from setuptools import setup, find_packages

setup(
    name="voice-control-system",
    version="0.1.0",
    description="Voice-controlled system using Whisper, local LLM, and pynput",
    author="Devin AI",
    packages=find_packages(),
    install_requires=[
        "pyaudio>=0.2.13",
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "llama-cpp-python>=0.2.0",
        "pynput>=1.7.6",
        "numpy>=1.20.0",
        "tqdm>=4.65.0",
    ],
    entry_points={
        "console_scripts": [
            "voice-control=src.main:main",
        ],
    },
    python_requires=">=3.8",
)
