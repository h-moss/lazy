#!/usr/bin/env python3
"""
Test script for the voice control system.
"""
import os
import time
import json
import unittest
import threading
from unittest.mock import MagicMock, patch

# Import components
from audio_capture import AudioCapture
from transcriber import WhisperTranscriber
from command_interpreter import CommandInterpreter
from command_executor import CommandExecutor
from voice_control_system import VoiceControlSystem
from optimized_voice_control import OptimizedVoiceControlSystem

class TestAudioCapture(unittest.TestCase):
    """Test the AudioCapture class."""
    
    @patch('pyaudio.PyAudio')
    def test_initialization(self, mock_pyaudio):
        """Test initialization of AudioCapture."""
        audio_capture = AudioCapture()
        self.assertIsNotNone(audio_capture)
        self.assertFalse(audio_capture.is_recording)
        
    @patch('pyaudio.PyAudio')
    def test_start_stop_stream(self, mock_pyaudio):
        """Test starting and stopping the audio stream."""
        audio_capture = AudioCapture()
        
        # Mock the stream
        mock_stream = MagicMock()
        mock_pyaudio.return_value.open.return_value = mock_stream
        
        # Start stream
        audio_capture.start_stream()
        mock_pyaudio.return_value.open.assert_called_once()
        mock_stream.start_stream.assert_called_once()
        
        # Stop stream
        audio_capture.stop_stream()
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()


class TestWhisperTranscriber(unittest.TestCase):
    """Test the WhisperTranscriber class."""
    
    @patch('transformers.pipeline')
    def test_initialization(self, mock_pipeline):
        """Test initialization of WhisperTranscriber."""
        transcriber = WhisperTranscriber(model_name="test_model")
        self.assertIsNotNone(transcriber)
        mock_pipeline.assert_called_once()
        
    @patch('transformers.pipeline')
    def test_transcribe(self, mock_pipeline):
        """Test transcription functionality."""
        # Mock the pipeline return value
        mock_pipeline.return_value.return_value = {"text": "test transcription"}
        
        transcriber = WhisperTranscriber(model_name="test_model")
        result = transcriber.transcribe("test_waveform")
        
        self.assertEqual(result["text"], "test transcription")
        mock_pipeline.return_value.assert_called_once()


class TestCommandInterpreter(unittest.TestCase):
    """Test the CommandInterpreter class."""
    
    @patch('llama_cpp.Llama')
    def test_initialization(self, mock_llama):
        """Test initialization of CommandInterpreter."""
        interpreter = CommandInterpreter(model_path="test_model")
        self.assertIsNotNone(interpreter)
        
    @patch('llama_cpp.Llama')
    def test_pattern_matching(self, mock_llama):
        """Test pattern matching for common commands."""
        interpreter = CommandInterpreter(model_path="test_model")
        
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


class TestCommandExecutor(unittest.TestCase):
    """Test the CommandExecutor class."""
    
    @patch('pynput.mouse.Controller')
    @patch('pynput.keyboard.Controller')
    def test_initialization(self, mock_keyboard, mock_mouse):
        """Test initialization of CommandExecutor."""
        executor = CommandExecutor()
        self.assertIsNotNone(executor)
        
    @patch('pynput.mouse.Controller')
    @patch('pynput.keyboard.Controller')
    def test_execute_mouse_move(self, mock_keyboard, mock_mouse):
        """Test executing a mouse move command."""
        executor = CommandExecutor()
        
        # Test mouse move
        command = {"type": "mouse", "action": "move", "x": 500, "y": 300}
        result = executor.execute(command)
        
        self.assertTrue(result)
        mock_mouse.return_value.position = (500, 300)
        
    @patch('pynput.mouse.Controller')
    @patch('pynput.keyboard.Controller')
    def test_execute_keyboard_press(self, mock_keyboard, mock_mouse):
        """Test executing a keyboard press command."""
        executor = CommandExecutor()
        
        # Test keyboard press
        command = {"type": "keyboard", "action": "press", "keys": ["ctrl", "c"]}
        result = executor.execute(command)
        
        self.assertTrue(result)
        # Verify keyboard controller was used
        self.assertTrue(mock_keyboard.return_value.press.called)
        self.assertTrue(mock_keyboard.return_value.release.called)


