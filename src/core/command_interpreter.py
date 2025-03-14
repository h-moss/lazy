import json
import os
import re
from typing import Dict, Any, Optional
from llama_cpp import Llama
from src.core.pattern_matcher import PatternMatcher

class CommandInterpreter:
    """Interprets transcribed text into structured commands."""
    
    def __init__(self, model_path=None, n_ctx=2048, n_threads=None, verbose=False):
        self.verbose = verbose
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        
        # Get model path and initialize LLM
        self.model_path = model_path or self._get_default_model()
        self.llm = self._initialize_llm()
        
        # Initialize pattern matcher and command cache
        self.pattern_matcher = PatternMatcher()
        self.command_cache = {}
        
    def _initialize_llm(self):
        """Initialize the LLM if model path exists."""
        if self.model_path and os.path.exists(self.model_path):
            return Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads or os.cpu_count(),
                verbose=self.verbose
            )
        return None
        
    def _get_default_model(self):
        """Get the default model path."""
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "models")
        os.makedirs(models_dir, exist_ok=True)
        return os.path.join(models_dir, "llm_model.bin")
        
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
        
    def interpret(self, text):
        """Interpret transcribed text into a structured command."""
        # Check cache first
        if text in self.command_cache:
            return self.command_cache[text]
            
        # Clean up the text
        text = text.strip().lower()
        
        # Try to match common patterns directly for faster response
        command = self.pattern_matcher.match_pattern(text)
        if command:
            # Cache the result
            self.command_cache[text] = command
            return command
            
        # Use the LLM for more complex commands if available
        if self.llm is None:
            if self.verbose:
                print("LLM not initialized. Using pattern matching only.")
            return {"error": "LLM not available. Could not interpret complex command."}
            
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
                
        # Return error if parsing failed
        return {"error": "Could not interpret command"}
    
    def _validate_command(self, command):
        """Validate a command structure."""
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
