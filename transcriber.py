import torch
import numpy as np
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available
from audio_capture import AudioCapture
import threading
import time
import json
import os

class WhisperTranscriber:
    """
    A class to transcribe audio using OpenAI's Whisper model.
    """
    def __init__(self, 
                 model_name="openai/whisper-small",
                 device=None,
                 chunk_length_s=30,
                 batch_size=8,
                 return_timestamps=True):
        """
        Initialize the WhisperTranscriber class.
        
        Args:
            model_name (str): Name of the Whisper model to use.
            device (str): Device to use for inference (cpu, cuda, mps).
            chunk_length_s (int): Length of audio chunks in seconds.
            batch_size (int): Batch size for processing.
            return_timestamps (bool): Whether to return timestamps.
        """
        # Determine device
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        
        # Set up the pipeline
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            torch_dtype=torch.float16 if device != "cpu" else torch.float32,
            device=device,
            model_kwargs={"attn_implementation": "flash_attention_2"}
            if is_flash_attn_2_available() and device == "cuda"
            else {"attn_implementation": "sdpa"},
        )
        
        self.chunk_length_s = chunk_length_s
        self.batch_size = batch_size
        self.return_timestamps = return_timestamps
        self.audio_capture = None
        self.is_listening = False
        self.listening_thread = None
        self.transcription_callback = None
        
    def transcribe(self, waveform):
        """
        Transcribe audio waveform to text.
        
        Args:
            waveform: Audio waveform to transcribe.
            
        Returns:
            dict: Transcription results.
        """
        outputs = self.pipe(
            waveform,
            chunk_length_s=self.chunk_length_s,
            batch_size=self.batch_size,
            return_timestamps=self.return_timestamps,
        )
        
        return outputs
    
    def transcribe_file(self, audio_file):
        """
        Transcribe audio from a file.
        
        Args:
            audio_file (str): Path to audio file.
            
        Returns:
            dict: Transcription results.
        """
        return self.pipe(audio_file)
    
    def start_listening(self, callback=None):
        """
        Start listening for audio and transcribing in real-time.
        
        Args:
            callback (callable): Function to call with transcription results.
        """
        if self.is_listening:
            return
            
        self.is_listening = True
        self.transcription_callback = callback
        
        # Initialize audio capture if not already done
        if self.audio_capture is None:
            self.audio_capture = AudioCapture()
            
        # Start audio stream
        self.audio_capture.start_stream()
        
        # Start listening thread
        self.listening_thread = threading.Thread(target=self._listening_worker)
        self.listening_thread.daemon = True
        self.listening_thread.start()
        
    def stop_listening(self):
        """Stop listening for audio."""
        self.is_listening = False
        if self.listening_thread is not None:
            self.listening_thread.join(timeout=1.0)
            self.listening_thread = None
            
        if self.audio_capture is not None:
            self.audio_capture.stop_stream()
            
    def _listening_worker(self):
        """Worker thread for listening and transcribing audio."""
        temp_file = "temp_audio.wav"
        
        while self.is_listening:
            # Wait for voice activity
            if self.audio_capture is None or not self.audio_capture.is_recording:
                time.sleep(0.1)
                continue
                
            # Wait for recording to complete
            while self.audio_capture is not None and self.audio_capture.is_recording and self.is_listening:
                time.sleep(0.1)
                
            # Save audio to temporary file
            if self.audio_capture is not None and self.audio_capture.save_audio(temp_file):
                try:
                    # Transcribe audio
                    result = self.transcribe_file(temp_file)
                    
                    # Call callback with result
                    if self.transcription_callback is not None:
                        self.transcription_callback(result)
                        
                    print(f"Transcription: {result['text']}")
                except Exception as e:
                    print(f"Error transcribing audio: {e}")
                    
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
    def __del__(self):
        """Clean up resources."""
        self.stop_listening()
        if self.audio_capture is not None:
            del self.audio_capture


# Example usage
if __name__ == "__main__":
    def print_transcription(result):
        print(f"Transcribed: {result['text']}")
        
    # Initialize transcriber
    transcriber = WhisperTranscriber(model_name="openai/whisper-small")
    
    # Start listening
    print("Listening for speech... (Press Ctrl+C to stop)")
    transcriber.start_listening(callback=print_transcription)
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        # Clean up
        transcriber.stop_listening()
