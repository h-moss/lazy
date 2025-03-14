#!/usr/bin/env python3
"""
Main script to run the voice-controlled system.
"""
import os
import sys
import time
import argparse

def main():
    """Main function to run the voice control system."""
    parser = argparse.ArgumentParser(description='Voice Control System')
    parser.add_argument('--optimized', action='store_true', help='Use optimized version')
    parser.add_argument('--whisper-model', type=str, default='openai/whisper-small',
                        help='Whisper model to use (default: openai/whisper-small)')
    parser.add_argument('--llm-model', type=str, default=None,
                        help='Path to LLM model file (default: None)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    
    args = parser.parse_args()
    
    if args.optimized:
        from optimized_voice_control import OptimizedVoiceControlSystem
        
        print("Starting optimized voice control system...")
        system = OptimizedVoiceControlSystem(
            whisper_model=args.whisper_model,
            llm_model_path=args.llm_model,
            verbose=args.verbose
        )
    else:
        from voice_control_system import VoiceControlSystem
        
        print("Starting standard voice control system...")
        system = VoiceControlSystem(
            whisper_model=args.whisper_model,
            llm_model_path=args.llm_model,
            verbose=args.verbose
        )
    
    # Start the system
    system.start()
    
    if args.test:
        # Run in test mode
        print("\nRunning in test mode. System will exit after 30 seconds.")
        try:
            time.sleep(30)
        finally:
            system.stop()
            return
    
    # Run normally
    try:
        print("\nPress Ctrl+C to stop the system.")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping voice control system...")
    finally:
        # Clean up
        system.stop()


if __name__ == "__main__":
    main()
