from pynput import mouse
from typing import Dict, Any

class MouseController:
    """Controls mouse actions."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.controller = mouse.Controller()
        self.button_map = {
            'left': mouse.Button.left,
            'right': mouse.Button.right,
            'middle': mouse.Button.middle,
        }
        
    def execute(self, command):
        if "action" not in command:
            return False
            
        try:
            action = command["action"]
            
            if action == "move":
                return self._move(command)
            elif action == "click":
                return self._click(command)
            elif action == "double_click":
                return self._double_click(command)
            elif action == "scroll":
                return self._scroll(command)
            else:
                return False
        except Exception as e:
            if self.verbose:
                print(f"Error executing mouse command: {e}")
            return False
            
    def _move(self, command):
        if "x" not in command or "y" not in command:
            return False
        self.controller.position = (command["x"], command["y"])
        return True
        
    def _click(self, command):
        if "button" not in command:
            return False
        button_name = command["button"].lower()
        if button_name not in self.button_map:
            return False
        self.controller.click(self.button_map[button_name])
        return True
        
    def _double_click(self, command):
        if "button" not in command:
            return False
        button_name = command["button"].lower()
        if button_name not in self.button_map:
            return False
        self.controller.click(self.button_map[button_name], 2)
        return True
        
    def _scroll(self, command):
        if "direction" not in command or "amount" not in command:
            return False
        direction = command["direction"].lower()
        amount = command["amount"]
        
        if direction == "up":
            self.controller.scroll(0, amount)
        elif direction == "down":
            self.controller.scroll(0, -amount)
        else:
            return False
        return True
        
    def move_relative(self, dx, dy):
        """Move the mouse by a relative amount."""
        self.controller.move(dx, dy)
        
    def get_position(self):
        """Get the current mouse position."""
        return self.controller.position
