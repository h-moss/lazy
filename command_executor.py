from pynput import mouse, keyboard
import time
import json
from typing import Dict, List, Any, Union, Optional

class CommandExecutor:
    """
    A class to execute structured commands using pynput.
    """
    def __init__(self, verbose: bool = False):
        """
        Initialize the CommandExecutor class.
        
        Args:
            verbose (bool): Whether to print verbose output.
        """
        self.verbose = verbose
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        
        # Map of key names to pynput key objects
        self.key_map = {
            # Special keys
            'alt': keyboard.Key.alt,
            'alt_l': keyboard.Key.alt_l,
            'alt_r': keyboard.Key.alt_r,
            'alt_gr': keyboard.Key.alt_gr,
            'backspace': keyboard.Key.backspace,
            'caps_lock': keyboard.Key.caps_lock,
            'cmd': keyboard.Key.cmd,
            'cmd_l': keyboard.Key.cmd_l,
            'cmd_r': keyboard.Key.cmd_r,
            'ctrl': keyboard.Key.ctrl,
            'ctrl_l': keyboard.Key.ctrl_l,
            'ctrl_r': keyboard.Key.ctrl_r,
            'delete': keyboard.Key.delete,
            'down': keyboard.Key.down,
            'end': keyboard.Key.end,
            'enter': keyboard.Key.enter,
            'esc': keyboard.Key.esc,
            'f1': keyboard.Key.f1,
            'f2': keyboard.Key.f2,
            'f3': keyboard.Key.f3,
            'f4': keyboard.Key.f4,
            'f5': keyboard.Key.f5,
            'f6': keyboard.Key.f6,
            'f7': keyboard.Key.f7,
            'f8': keyboard.Key.f8,
            'f9': keyboard.Key.f9,
            'f10': keyboard.Key.f10,
            'f11': keyboard.Key.f11,
            'f12': keyboard.Key.f12,
            'home': keyboard.Key.home,
            'insert': keyboard.Key.insert,
            'left': keyboard.Key.left,
            'menu': keyboard.Key.menu,
            'num_lock': keyboard.Key.num_lock,
            'page_down': keyboard.Key.page_down,
            'page_up': keyboard.Key.page_up,
            'pause': keyboard.Key.pause,
            'print_screen': keyboard.Key.print_screen,
            'right': keyboard.Key.right,
            'scroll_lock': keyboard.Key.scroll_lock,
            'shift': keyboard.Key.shift,
            'shift_l': keyboard.Key.shift_l,
            'shift_r': keyboard.Key.shift_r,
            'space': keyboard.Key.space,
            'tab': keyboard.Key.tab,
            'up': keyboard.Key.up,
        }
        
        # Map of mouse button names to pynput mouse button objects
        self.button_map = {
            'left': mouse.Button.left,
            'right': mouse.Button.right,
            'middle': mouse.Button.middle,
        }
        
    def execute(self, command: Dict[str, Any]) -> bool:
        """
        Execute a structured command.
        
        Args:
            command (dict): Structured command to execute.
            
        Returns:
            bool: Whether the command was executed successfully.
        """
        if self.verbose:
            print(f"Executing command: {json.dumps(command, indent=2)}")
            
        # Check for error in command
        if "error" in command:
            if self.verbose:
                print(f"Error in command: {command['error']}")
            return False
            
        # Check command type
        if "type" not in command:
            if self.verbose:
                print("Invalid command: missing 'type'")
            return False
            
        # Execute based on command type
        if command["type"] == "mouse":
            return self._execute_mouse_command(command)
        elif command["type"] == "keyboard":
            return self._execute_keyboard_command(command)
        else:
            if self.verbose:
                print(f"Unknown command type: {command['type']}")
            return False
            
    def _execute_mouse_command(self, command: Dict[str, Any]) -> bool:
        """
        Execute a mouse command.
        
        Args:
            command (dict): Mouse command to execute.
            
        Returns:
            bool: Whether the command was executed successfully.
        """
        if "action" not in command:
            if self.verbose:
                print("Invalid mouse command: missing 'action'")
            return False
            
        try:
            # Mouse move
            if command["action"] == "move":
                if "x" not in command or "y" not in command:
                    if self.verbose:
                        print("Invalid move command: missing 'x' or 'y'")
                    return False
                    
                x, y = command["x"], command["y"]
                self.mouse_controller.position = (x, y)
                return True
                
            # Mouse click
            elif command["action"] == "click":
                if "button" not in command:
                    if self.verbose:
                        print("Invalid click command: missing 'button'")
                    return False
                    
                button_name = command["button"].lower()
                if button_name not in self.button_map:
                    if self.verbose:
                        print(f"Unknown mouse button: {button_name}")
                    return False
                    
                button = self.button_map[button_name]
                self.mouse_controller.click(button)
                return True
                
            # Mouse double click
            elif command["action"] == "double_click":
                if "button" not in command:
                    if self.verbose:
                        print("Invalid double_click command: missing 'button'")
                    return False
                    
                button_name = command["button"].lower()
                if button_name not in self.button_map:
                    if self.verbose:
                        print(f"Unknown mouse button: {button_name}")
                    return False
                    
                button = self.button_map[button_name]
                self.mouse_controller.click(button, 2)
                return True
                
            # Mouse scroll
            elif command["action"] == "scroll":
                if "direction" not in command or "amount" not in command:
                    if self.verbose:
                        print("Invalid scroll command: missing 'direction' or 'amount'")
                    return False
                    
                direction = command["direction"].lower()
                amount = command["amount"]
                
                if direction == "up":
                    self.mouse_controller.scroll(0, amount)
                elif direction == "down":
                    self.mouse_controller.scroll(0, -amount)
                else:
                    if self.verbose:
                        print(f"Unknown scroll direction: {direction}")
                    return False
                    
                return True
                
            else:
                if self.verbose:
                    print(f"Unknown mouse action: {command['action']}")
                return False
                
        except Exception as e:
            if self.verbose:
                print(f"Error executing mouse command: {e}")
            return False
            
    def _execute_keyboard_command(self, command: Dict[str, Any]) -> bool:
        """
        Execute a keyboard command.
        
        Args:
            command (dict): Keyboard command to execute.
            
        Returns:
            bool: Whether the command was executed successfully.
        """
        if "action" not in command:
            if self.verbose:
                print("Invalid keyboard command: missing 'action'")
            return False
            
        try:
            # Keyboard press
            if command["action"] == "press":
                if "keys" not in command or not isinstance(command["keys"], list):
                    if self.verbose:
                        print("Invalid press command: missing or invalid 'keys'")
                    return False
                    
                keys = command["keys"]
                if not keys:
                    if self.verbose:
                        print("Invalid press command: empty 'keys' list")
                    return False
                    
                # Convert key names to pynput key objects
                pynput_keys = []
                for key_name in keys:
                    key_name = key_name.lower()
                    if key_name in self.key_map:
                        pynput_keys.append(self.key_map[key_name])
                    elif len(key_name) == 1:
                        # Single character key
                        pynput_keys.append(key_name)
                    else:
                        if self.verbose:
                            print(f"Unknown key: {key_name}")
                        return False
                        
                # Press all keys together
                for key in pynput_keys:
                    self.keyboard_controller.press(key)
                    
                # Small delay to ensure keys are registered
                time.sleep(0.05)
                
                # Release all keys in reverse order
                for key in reversed(pynput_keys):
                    self.keyboard_controller.release(key)
                    
                return True
                
            # Keyboard type
            elif command["action"] == "type":
                if "text" not in command or not isinstance(command["text"], str):
                    if self.verbose:
                        print("Invalid type command: missing or invalid 'text'")
                    return False
                    
                text = command["text"]
                self.keyboard_controller.type(text)
                return True
                
            else:
                if self.verbose:
                    print(f"Unknown keyboard action: {command['action']}")
                return False
                
        except Exception as e:
            if self.verbose:
                print(f"Error executing keyboard command: {e}")
            return False
            
    def move_mouse_relative(self, dx: int, dy: int) -> None:
        """
        Move the mouse by a relative amount.
        
        Args:
            dx (int): Horizontal movement.
            dy (int): Vertical movement.
        """
        self.mouse_controller.move(dx, dy)
        
    def get_mouse_position(self) -> tuple:
        """
        Get the current mouse position.
        
        Returns:
            tuple: (x, y) coordinates.
        """
        return self.mouse_controller.position


# Example usage
if __name__ == "__main__":
    # Initialize the executor
    executor = CommandExecutor(verbose=True)
    
    # Test with some example commands
    test_commands = [
        {"type": "mouse", "action": "move", "x": 500, "y": 300},
        {"type": "mouse", "action": "click", "button": "left"},
        {"type": "mouse", "action": "double_click", "button": "left"},
        {"type": "mouse", "action": "scroll", "direction": "down", "amount": 5},
        {"type": "keyboard", "action": "press", "keys": ["ctrl", "c"]},
        {"type": "keyboard", "action": "type", "text": "Hello, world!"}
    ]
    
    print("WARNING: This will execute actual mouse and keyboard commands.")
    print("Make sure you're ready for this. You have 5 seconds to cancel (Ctrl+C).")
    
    try:
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
            
        print("\nExecuting test commands:")
        for i, cmd in enumerate(test_commands):
            print(f"\nCommand {i+1}/{len(test_commands)}:")
            executor.execute(cmd)
            time.sleep(1)  # Wait between commands
            
        print("\nTest completed.")
        
    except KeyboardInterrupt:
        print("\nTest cancelled.")
