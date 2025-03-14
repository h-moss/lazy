#!/usr/bin/env python3
"""
Main entry point for the voice control system.
"""
import argparse
import time
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.core.voice_control_system import VoiceControlSystem
from src.core.optimized_voice_control import OptimizedVoiceControlSystem

def main():
    """Main function to run the voice control system."""
    parser = argparse.ArgumentParser(description="Voice Control System")
    parser.add_argument("--optimized", action="store_true", help="Use optimized voice control system")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--llm-model", help="Path to LLM model file")
    parser.add_argument("--engine", default="whisper", choices=["whisper", "google", "sphinx"], 
                       help="Recognition engine to use with SpeechRecognition")
    
    args = parser.parse_args()
    
    print("Initializing voice control system...")
    
    # Create the voice control system
    if args.optimized:
        system = OptimizedVoiceControlSystem(
            llm_model_path=args.llm_model,
            verbose=args.verbose,
            recognition_engine=args.engine
        )
    else:
        system = VoiceControlSystem(
            llm_model_path=args.llm_model,
            verbose=args.verbose,
            recognition_engine=args.engine
        )
    
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
