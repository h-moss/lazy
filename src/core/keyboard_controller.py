from pynput import keyboard
import time
from typing import Dict, Any, List

class KeyboardController:
    """Controls keyboard actions."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.controller = keyboard.Controller()
        self.key_map = {
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
        
    def execute(self, command):
        if "action" not in command:
            return False
            
        try:
            action = command["action"]
            
            if action == "press":
                return self._press_keys(command)
            elif action == "type":
                return self._type_text(command)
            else:
                return False
        except Exception as e:
            if self.verbose:
                print(f"Error executing keyboard command: {e}")
            return False
            
    def _press_keys(self, command):
        if "keys" not in command or not isinstance(command["keys"], list):
            return False
            
        keys = command["keys"]
        if not keys:
            return False
            
        pynput_keys = []
        for key_name in keys:
            key_name = key_name.lower()
            if key_name in self.key_map:
                pynput_keys.append(self.key_map[key_name])
            elif len(key_name) == 1:
                pynput_keys.append(key_name)
            else:
                return False
                
        for key in pynput_keys:
            self.controller.press(key)
            
        time.sleep(0.05)
            
        for key in reversed(pynput_keys):
            self.controller.release(key)
            
        return True
        
    def _type_text(self, command):
        if "text" not in command or not isinstance(command["text"], str):
            return False
            
        self.controller.type(command["text"])
        return True
