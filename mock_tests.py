#!/usr/bin/env python3
"""
Mock tests for the voice control system that don't require an X server.
"""
import unittest
from unittest.mock import MagicMock, patch
import json
import os
import sys

# Mock pynput modules before importing our modules
sys.modules['pynput'] = MagicMock()
sys.modules['pynput.mouse'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()

# Now import our modules
from command_interpreter import CommandInterpreter

class TestCommandInterpreter(unittest.TestCase):
    """Test the CommandInterpreter class with mocks."""
    
    @patch('llama_cpp.Llama')
    def test_initialization(self, mock_llama):
        """Test initialization of CommandInterpreter."""
        interpreter = CommandInterpreter(model_path=None)
        self.assertIsNotNone(interpreter)
        
    @patch('llama_cpp.Llama')
    def test_pattern_matching(self, mock_llama):
        """Test pattern matching for common commands."""
        interpreter = CommandInterpreter(model_path=None)
        
        # Test mouse movement command
        result = interpreter._match_common_patterns("move mouse to 500, 300")
        self.assertEqual(result["type"], "mouse")
        self.assertEqual(result["action"], "move")
        self.assertEqual(result["x"], 500)
        self.assertEqual(result["y"], 300)
        
        # Test click command
        result = interpreter._match_common_patterns("click left mouse button")
        self.assertEqual(result["type"], "mouse")
        self.assertEqual(result["action"], "click")
        self.assertEqual(result["button"], "left")
        
        # Test keyboard shortcut
        result = interpreter._match_common_patterns("press ctrl and c")
        self.assertEqual(result["type"], "keyboard")
        self.assertEqual(result["action"], "press")
        self.assertEqual(result["keys"], ["ctrl", "c"])
        
        # Test typing command
        result = interpreter._match_common_patterns("type hello world")
        self.assertEqual(result["type"], "keyboard")
        self.assertEqual(result["action"], "type")
        self.assertEqual(result["text"], "hello world")
        
    @patch('llama_cpp.Llama')
    def test_command_validation(self, mock_llama):
        """Test command validation."""
        interpreter = CommandInterpreter(model_path=None)
        
        # Valid mouse command
        command = {"type": "mouse", "action": "move", "x": 500, "y": 300}
        self.assertTrue(interpreter._validate_command(command))
        
        # Invalid mouse command (missing x)
        command = {"type": "mouse", "action": "move", "y": 300}
        self.assertFalse(interpreter._validate_command(command))
        
        # Valid keyboard command
        command = {"type": "keyboard", "action": "press", "keys": ["ctrl", "c"]}
        self.assertTrue(interpreter._validate_command(command))
        
        # Invalid keyboard command (missing keys)
        command = {"type": "keyboard", "action": "press"}
        self.assertFalse(interpreter._validate_command(command))
        
    @patch('llama_cpp.Llama')
    def test_interpret_with_pattern_matching(self, mock_llama):
        """Test interpret method with pattern matching."""
        interpreter = CommandInterpreter(model_path=None)
        
        # Test with a command that can be pattern matched
        result = interpreter.interpret("move mouse to 500, 300")
        self.assertEqual(result["type"], "mouse")
        self.assertEqual(result["action"], "move")
        self.assertEqual(result["x"], 500)
        self.assertEqual(result["y"], 300)
        
        # Test with a command that can be pattern matched
        result = interpreter.interpret("click left mouse button")
        self.assertEqual(result["type"], "mouse")
        self.assertEqual(result["action"], "click")
        self.assertEqual(result["button"], "left")
        
        # Test with a command that can be pattern matched
        result = interpreter.interpret("press ctrl and c")
        self.assertEqual(result["type"], "keyboard")
        self.assertEqual(result["action"], "press")
        self.assertEqual(result["keys"], ["ctrl", "c"])
        
        # Test with a command that can be pattern matched
        result = interpreter.interpret("type hello world")
        self.assertEqual(result["type"], "keyboard")
        self.assertEqual(result["action"], "type")
        self.assertEqual(result["text"], "hello world")
        
    def test_interpret_with_llm_fallback(self):
        """Test interpret method with LLM fallback."""
        # Create interpreter without a model
        interpreter = CommandInterpreter(model_path=None)
        
        # Test with a command that would require LLM
        result = interpreter.interpret("move the cursor to the middle of the screen")
        
        # Verify result contains error message about LLM not being available
        self.assertIn("error", result)
        self.assertIn("LLM not available", result["error"])


class TestSystemIntegration(unittest.TestCase):
    """Test the integration of components with mocks."""
    
    @patch('command_interpreter.CommandInterpreter')
    def test_command_flow(self, mock_interpreter_class):
        """Test the flow from transcription to command execution."""
        # Mock the interpreter
        mock_interpreter = MagicMock()
        mock_interpreter.interpret.return_value = {
            "type": "mouse", 
            "action": "move", 
            "x": 500, 
            "y": 300
        }
        mock_interpreter_class.return_value = mock_interpreter
        
        # Create a mock transcription result
        transcription = "move mouse to 500, 300"
        
        # Interpret the command
        command = mock_interpreter.interpret(transcription)
        
        # Verify the command
        self.assertEqual(command["type"], "mouse")
        self.assertEqual(command["action"], "move")
        self.assertEqual(command["x"], 500)
        self.assertEqual(command["y"], 300)
        
        # Verify the interpreter was called
        mock_interpreter.interpret.assert_called_once_with(transcription)


if __name__ == "__main__":
    unittest.main(verbosity=2)
