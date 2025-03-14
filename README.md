# Voice Control System

A voice-controlled system for laptop control using spoken commands, built with:

- **Whisper (OpenAI)** - For transcribing spoken commands into text
- **Local LLM** - For processing transcribed text into structured commands
- **Pynput** - For executing structured commands as keyboard and mouse inputs

## Features

- Real-time audio capture with voice activity detection
- Accurate speech-to-text transcription using Whisper
- Command interpretation using a local LLM
- Keyboard and mouse control via pynput
- Continuous listening loop for seamless interaction
- Optimized version with improved latency and accuracy

## System Architecture

The system consists of three main components:

1. **Audio Capture and Transcription (Whisper)**
   - Captures audio from the microphone
   - Transcribes spoken commands to text using OpenAI's Whisper model

2. **Command Interpretation (Local LLM)**
   - Processes transcribed text into structured commands
   - Supports various command formats for mouse and keyboard control

3. **Command Execution (Pynput)**
   - Executes structured commands as actual keyboard and mouse inputs
   - Supports mouse movements, clicks, scrolling, and keyboard shortcuts

## Command Examples

The system supports various voice commands that are converted into structured formats:

- "Move mouse to 500, 300" → `{'type': 'mouse', 'action': 'move', 'x': 500, 'y': 300}`
- "Click left mouse button" → `{'type': 'mouse', 'action': 'click', 'button': 'left'}`
- "Right click" → `{'type': 'mouse', 'action': 'click', 'button': 'right'}`
- "Double click" → `{'type': 'mouse', 'action': 'double_click', 'button': 'left'}`
- "Scroll down 5 lines" → `{'type': 'mouse', 'action': 'scroll', 'direction': 'down', 'amount': 5}`
- "Press control and c" → `{'type': 'keyboard', 'action': 'press', 'keys': ['ctrl', 'c']}`
- "Press alt f4" → `{'type': 'keyboard', 'action': 'press', 'keys': ['alt', 'f4']}`
- "Type hello world" → `{'type': 'keyboard', 'action': 'type', 'text': 'hello world'}`

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/h-moss/lazy.git
   cd lazy
   ```

2. Install dependencies:
   ```
   # System dependencies
   sudo apt-get update
   sudo apt-get install -y portaudio19-dev python3-pyaudio
   
   # Python dependencies
   pip install pyaudio pynput transformers torch llama-cpp-python
   ```

3. Download a model for the local LLM:
   - Create a `models` directory
   - Download a compatible model (e.g., from [TheBloke on Hugging Face](https://huggingface.co/TheBloke))
   - Place the model file in the `models` directory

## Usage

### Standard Version

Run the standard voice control system:

```
python main.py
```

### Optimized Version

Run the optimized version with improved latency and accuracy:

```
python main.py --optimized
```

### Additional Options

```
python main.py --help
```

Options:
- `--optimized`: Use the optimized version
- `--whisper-model MODEL`: Specify the Whisper model to use
- `--llm-model PATH`: Path to the LLM model file
- `--verbose`: Enable verbose output
- `--test`: Run in test mode (exits after 30 seconds)

## Testing

Run the test suite to verify system functionality:

```
python test_voice_control.py
```

## Optimization Features

The optimized version includes:
- Command caching for frequently used commands
- Parallel processing of transcription and interpretation
- Voice activity detection to reduce processing of silence
- Efficient audio chunking for lower latency
- Command validation to improve accuracy

## License

This project is licensed under the MIT License - see the LICENSE file for details.
