import os
import time
import json
import threading
from typing import Dict, Any, Optional

from src.core.simplified_transcriber import SimplifiedTranscriber
from src.core.command_interpreter import CommandInterpreter
from src.core.command_executor import CommandExecutor

class VoiceControlSystem:
    """
    A voice-controlled system that integrates Whisper transcription,
    local LLM command interpretation, and pynput command execution.
    """
    def __init__(self, 
                 llm_model_path: Optional[str] = None,
                 verbose: bool = False):
        """
        Initialize the VoiceControlSystem.
        
        Args:
            llm_model_path (str, optional): Path to the LLM model file.
            verbose (bool): Whether to print verbose output.
        """
        self.verbose = verbose
        
        # Initialize components
        print("Initializing transcriber...")
        self.transcriber = SimplifiedTranscriber(verbose=verbose)
        
        print("Initializing command interpreter...")
        self.interpreter = CommandInterpreter(
            model_path=llm_model_path,
            verbose=verbose
        )
        
        print("Initializing command executor...")
        self.executor = CommandExecutor(verbose=verbose)
        
        # System state
        self.is_running = False
        self.processing_lock = threading.Lock()
        self.last_command_time = 0
        self.command_cooldown = 1.0  # seconds
        
    def start(self):
        """Start the voice control system."""
        if self.is_running:
            print("Voice control system is already running.")
            return
            
        self.is_running = True
        
        # Start the transcriber with our callback
        self.transcriber.start_listening(callback=self._handle_transcription)
        
        print("\nVoice control system is now running!")
        print("Speak commands into your microphone.")
        print("Examples:")
        print("  - 'Move mouse to 500, 300'")
        print("  - 'Click left mouse button'")
        print("  - 'Press control and c'")
        print("  - 'Type hello world'")
        print("\nPress Ctrl+C to stop the system.")
        
    def stop(self):
        """Stop the voice control system."""
        if not self.is_running:
            return
            
        self.is_running = False
        self.transcriber.stop_listening()
        print("\nVoice control system stopped.")
        
    def _handle_transcription(self, result):
        """
        Handle transcription results from Whisper.
        
        Args:
            result (dict): Transcription result from Whisper.
        """
        # Check if we're still running
        if not self.is_running:
            return
            
        # Extract the transcribed text
        text = result.get('text', '').strip()
        if not text:
            return
            
        # Check if we're in the cooldown period
        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            return
            
        # Acquire lock to prevent concurrent processing
        if not self.processing_lock.acquire(blocking=False):
            return
            
        try:
            # Update last command time
            self.last_command_time = current_time
            
            # Print the transcribed text
            print(f"\nTranscribed: {text}")
            
            # Interpret the command
            print("Interpreting command...")
            command = self.interpreter.interpret(text)
            
            # Check for error
            if "error" in command:
                print(f"Error: {command['error']}")
                return
                
            # Print the interpreted command
            print(f"Command: {json.dumps(command, indent=2)}")
            
            # Execute the command
            print("Executing command...")
            success = self.executor.execute(command)
            
            # Print the result
            if success:
                print("Command executed successfully.")
            else:
                print("Failed to execute command.")
                
        finally:
            # Release the lock
            self.processing_lock.release()


def main():
    """Main function to run the voice control system."""
    print("Initializing voice control system...")
    
    # Create the voice control system
    system = VoiceControlSystem(verbose=True)
    
    # Start the system
    system.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping voice control system...")
    finally:
        # Clean up
        system.stop()


if __name__ == "__main__":
    main()
