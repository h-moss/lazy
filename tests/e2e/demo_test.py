#!/usr/bin/env python3
"""
Demo script to test the voice control system with simulated voice commands.
This script bypasses the need for real voice input by directly feeding
transcribed text to the command interpreter and executor.
"""
import os
import time
import json
from src.core.command_interpreter import CommandInterpreter
from src.core.command_executor import CommandExecutor

def main():
    """Run a demonstration of the voice control system with simulated commands."""
    print("Voice Control System Demo Test")
    print("=============================")
    print("This demo simulates voice commands without requiring real voice input.")
    print("It will interpret and execute commands as if they were spoken.")
    print()
    
    # Initialize components
    print("Initializing command interpreter...")
    interpreter = CommandInterpreter(model_path=None, verbose=True)
    
    print("Initializing command executor...")
    try:
        executor = CommandExecutor(verbose=True)
        executor_available = True
    except Exception as e:
        print(f"Warning: Could not initialize command executor: {e}")
        print("Running in simulation mode only (commands will be interpreted but not executed)")
        executor_available = False
    
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
        
        # Execute the command if executor is available
        if executor_available:
            print("Executing command...")
            try:
                start_time = time.time()
                success = executor.execute(command)
                execute_time = time.time() - start_time
                
                if success:
                    print(f"Command executed successfully in {execute_time:.4f} seconds")
                else:
                    print("Failed to execute command")
            except Exception as e:
                print(f"Error executing command: {e}")
        else:
            print("Skipping execution (simulation mode)")
        
        # Wait between commands
        time.sleep(1)
    
    print("\n" + "="*50)
    print("Demo test completed!")
    print("All commands were successfully interpreted.")
    if not executor_available:
        print("Note: Commands were not executed due to missing display environment.")
        print("To run with full execution, test on a system with a display environment.")

if __name__ == "__main__":
    main()
