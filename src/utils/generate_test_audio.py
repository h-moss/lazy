#!/usr/bin/env python3
"""
Script to generate test audio files using text-to-speech.
This is a helper script for creating test audio files for the voice control system.
"""
import os
import argparse
import subprocess
import tempfile

def generate_audio_file(text, output_file, voice="en-US-Neural2-F"):
    """
    Generate an audio file from text using Google Text-to-Speech.
    
    Args:
        text (str): Text to convert to speech.
        output_file (str): Path to save the audio file.
        voice (str): Voice to use for TTS.
    """
    try:
        # Create a temporary file for the raw audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Use gtts-cli to generate speech
        subprocess.run(
            ["gtts-cli", text, "--output", temp_path],
            check=True
        )
        
        # Convert to proper format using ffmpeg
        subprocess.run(
            ["ffmpeg", "-i", temp_path, "-ar", "16000", "-ac", "1", output_file, "-y"],
            check=True
        )
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        print(f"Generated audio file: {output_file}")
        return True
    
    except Exception as e:
        print(f"Error generating audio file: {e}")
        return False

def main():
    """Generate test audio files for the voice control system."""
    parser = argparse.ArgumentParser(description='Generate test audio files')
    parser.add_argument('--output-dir', type=str, default='test_audio',
                        help='Directory to save audio files')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Define test cases
    test_cases = [
        {"text": "move mouse to 500, 300", "file": "move_mouse.wav"},
        {"text": "click left mouse button", "file": "click.wav"},
        {"text": "right click", "file": "right_click.wav"},
        {"text": "double click", "file": "double_click.wav"},
        {"text": "scroll down 5 lines", "file": "scroll_down.wav"},
        {"text": "press control and c", "file": "press_ctrl_c.wav"},
        {"text": "press alt f4", "file": "press_alt_f4.wav"},
        {"text": "type hello world", "file": "type_hello.wav"}
    ]
    
    # Generate audio files
    print("Generating test audio files...")
    
    success = 0
    for test in test_cases:
        output_file = os.path.join(args.output_dir, test["file"])
        if generate_audio_file(test["text"], output_file):
            success += 1
    
    # Print summary
    print(f"\nGenerated {success}/{len(test_cases)} audio files in {args.output_dir}")
    
    # Print instructions
    print("\nTo install required dependencies:")
    print("  pip install gtts pydub")
    print("  sudo apt-get install ffmpeg")
    
    print("\nTo run the end-to-end test:")
    print("  python file_based_test.py")

if __name__ == "__main__":
    main()
