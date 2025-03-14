#!/usr/bin/env python3
"""
Unit tests for the voice control system.
"""
import unittest
import os
import json
import tempfile
import numpy as np
from unittest.mock import MagicMock, patch

# Add project root to Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import modules that don't require X server
from src.core.transcriber import Transcriber
from src.core.command_interpreter import CommandInterpreter

# Skip tests that require X server in headless environments
SKIP_X_SERVER_TESTS = os.environ.get('DISPLAY', '') == ''
if not SKIP_X_SERVER_TESTS:
    from src.core.command_executor import CommandExecutor
    from src.core.voice_control_system import VoiceControlSystem
    from src.core.optimized_voice_control import OptimizedVoiceControlSystem

# AudioCapture tests removed as the class has been replaced by SpeechRecognition

class TestCommandInterpreter(unittest.TestCase):
    """Test the command interpreter component."""
    
    def setUp(self):
        """Set up the test case."""
        # Mock model path to simulate no LLM available
        self.interpreter = CommandInterpreter(model_path=None, verbose=False)
        
    def test_interpret_with_no_llm(self):
        """Test interpreting commands with no LLM available."""
        command = self.interpreter.interpret("move mouse to 500, 300")
        self.assertIn("error", command)
        self.assertEqual(command["error"], "LLM not available. Could not interpret command.")
        
    @unittest.skip("Skipping tests that require LLM")
    def test_interpret_mouse_move(self):
        """Test interpreting mouse move commands."""
        # This test requires an LLM to be available
        command = self.interpreter.interpret("move mouse to 500, 300")
        self.assertEqual(command["type"], "mouse")
        self.assertEqual(command["action"], "move")
        self.assertEqual(command["x"], 500)
        self.assertEqual(command["y"], 300)
        
    @unittest.skip("Skipping tests that require LLM")
    def test_interpret_mouse_click(self):
        """Test interpreting mouse click commands."""
        # This test requires an LLM to be available
        command = self.interpreter.interpret("click left mouse button")
        self.assertEqual(command["type"], "mouse")
        self.assertEqual(command["action"], "click")
        self.assertEqual(command["button"], "left")
        
    @unittest.skip("Skipping tests that require LLM")
    def test_interpret_keyboard_type(self):
        """Test interpreting keyboard type commands."""
        # This test requires an LLM to be available
        command = self.interpreter.interpret("type hello world")
        self.assertEqual(command["type"], "keyboard")
        self.assertEqual(command["action"], "type")
        self.assertEqual(command["text"], "hello world")

@unittest.skipIf(SKIP_X_SERVER_TESTS, "Skipping tests that require X server")
class TestCommandExecutor(unittest.TestCase):
    """Test the command executor component."""
    
    @patch('pynput.mouse.Controller')
    @patch('pynput.keyboard.Controller')
    def setUp(self, mock_keyboard, mock_mouse):
        """Set up the test case."""
        self.mock_mouse = mock_mouse.return_value
        self.mock_keyboard = mock_keyboard.return_value
        self.executor = CommandExecutor(verbose=False)
        
    def test_execute_mouse_move(self):
        """Test executing mouse move commands."""
        command = {"type": "mouse", "action": "move", "x": 500, "y": 300}
        self.executor.execute(command)
        self.mock_mouse.position = (500, 300)
        
    def test_execute_mouse_click(self):
        """Test executing mouse click commands."""
        command = {"type": "mouse", "action": "click", "button": "left"}
        self.executor.execute(command)
        
    def test_execute_keyboard_type(self):
        """Test executing keyboard type commands."""
        command = {"type": "keyboard", "action": "type", "text": "hello world"}
        self.executor.execute(command)
        self.mock_keyboard.type.assert_called_with("hello world")

if __name__ == "__main__":
    unittest.main()
