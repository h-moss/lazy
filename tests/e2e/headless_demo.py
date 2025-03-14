#!/usr/bin/env python3
"""
Headless demo script to test the voice control system's command interpretation
without requiring a display server or real voice input.
"""
import json
import time
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.command_interpreter import CommandInterpreter

def main():
    """Run a demonstration of the command interpreter in headless mode."""
    print("Voice Control System - Headless Demo")
    print("====================================")
    print("This demo tests command interpretation without requiring X server or voice input.")
    print()
    
    # Initialize command interpreter
    print("Initializing command interpreter...")
    interpreter = CommandInterpreter(model_path=None, verbose=True)
    
    # Test commands
    test_commands = [
        "move mouse to 500, 300",
        "click left mouse button",
        "right click",
        "double click",
        "scroll down 5 lines",
        "press control and c",
        "press alt f4",
        "type hello world"
    ]
    
    # Process each command
    results = []
    for cmd in test_commands:
        print("\n" + "="*50)
        print(f"Simulated voice command: '{cmd}'")
        
        # Interpret the command
        print("Interpreting command...")
        start_time = time.time()
        command = interpreter.interpret(cmd)
        interpret_time = time.time() - start_time
        
        # Print the interpreted command
        print(f"Interpreted command: {json.dumps(command, indent=2)}")
        print(f"Interpretation time: {interpret_time:.4f} seconds")
        
        # Store results
        results.append({
            "command": cmd,
            "interpretation": command,
            "time": interpret_time
        })
    
    # Print summary
    print("\n" + "="*50)
    print("Demo test completed!")
    print(f"Processed {len(test_commands)} commands")
    
    # Calculate statistics
    pattern_matched = sum(1 for r in results if "error" not in r["interpretation"])
    avg_time = sum(r["time"] for r in results) / len(results)
    
    print(f"Successfully interpreted: {pattern_matched}/{len(results)} commands")
    print(f"Average interpretation time: {avg_time:.4f} seconds")

if __name__ == "__main__":
    main()
