import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.transcriber_sr import TranscriberSR

class TestTranscriberSR(unittest.TestCase):
    """Test the SpeechRecognition-based transcriber."""
    
    @patch('speech_recognition.Recognizer')
    def test_init(self, mock_recognizer):
        """Test initialization."""
        # Create mock recognizer
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        
        # Create TranscriberSR
        transcriber = TranscriberSR(verbose=True)
        
        # Check initialization
        self.assertIsNotNone(transcriber)
        self.assertEqual(transcriber.model_name, "whisper")
        self.assertTrue(transcriber.verbose)
        self.assertFalse(transcriber.is_listening)
        
    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.AudioFile')
    def test_transcribe_file(self, mock_audio_file, mock_recognizer):
        """Test transcribing from a file."""
        # Create mock recognizer
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        
        # Mock recognize_whisper
        mock_recognizer_instance.recognize_whisper.return_value = "test transcription"
        
        # Create TranscriberSR
        transcriber = TranscriberSR()
        
        # Test transcribe_file
        result = transcriber.transcribe_file("test.wav")
        
        # Check result
        self.assertEqual(result["text"], "test transcription")
        
    @patch('speech_recognition.Recognizer')
    def test_recognize_audio_error(self, mock_recognizer):
        """Test error handling in recognize_audio."""
        # Create mock recognizer
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        
        # Mock recognize_whisper to raise an exception
        mock_recognizer_instance.recognize_whisper.side_effect = Exception("Test error")
        
        # Create TranscriberSR
        transcriber = TranscriberSR(verbose=True)
        
        # Create mock audio data
        mock_audio_data = MagicMock()
        
        # Test _recognize_audio
        result = transcriber._recognize_audio(mock_audio_data)
        
        # Check result
        self.assertEqual(result["text"], "")
        self.assertEqual(result["error"], "Test error")

if __name__ == "__main__":
    unittest.main()
