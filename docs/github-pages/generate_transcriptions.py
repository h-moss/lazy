#!/usr/bin/env python3
"""
Script to generate transcriptions for test audio files and save them for the GitHub Pages website.
"""
import os
import sys
import json
import shutil
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.core.simplified_transcriber import SimplifiedTranscriber
from src.core.command_interpreter import CommandInterpreter

def main():
    """Generate transcriptions for test audio files and save them for the GitHub Pages website."""
    print("Generating transcriptions for test audio files...")
    
    # Initialize components
    transcriber = SimplifiedTranscriber(verbose=True)
    interpreter = CommandInterpreter(verbose=True)
    
    # Define test cases with expected outputs
    test_cases = [
        {"file": "move_mouse.wav", "expected": {"type": "mouse", "action": "move", "x": 500, "y": 300}},
        {"file": "click.wav", "expected": {"type": "mouse", "action": "click", "button": "left"}},
        {"file": "right_click.wav", "expected": {"type": "mouse", "action": "click", "button": "right"}},
        {"file": "double_click.wav", "expected": {"type": "mouse", "action": "double_click", "button": "left"}},
        {"file": "scroll_down.wav", "expected": {"type": "mouse", "action": "scroll", "direction": "down", "amount": 5}},
        {"file": "press_ctrl_c.wav", "expected": {"type": "keyboard", "action": "press", "keys": ["ctrl", "c"]}},
        {"file": "press_alt_f4.wav", "expected": {"type": "keyboard", "action": "press", "keys": ["alt", "f4"]}},
        {"file": "type_hello.wav", "expected": {"type": "keyboard", "action": "type", "text": "hello world"}}
    ]
    
    # Create audio directory in GitHub Pages
    audio_dir = os.path.join(os.path.dirname(__file__), 'audio')
    os.makedirs(audio_dir, exist_ok=True)
    
    # Create data directory for transcriptions
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Process each test case
    results = []
    
    for test in test_cases:
        file_path = os.path.join(project_root, 'test_audio', test["file"])
        
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            continue
        
        # Copy audio file to GitHub Pages audio directory
        dest_path = os.path.join(audio_dir, test["file"])
        shutil.copy2(file_path, dest_path)
        
        # Transcribe audio
        print(f"Transcribing: {test['file']}")
        transcription = transcriber.transcribe_file(file_path)
        
        # Get transcribed text
        text = transcription.get("text", "")
        
        # Interpret command
        command = interpreter.interpret(text) if text else {"error": "No transcription"}
        
        # Create result object
        result = {
            "file": test["file"],
            "voice_command": test["file"].replace(".wav", "").replace("_", " "),
            "transcription": text,
            "command": command,
            "expected": test["expected"]
        }
        
        results.append(result)
        
        # Save individual result as JSON
        result_file = os.path.join(data_dir, f"{test['file'].replace('.wav', '.json')}")
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Processed: {test['file']}")
    
    # Save all results as a single JSON file
    all_results_file = os.path.join(data_dir, "all_results.json")
    with open(all_results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Generated transcriptions for {len(results)} audio files")
    print(f"Results saved to: {data_dir}")
    print(f"Audio files copied to: {audio_dir}")

if __name__ == "__main__":
    main()
