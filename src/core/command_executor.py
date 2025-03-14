import json
from typing import Dict, Any
from src.core.mouse_controller import MouseController
from src.core.keyboard_controller import KeyboardController

class CommandExecutor:
    """Executes structured commands using mouse and keyboard controllers."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.mouse_controller = MouseController(verbose)
        self.keyboard_controller = KeyboardController(verbose)
        
    def execute(self, command):
        if self.verbose:
            print(f"Executing command: {json.dumps(command, indent=2)}")
            
        if "error" in command:
            if self.verbose:
                print(f"Error in command: {command['error']}")
            return False
            
        if "type" not in command:
            if self.verbose:
                print("Invalid command: missing 'type'")
            return False
            
        if command["type"] == "mouse":
            return self.mouse_controller.execute(command)
        elif command["type"] == "keyboard":
            return self.keyboard_controller.execute(command)
        else:
            if self.verbose:
                print(f"Unknown command type: {command['type']}")
            return False
            
    def move_mouse_relative(self, dx, dy):
        """Move the mouse by a relative amount."""
        self.mouse_controller.move_relative(dx, dy)
        
    def get_mouse_position(self):
        """Get the current mouse position."""
        return self.mouse_controller.get_position()


# Example usage
if __name__ == "__main__":
    import time
    
    # Initialize the executor
    executor = CommandExecutor(verbose=True)
    
    # Test with some example commands
    test_commands = [
        {"type": "mouse", "action": "move", "x": 500, "y": 300},
        {"type": "mouse", "action": "click", "button": "left"},
        {"type": "keyboard", "action": "type", "text": "Hello, world!"}
    ]
    
    print("WARNING: This will execute actual mouse and keyboard commands.")
    print("Make sure you're ready for this. You have 3 seconds to cancel (Ctrl+C).")
    
    try:
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
            
        print("\nExecuting test commands:")
        for cmd in test_commands:
            executor.execute(cmd)
            time.sleep(1)
            
        print("\nTest completed.")
        
    except KeyboardInterrupt:
        print("\nTest cancelled.")
