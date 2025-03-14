import re
from typing import Dict, Any, Optional

class PatternMatcher:
    """Matches common command patterns without using LLM."""
    
    def match_pattern(self, text: str) -> Optional[Dict[str, Any]]:
        """Match common command patterns directly."""
        text = text.strip().lower()
        
        # Mouse movement
        mouse_move_match = re.search(r'move (?:mouse|cursor) (?:to)? (?:coordinates? |position |point )?(\d+)[,\s.-]+(\d+)', text)
        if mouse_move_match:
            x, y = int(mouse_move_match.group(1)), int(mouse_move_match.group(2))
            return {"type": "mouse", "action": "move", "x": x, "y": y}
            
        # Mouse clicks
        if re.search(r'(?:left )?click|click(?: left)?', text) and not "double" in text and not "right" in text:
            return {"type": "mouse", "action": "click", "button": "left"}
            
        if re.search(r'right click|click right', text):
            return {"type": "mouse", "action": "click", "button": "right"}
            
        if re.search(r'double click|double-click', text):
            return {"type": "mouse", "action": "double_click", "button": "left"}
            
        # Mouse scroll
        scroll_match = re.search(r'scroll (up|down)(?: (\d+))?', text)
        if scroll_match:
            direction = scroll_match.group(1)
            amount = int(scroll_match.group(2)) if scroll_match.group(2) else 3
            return {"type": "mouse", "action": "scroll", "direction": direction, "amount": amount}
            
        # Keyboard shortcuts
        key_combos = {
            r'(?:press |hit )?ctrl(?:l)?(?: and| \+)? c': ["ctrl", "c"],
            r'(?:press |hit )?ctrl(?:l)?(?: and| \+)? v': ["ctrl", "v"],
            r'(?:press |hit )?ctrl(?:l)?(?: and| \+)? x': ["ctrl", "x"],
            r'(?:press |hit )?ctrl(?:l)?(?: and| \+)? z': ["ctrl", "z"],
            r'(?:press |hit )?ctrl(?:l)?(?: and| \+)? a': ["ctrl", "a"],
            r'(?:press |hit )?ctrl(?:l)?(?: and| \+)? s': ["ctrl", "s"],
            r'(?:press |hit )?alt(?: and| \+)? f4': ["alt", "f4"],
            r'(?:press |hit )?alt(?: and| \+)? tab': ["alt", "tab"],
        }
        
        for pattern, keys in key_combos.items():
            if re.search(pattern, text):
                return {"type": "keyboard", "action": "press", "keys": keys}
                
        # Typing text
        type_match = re.search(r'type(?: out| in)? ["\']?([^"\']+)["\']?', text)
        if type_match:
            return {"type": "keyboard", "action": "type", "text": type_match.group(1).strip()}
            
        return None
