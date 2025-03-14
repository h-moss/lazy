import speech_recognition as sr
import threading
import time
import os
from typing import Callable, Optional, Dict, Any

class TranscriberSR:
    """
    A transcriber implementation using the SpeechRecognition package.
    Provides the same interface as WhisperTranscriber for compatibility.
    """
    def __init__(self, 
                 model_name="whisper", 
                 device=None,
                 chunk_length_s=30,
                 batch_size=8,
                 return_timestamps=True,
                 verbose=False):
        """
        Initialize the TranscriberSR class.
        
        Args:
            model_name (str): Name of the recognition engine to use.
            device (str): Not used, kept for compatibility.
            chunk_length_s (int): Not used, kept for compatibility.
            batch_size (int): Not used, kept for compatibility.
            return_timestamps (bool): Not used, kept for compatibility.
            verbose (bool): Whether to print verbose output.
        """
        self.model_name = model_name
        self.verbose = verbose
        self.recognizer = sr.Recognizer()
        
        # Adjust recognition parameters
        self.recognizer.pause_threshold = 0.8
        self.recognizer.energy_threshold = 300
        
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
        # Convert waveform to AudioData
        audio_data = sr.AudioData(waveform.tobytes(), 
                                 sample_rate=16000, 
                                 sample_width=2)
        
        return self._recognize_audio(audio_data)
    
    def transcribe_file(self, audio_file):
        """
        Transcribe audio from a file.
        
        Args:
            audio_file (str): Path to audio file.
            
        Returns:
            dict: Transcription results.
        """
        with sr.AudioFile(audio_file) as source:
            audio_data = self.recognizer.record(source)
            
        return self._recognize_audio(audio_data)
    
    def _recognize_audio(self, audio_data):
        """
        Recognize speech in audio data.
        
        Args:
            audio_data: Audio data to recognize.
            
        Returns:
            dict: Transcription results.
        """
        try:
            if self.model_name == "whisper":
                text = self.recognizer.recognize_whisper(audio_data)
            elif self.model_name == "google":
                text = self.recognizer.recognize_google(audio_data)
            elif self.model_name == "sphinx":
                text = self.recognizer.recognize_sphinx(audio_data)
            else:
                # Default to whisper
                text = self.recognizer.recognize_whisper(audio_data)
                
            return {"text": text}
        except sr.UnknownValueError:
            return {"text": ""}
        except sr.RequestError as e:
            if self.verbose:
                print(f"Recognition error: {e}")
            return {"text": "", "error": str(e)}
        except Exception as e:
            if self.verbose:
                print(f"Error recognizing audio: {e}")
            return {"text": "", "error": str(e)}
    
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
                    
                    result = self._recognize_audio(audio)
                    
                    if result["text"]:
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
