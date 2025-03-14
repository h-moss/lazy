#!/usr/bin/env python3
"""
End-to-end test for the voice control system using pre-recorded audio files.
"""
import os
import time
import json
import argparse
from typing import Dict, Any, Optional

from src.core.transcriber import Transcriber
from src.core.command_interpreter import CommandInterpreter

# Only import CommandExecutor if we have a display
try:
    from src.core.command_executor import CommandExecutor
    HAS_DISPLAY = True
except ImportError:
    HAS_DISPLAY = False
    print("Warning: No display detected. Running in headless mode without command execution.")

def test_with_audio_file(
    audio_file: str,
    expected_command: Dict[str, Any],
    whisper_model: str = "openai/whisper-small",
    llm_model_path: Optional[str] = None,
    verbose: bool = False
) -> bool:
    """
    Test the voice control system with a pre-recorded audio file.
    
    Args:
        audio_file (str): Path to the audio file.
        expected_command (dict): Expected command structure.
        whisper_model (str): Name of the Whisper model to use.
        llm_model_path (str): Path to the LLM model file.
        verbose (bool): Whether to print verbose output.
        
    Returns:
        bool: Whether the test passed.
    """
    print(f"\nTesting with audio file: {audio_file}")
    
    # Initialize components
    print("Initializing transcriber...")
    transcriber = Transcriber(
        verbose=verbose
    )
    
    print("Initializing command interpreter...")
    interpreter = CommandInterpreter(
        model_path=llm_model_path,
        verbose=verbose
    )
    
    # Initialize command executor if display is available
    executor = None
    if HAS_DISPLAY:
        try:
            print("Initializing command executor...")
            executor = CommandExecutor(verbose=verbose)
        except Exception as e:
            print(f"Warning: Could not initialize command executor: {e}")
            print("Running in headless mode without command execution.")
    
    # Transcribe the audio file
    print("Transcribing audio...")
    start_time = time.time()
    transcription = transcriber.transcribe_file(audio_file)
    transcribe_time = time.time() - start_time
    
    # Print the transcription
    text = transcription.get('text', '').strip()
    print(f"Transcribed text: '{text}'")
    print(f"Transcription time: {transcribe_time:.4f} seconds")
    
    # Interpret the command
    print("Interpreting command...")
    start_time = time.time()
    command = interpreter.interpret(text)
    interpret_time = time.time() - start_time
    
    # Print the command
    print(f"Interpreted command: {json.dumps(command, indent=2)}")
    print(f"Interpretation time: {interpret_time:.4f} seconds")
    
    # Compare with expected command
    print("Comparing with expected command...")
    if "error" in command:
        print(f"Error: {command['error']}")
        return False
    
    # Check if command matches expected structure
    match = True
    for key, value in expected_command.items():
        if key not in command or command[key] != value:
            match = False
            break
    
    if match:
        print("✅ Test PASSED: Command matches expected structure")
        
        # Execute command if executor is available
        if executor is not None:
            print("Executing command...")
            success = executor.execute(command)
            if success:
                print("Command executed successfully.")
            else:
                print("Failed to execute command.")
        else:
            print("Skipping execution (headless mode).")
            
        return True
    else:
        print("❌ Test FAILED: Command does not match expected structure")
        print(f"Expected: {json.dumps(expected_command, indent=2)}")
        return False

def main():
    """Run end-to-end tests with pre-recorded audio files."""
    parser = argparse.ArgumentParser(description='End-to-end test with audio files')
    parser.add_argument('--audio-dir', type=str, default='test_audio',
                        help='Directory containing test audio files')
    parser.add_argument('--whisper-model', type=str, default='openai/whisper-small',
                        help='Whisper model to use')
    parser.add_argument('--llm-model', type=str, default='models/llm_model.bin',
                        help='Path to LLM model file')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Check if audio directory exists
    if not os.path.exists(args.audio_dir):
        print(f"Error: Audio directory '{args.audio_dir}' does not exist")
        return
    
    # Define test cases
    test_cases = [
        {
            "file": "move_mouse.wav",
            "expected": {"type": "mouse", "action": "move", "x": 500, "y": 300}
        },
        {
            "file": "click.wav",
            "expected": {"type": "mouse", "action": "click", "button": "left"}
        },
        {
            "file": "type_hello.wav",
            "expected": {"type": "keyboard", "action": "type", "text": "hello world"}
        }
    ]
    
    # Run tests
    print("Running end-to-end tests with pre-recorded audio files")
    print("======================================================")
    
    passed = 0
    total = 0
    
    for test in test_cases:
        audio_file = os.path.join(args.audio_dir, test["file"])
        
        # Skip if file doesn't exist
        if not os.path.exists(audio_file):
            print(f"\nSkipping test for {test['file']}: File not found")
            continue
        
        # Run the test
        result = test_with_audio_file(
            audio_file=audio_file,
            expected_command=test["expected"],
            whisper_model=args.whisper_model,
            llm_model_path=args.llm_model,
            verbose=args.verbose
        )
        
        total += 1
        if result:
            passed += 1
    
    # Print summary
    print("\n======================================================")
    print(f"Test summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print(f"❌ {total - passed} tests failed")

if __name__ == "__main__":
    main()