class TestVoiceControlSystem(unittest.TestCase):
    """Test the VoiceControlSystem class."""
    
    @patch('transcriber.WhisperTranscriber')
    @patch('command_interpreter.CommandInterpreter')
    @patch('command_executor.CommandExecutor')
    def test_initialization(self, mock_executor, mock_interpreter, mock_transcriber):
        """Test initialization of VoiceControlSystem."""
        system = VoiceControlSystem()
        self.assertIsNotNone(system)
        
    @patch('transcriber.WhisperTranscriber')
    @patch('command_interpreter.CommandInterpreter')
    @patch('command_executor.CommandExecutor')
    def test_start_stop(self, mock_executor, mock_interpreter, mock_transcriber):
        """Test starting and stopping the voice control system."""
        system = VoiceControlSystem()
        
        # Start system
        system.start()
        self.assertTrue(system.is_running)
        mock_transcriber.return_value.start_listening.assert_called_once()
        
        # Stop system
        system.stop()
        self.assertFalse(system.is_running)
        mock_transcriber.return_value.stop_listening.assert_called_once()
        
    @patch('transcriber.WhisperTranscriber')
    @patch('command_interpreter.CommandInterpreter')
    @patch('command_executor.CommandExecutor')
    def test_handle_transcription(self, mock_executor, mock_interpreter, mock_transcriber):
        """Test handling transcription results."""
        system = VoiceControlSystem()
        system.is_running = True
        
        # Mock interpreter to return a valid command
        mock_interpreter.return_value.interpret.return_value = {
            "type": "mouse", "action": "move", "x": 500, "y": 300
        }
        
        # Mock executor to return success
        mock_executor.return_value.execute.return_value = True
        
        # Call the handler with a test result
        system._handle_transcription({"text": "move mouse to 500, 300"})
        
        # Verify interpreter was called
        mock_interpreter.return_value.interpret.assert_called_once_with("move mouse to 500, 300")
        
        # Verify executor was called with the command
        mock_executor.return_value.execute.assert_called_once()


class TestOptimizedVoiceControlSystem(unittest.TestCase):
    """Test the OptimizedVoiceControlSystem class."""
    
    @patch('transcriber.WhisperTranscriber')
    @patch('command_interpreter.CommandInterpreter')
    @patch('command_executor.CommandExecutor')
    def test_initialization(self, mock_executor, mock_interpreter, mock_transcriber):
        """Test initialization of OptimizedVoiceControlSystem."""
        system = OptimizedVoiceControlSystem()
        self.assertIsNotNone(system)
        
    @patch('transcriber.WhisperTranscriber')
    @patch('command_interpreter.CommandInterpreter')
    @patch('command_executor.CommandExecutor')
    def test_command_caching(self, mock_executor, mock_interpreter, mock_transcriber):
        """Test command caching functionality."""
        system = OptimizedVoiceControlSystem()
        
        # Mock interpreter to return a valid command
        mock_interpreter.return_value.interpret.return_value = {
            "type": "mouse", "action": "move", "x": 500, "y": 300
        }
        
        # Add a command to the cache
        system.command_cache["move mouse to 500, 300"] = {
            "type": "mouse", "action": "move", "x": 500, "y": 300
        }
        
        # Start the system
        system.start()
        
        # Simulate a worker thread processing a cached command
        system.command_queue.put(("move mouse to 500, 300", time.time()))
        
        # Wait for processing
        time.sleep(0.1)
        
        # Stop the system
        system.stop()
        
        # Verify cache statistics
        stats = system.get_cache_stats()
        self.assertEqual(stats["cache_size"], 1)


class TestEndToEnd(unittest.TestCase):
    """End-to-end tests for the voice control system."""
    
    @patch('audio_capture.AudioCapture')
    @patch('transcriber.WhisperTranscriber.transcribe_file')
    @patch('command_interpreter.CommandInterpreter.interpret')
    @patch('command_executor.CommandExecutor.execute')
    def test_end_to_end_flow(self, mock_execute, mock_interpret, mock_transcribe, mock_audio):
        """Test the end-to-end flow from audio to command execution."""
        # Mock the transcription result
        mock_transcribe.return_value = {"text": "move mouse to 500, 300"}
        
        # Mock the interpretation result
        mock_interpret.return_value = {"type": "mouse", "action": "move", "x": 500, "y": 300}
        
        # Mock the execution result
        mock_execute.return_value = True
        
        # Create a system instance
        system = VoiceControlSystem(verbose=True)
        
        # Start the system
        system.start()
        
        # Simulate audio capture and transcription
        callback = mock_audio.return_value.start_stream.call_args[0][0]
        callback({"text": "move mouse to 500, 300"})
        
        # Wait for processing
        time.sleep(0.1)
        
        # Stop the system
        system.stop()
        
        # Verify the flow
        mock_interpret.assert_called_with("move mouse to 500, 300")
        mock_execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
