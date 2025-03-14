#!/usr/bin/env python3
"""
Main entry point for the voice control system.
"""
from core.audio_capture import AudioCapture
from core.transcriber import WhisperTranscriber
from core.command_interpreter import CommandInterpreter
from core.command_executor import CommandExecutor

def main():
    """Run the voice control system."""
    print("Starting Voice Control System")
    print("============================")
    
    # Initialize components
    print("Initializing audio capture...")
    audio = AudioCapture()
    
    print("Initializing transcriber...")
    transcriber = WhisperTranscriber()
    
    print("Initializing command interpreter...")
    interpreter = CommandInterpreter()
    
    print("Initializing command executor...")
    executor = CommandExecutor()
    
    # Define callback for transcription results
    def process_command(result):
        text = result.get('text', '').strip()
        if not text:
            return
            
        print(f"Transcribed: '{text}'")
        
        # Interpret command
        command = interpreter.interpret(text)
        
        # Execute command if valid
        if "error" not in command:
            print(f"Executing: {command}")
            executor.execute(command)
        else:
            print(f"Error: {command['error']}")
    
    # Start listening
    print("\nListening for voice commands... (Press Ctrl+C to stop)")
    transcriber.start_listening(callback=process_command)
    
    try:
        # Keep the main thread alive
        while True:
            import time
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        # Clean up
        transcriber.stop_listening()

if __name__ == "__main__":
    main()
