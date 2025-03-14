#!/usr/bin/env python3
"""
Mock tests for the voice control system.
These tests don't require a display server or real voice input.
"""
import unittest
import json
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.command_interpreter import CommandInterpreter

class TestCommandInterpreter(unittest.TestCase):
    """Test the command interpreter with mock inputs."""
    
    def setUp(self):
        """Set up the test case."""
        self.interpreter = CommandInterpreter(model_path=None, verbose=False)
        
    def test_mouse_move_command(self):
        """Test mouse move command interpretation."""
        test_cases = [
            ("move mouse to 500, 300", {"type": "mouse", "action": "move", "x": 500, "y": 300}),
            ("move cursor to 100 200", {"type": "mouse", "action": "move", "x": 100, "y": 200}),
            ("move mouse to coordinates 300, 400", {"type": "mouse", "action": "move", "x": 300, "y": 400}),
        ]
        
        for text, expected in test_cases:
            command = self.interpreter.interpret(text)
            self.assertEqual(command["type"], expected["type"])
            self.assertEqual(command["action"], expected["action"])
            self.assertEqual(command["x"], expected["x"])
            self.assertEqual(command["y"], expected["y"])
            
    def test_mouse_click_command(self):
        """Test mouse click command interpretation."""
        test_cases = [
            ("click left mouse button", {"type": "mouse", "action": "click", "button": "left"}),
            ("click", {"type": "mouse", "action": "click", "button": "left"}),
            ("right click", {"type": "mouse", "action": "click", "button": "right"}),
            ("double click", {"type": "mouse", "action": "double_click", "button": "left"}),
        ]
        
        for text, expected in test_cases:
            command = self.interpreter.interpret(text)
            self.assertEqual(command["type"], expected["type"])
            self.assertEqual(command["action"], expected["action"])
            self.assertEqual(command["button"], expected["button"])
            
    def test_keyboard_press_command(self):
        """Test keyboard press command interpretation."""
        test_cases = [
            ("press control and c", {"type": "keyboard", "action": "press", "keys": ["ctrl", "c"]}),
            ("press alt f4", {"type": "keyboard", "action": "press", "keys": ["alt", "f4"]}),
        ]
        
        for text, expected in test_cases:
            command = self.interpreter.interpret(text)
            self.assertEqual(command["type"], expected["type"])
            self.assertEqual(command["action"], expected["action"])
            self.assertEqual(command["keys"], expected["keys"])
            
    def test_keyboard_type_command(self):
        """Test keyboard type command interpretation."""
        test_cases = [
            ("type hello world", {"type": "keyboard", "action": "type", "text": "hello world"}),
            ("type 'testing 123'", {"type": "keyboard", "action": "type", "text": "testing 123"}),
        ]
        
        for text, expected in test_cases:
            command = self.interpreter.interpret(text)
            self.assertEqual(command["type"], expected["type"])
            self.assertEqual(command["action"], expected["action"])
            self.assertEqual(command["text"], expected["text"])

if __name__ == "__main__":
    unittest.main()
