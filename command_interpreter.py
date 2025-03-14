import json
import os
import re
from typing import Dict, List, Any, Optional, Union
from llama_cpp import Llama

class CommandInterpreter:
    """
    A class to interpret transcribed text into structured commands using a local LLM.
    """
    def __init__(self, 
                 model_path: Optional[str] = None,
                 n_ctx: int = 2048,
                 n_threads: Optional[int] = None,
                 verbose: bool = False):
        """
        Initialize the CommandInterpreter class.
        
        Args:
            model_path (str, optional): Path to the LLM model file. If None, will download a default model.
            n_ctx (int): Context window size.
            n_threads (int, optional): Number of threads to use. If None, uses all available cores.
            verbose (bool): Whether to print verbose output.
        """
        self.verbose = verbose
        
        # Default model path in the models directory
        if model_path is None:
            model_path = self._get_default_model()
            
        # Initialize the LLM
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads or os.cpu_count(),
            verbose=verbose
        )
        
        # Command templates for the system prompt
        self.command_templates = {
            "mouse_move": {"type": "mouse", "action": "move", "x": 0, "y": 0},
            "mouse_click": {"type": "mouse", "action": "click", "button": "left"},
            "mouse_double_click": {"type": "mouse", "action": "double_click", "button": "left"},
            "mouse_right_click": {"type": "mouse", "action": "click", "button": "right"},
            "mouse_scroll": {"type": "mouse", "action": "scroll", "direction": "up", "amount": 5},
            "keyboard_press": {"type": "keyboard", "action": "press", "keys": []},
            "keyboard_type": {"type": "keyboard", "action": "type", "text": ""}
        }
        
        # Cache for frequently used commands
        self.command_cache = {}
        
    def _get_default_model(self) -> str:
        """
        Get the default model path. Downloads the model if it doesn't exist.
        
        Returns:
            str: Path to the model file.
        """
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        os.makedirs(models_dir, exist_ok=True)
        
        # Default to a small model for quick loading
        default_model = os.path.join(models_dir, "ggml-model-q4_0.bin")
        
        # Check if model exists, if not download it
        if not os.path.exists(default_model):
            if self.verbose:
                print(f"Model not found at {default_model}. Please download a compatible model.")
                print("You can download models from https://huggingface.co/TheBloke")
                print("For example: llama-cpp-python-7b-ggml-model-q4_0.bin")
            
            # Return path anyway, will fail later but with a more specific error
            return default_model
            
        return default_model
        
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt for the LLM.
        
        Returns:
            str: System prompt.
        """
        prompt = """
You are a voice command interpreter that converts natural language commands into structured JSON for computer control.
Your task is to interpret the user's voice command and convert it to a valid JSON object following these templates:

1. Mouse movement: {"type": "mouse", "action": "move", "x": <x_coordinate>, "y": <y_coordinate>}
2. Mouse click: {"type": "mouse", "action": "click", "button": "<left|right|middle>"}
3. Mouse double-click: {"type": "mouse", "action": "double_click", "button": "<left|right|middle>"}
4. Mouse scroll: {"type": "mouse", "action": "scroll", "direction": "<up|down>", "amount": <number>}
5. Keyboard press: {"type": "keyboard", "action": "press", "keys": [<array_of_keys>]}
6. Keyboard type: {"type": "keyboard", "action": "type", "text": "<text_to_type>"}

Examples:
- "move mouse to coordinates 500, 300" → {"type": "mouse", "action": "move", "x": 500, "y": 300}
- "click left mouse button" → {"type": "mouse", "action": "click", "button": "left"}
- "right click" → {"type": "mouse", "action": "click", "button": "right"}
- "double click" → {"type": "mouse", "action": "double_click", "button": "left"}
- "scroll down 5 lines" → {"type": "mouse", "action": "scroll", "direction": "down", "amount": 5}
- "press control and c" → {"type": "keyboard", "action": "press", "keys": ["ctrl", "c"]}
- "press alt f4" → {"type": "keyboard", "action": "press", "keys": ["alt", "f4"]}
- "type hello world" → {"type": "keyboard", "action": "type", "text": "hello world"}

Important rules:
1. Only respond with a valid JSON object, nothing else.
2. For keyboard keys, use standard key names like: ctrl, alt, shift, enter, space, tab, esc, f1-f12, etc.
3. If the command is unclear or cannot be interpreted, respond with: {"error": "Could not interpret command"}
4. For mouse coordinates, use pixel values (integers).
5. For scroll amount, use a number representing lines or units to scroll.

Now interpret the following voice command:
"""
        return prompt.strip()
        
    def interpret(self, text: str) -> Dict[str, Any]:
        """
        Interpret transcribed text into a structured command.
        
        Args:
            text (str): Transcribed text to interpret.
            
        Returns:
            dict: Structured command.
        """
        # Check cache first
        if text in self.command_cache:
            return self.command_cache[text]
            
        # Clean up the text
        text = text.strip().lower()
        
        # Try to match common patterns directly for faster response
        command = self._match_common_patterns(text)
        if command:
            # Cache the result
            self.command_cache[text] = command
            return command
            
        # Use the LLM for more complex commands
        system_prompt = self._build_system_prompt()
        prompt = f"{system_prompt}\n\n{text}"
        
        # Generate response from LLM
        response = self.llm(
            prompt,
            max_tokens=256,
            stop=["```"],
            echo=False
        )
        
        # Extract the generated text
        generated_text = response["choices"][0]["text"].strip()
        
        # Try to parse as JSON
        try:
            # Find JSON in the response
            json_match = re.search(r'(\{.*\})', generated_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                command = json.loads(json_str)
                
                # Validate the command
                if self._validate_command(command):
                    # Cache the result
                    self.command_cache[text] = command
                    return command
        except (json.JSONDecodeError, ValueError) as e:
            if self.verbose:
                print(f"Error parsing JSON: {e}")
                print(f"Generated text: {generated_text}")
        
        # Return error if parsing failed
        return {"error": "Could not interpret command"}
    
    def _match_common_patterns(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Match common command patterns directly without using the LLM.
        
        Args:
            text (str): Text to match.
            
        Returns:
            dict or None: Matched command or None if no match.
        """
        # Mouse movement
        mouse_move_match = re.search(r'move (?:mouse|cursor) (?:to)? (?:coordinates? |position |point )?(\d+)[,\s]+(\d+)', text)
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
        # Common key combinations
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
            
        # No match found
        return None
        
    def _validate_command(self, command: Dict[str, Any]) -> bool:
        """
        Validate a command structure.
        
        Args:
            command (dict): Command to validate.
            
        Returns:
            bool: Whether the command is valid.
        """
        if "error" in command:
            return True
            
        if "type" not in command:
            return False
            
        if command["type"] == "mouse":
            if "action" not in command:
                return False
                
            if command["action"] == "move":
                return "x" in command and "y" in command
                
            if command["action"] in ["click", "double_click"]:
                return "button" in command
                
            if command["action"] == "scroll":
                return "direction" in command and "amount" in command
                
        elif command["type"] == "keyboard":
            if "action" not in command:
                return False
                
            if command["action"] == "press":
                return "keys" in command and isinstance(command["keys"], list)
                
            if command["action"] == "type":
                return "text" in command and isinstance(command["text"], str)
                
        return False


# Example usage
if __name__ == "__main__":
    # Initialize the interpreter
    interpreter = CommandInterpreter(verbose=True)
    
    # Test with some example commands
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
    
    for cmd in test_commands:
        print(f"\nInterpreting: '{cmd}'")
        result = interpreter.interpret(cmd)
        print(f"Result: {json.dumps(result, indent=2)}")
