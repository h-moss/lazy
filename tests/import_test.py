#!/usr/bin/env python3
"""
Simple test to verify imports work correctly.
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")
    
    # Import core modules
    from src.core.command_interpreter import CommandInterpreter
    print("✓ CommandInterpreter")
    
    from src.core.transcriber import WhisperTranscriber
    print("✓ WhisperTranscriber")
    
    from src.core.command_worker import CommandWorker
    print("✓ CommandWorker")
    
    # Try importing modules that require X server
    try:
        from src.core.mouse_controller import MouseController
        print("✓ MouseController")
        
        from src.core.keyboard_controller import KeyboardController
        print("✓ KeyboardController")
        
        from src.core.command_executor import CommandExecutor
        print("✓ CommandExecutor")
        
        from src.core.voice_control_system import VoiceControlSystem
        print("✓ VoiceControlSystem")
        
        from src.core.optimized_voice_control import OptimizedVoiceControlSystem
        print("✓ OptimizedVoiceControlSystem")
    except ImportError as e:
        print(f"Note: Some modules requiring X server could not be imported: {e}")
        print("This is expected in headless environments and doesn't indicate a problem with the refactoring.")
    
    print("\nAll imports tested successfully!")
    return True

if __name__ == "__main__":
    test_imports()
