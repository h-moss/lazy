import speech_recognition as sr
import threading
import time
import os
from typing import Callable, Optional, Dict, Any
import torch
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available

class Transcriber:
    """
    A unified transcriber that uses SpeechRecognition for microphone input
    and Whisper for transcription.
    """
    def __init__(self, verbose=False):
        """
        Initialize the Transcriber.
        
        Args:
            verbose (bool): Whether to print verbose output.
        """
        self.verbose = verbose
        self.recognizer = sr.Recognizer()
        
        # Adjust recognition parameters
        self.recognizer.pause_threshold = 0.8
        self.recognizer.energy_threshold = 300
        
        # Initialize Whisper pipeline
        device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-small",
            torch_dtype=torch.float16 if device != "cpu" else torch.float32,
            device=device,
            model_kwargs={"attn_implementation": "flash_attention_2"}
            if is_flash_attn_2_available() and device == "cuda"
            else {"attn_implementation": "sdpa"},
        )
        
        self.is_listening = False
        self.listening_thread = None
        self.transcription_callback = None
        
    def transcribe(self, waveform):
        """
        Transcribe audio waveform to text using Whisper.
        
        Args:
            waveform: Audio waveform to transcribe.
            
        Returns:
            dict: Transcription results.
        """
        try:
            outputs = self.pipe(
                waveform,
                chunk_length_s=30,
                batch_size=8,
                return_timestamps=True,
            )
            return outputs
        except Exception as e:
            if self.verbose:
                print(f"Error transcribing audio: {e}")
            return {"text": "", "error": str(e)}
    
    def transcribe_file(self, audio_file):
        """
        Transcribe audio from a file using Whisper.
        
        Args:
            audio_file (str): Path to audio file.
            
        Returns:
            dict: Transcription results.
        """
        try:
            return self.pipe(audio_file)
        except Exception as e:
            if self.verbose:
                print(f"Error transcribing file: {e}")
            return {"text": "", "error": str(e)}
    
    def start_listening(self, callback=None):
        """
        Start listening for audio using SpeechRecognition and transcribe with Whisper.
        
        Args:
            callback (callable): Function to call with transcription results.
        """
        if self.is_listening:
            return
            
        self.is_listening = True
        self.transcription_callback = callback
        
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
            
    def _listening_worker(self):
        """Worker thread for listening and transcribing audio."""
        while self.is_listening:
            try:
                with sr.Microphone() as source:
                    if self.verbose:
                        print("Adjusting for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    if self.verbose:
                        print("Listening...")
                    audio = self.recognizer.listen(source, 
                                                  timeout=5.0, 
                                                  phrase_time_limit=10.0)
                    
                    if self.verbose:
                        print("Processing audio...")
                    
                    # Convert audio data to numpy array for Whisper
                    audio_data = audio.get_raw_data()
                    import numpy as np
                    waveform = np.frombuffer(audio_data, np.int16).astype(np.float32) / 32768.0
                    
                    # Transcribe with Whisper
                    result = self.transcribe(waveform)
                    
                    if result.get("text", ""):
                        if self.verbose:
                            print(f"Transcription: {result['text']}")
                            
                        # Call callback with result
                        if self.transcription_callback is not None:
                            self.transcription_callback(result)
                
            except sr.WaitTimeoutError:
                if self.verbose:
                    print("Timeout waiting for phrase to start")
            except Exception as e:
                if self.verbose:
                    print(f"Error in listening worker: {e}")
                time.sleep(0.5)  # Prevent tight loop on error


# Example usage
if __name__ == "__main__":
    def print_transcription(result):
        print(f"Transcribed: {result['text']}")
        
    # Initialize transcriber
    transcriber = Transcriber(verbose=True)
    
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
