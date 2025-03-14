import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.simplified_transcriber import SimplifiedTranscriber

class TestSimplifiedTranscriber(unittest.TestCase):
    """Test the simplified transcriber."""
    
    @patch('torch.cuda.is_available')
    @patch('torch.backends.mps.is_available')
    @patch('speech_recognition.Recognizer')
    def test_init(self, mock_recognizer, mock_mps_available, mock_cuda_available):
        """Test initialization."""
        # Mock hardware availability
        mock_cuda_available.return_value = False
        mock_mps_available.return_value = False
        
        # Create mock recognizer
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        
        # Create SimplifiedTranscriber
        transcriber = SimplifiedTranscriber(verbose=True)
        
        # Check initialization
        self.assertIsNotNone(transcriber)
        self.assertTrue(transcriber.verbose)
        self.assertFalse(transcriber.is_listening)
        
    @patch('transformers.pipeline')
    @patch('speech_recognition.Recognizer')
    def test_transcribe_file(self, mock_recognizer, mock_pipeline):
        """Test transcribing from a file."""
        # Create mock pipeline
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.return_value = {"text": "test transcription"}
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Create SimplifiedTranscriber
        transcriber = SimplifiedTranscriber()
        
        # Mock the pipeline call
        transcriber.pipe = MagicMock()
        transcriber.pipe.return_value = {"text": "test transcription"}
        
        # Test transcribe_file
        result = transcriber.transcribe_file("test.wav")
        
        # Check result
        self.assertEqual(result["text"], "test transcription")
        
    @patch('transformers.pipeline')
    @patch('speech_recognition.Recognizer')
    def test_transcribe_error(self, mock_recognizer, mock_pipeline):
        """Test error handling in transcribe."""
        # Create SimplifiedTranscriber
        transcriber = SimplifiedTranscriber(verbose=True)
        
        # Mock the pipeline call to raise an exception
        transcriber.pipe = MagicMock()
        transcriber.pipe.side_effect = Exception("Test error")
        
        # Test transcribe with error
        result = transcriber.transcribe(b"dummy audio data")
        
        # Check result
        self.assertEqual(result["text"], "")
        self.assertEqual(result["error"], "Test error")
        
    @patch('speech_recognition.Microphone')
    @patch('transformers.pipeline')
    @patch('speech_recognition.Recognizer')
    def test_start_stop_listening(self, mock_recognizer, mock_pipeline, mock_microphone):
        """Test starting and stopping listening."""
        # Create mock recognizer
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        
        # Create SimplifiedTranscriber
        transcriber = SimplifiedTranscriber()
        
        # Mock the listening thread
        with patch.object(transcriber, '_listening_worker') as mock_worker:
            # Start listening
            callback = MagicMock()
            transcriber.start_listening(callback=callback)
            
            # Check state
            self.assertTrue(transcriber.is_listening)
            self.assertEqual(transcriber.transcription_callback, callback)
            
            # Stop listening
            transcriber.stop_listening()
            
            # Check state
            self.assertFalse(transcriber.is_listening)

if __name__ == "__main__":
    unittest.main()
