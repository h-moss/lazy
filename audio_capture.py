import pyaudio
import numpy as np
import wave
import threading
import queue
import time
from collections import deque

class AudioCapture:
    """
    A class to capture audio from the microphone in real-time.
    """
    def __init__(self, 
                 rate=16000, 
                 chunk_size=1024, 
                 channels=1, 
                 format=pyaudio.paInt16,
                 vad_threshold=0.01,
                 silence_duration=1.0):
        """
        Initialize the AudioCapture class.
        
        Args:
            rate (int): Sample rate of the audio.
            chunk_size (int): Number of frames per buffer.
            channels (int): Number of channels.
            format: Audio format.
            vad_threshold (float): Threshold for voice activity detection.
            silence_duration (float): Duration of silence to consider speech ended.
        """
        self.rate = rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.format = format
        self.vad_threshold = vad_threshold
        self.silence_duration = silence_duration
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.audio_buffer = deque(maxlen=int(rate * 5))  # 5 seconds buffer
        self.recording_thread = None
        
    def start_stream(self):
        """Start the audio stream."""
        if self.stream is not None and not self.stream.is_stopped():
            return
            
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._audio_callback
        )
        self.stream.start_stream()
        
    def stop_stream(self):
        """Stop the audio stream."""
        if self.stream is not None and not self.stream.is_stopped():
            self.stream.stop_stream()
            self.stream.close()
        self.stream = None
        
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for the audio stream."""
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        self.audio_buffer.extend(audio_data)
        
        # Check for voice activity
        if self.is_recording:
            self.audio_queue.put(in_data)
        else:
            # Simple voice activity detection
            energy = np.abs(audio_data).mean()
            if energy > self.vad_threshold * 32768:  # 32768 is max value for int16
                self.start_recording()
                
        return (in_data, pyaudio.paContinue)
    
    def start_recording(self):
        """Start recording audio."""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._recording_worker)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        # Add the buffer to the queue
        for chunk in self.get_buffer_chunks():
            self.audio_queue.put(chunk)
            
    def stop_recording(self):
        """Stop recording audio."""
        self.is_recording = False
        if self.recording_thread is not None:
            self.recording_thread.join(timeout=1.0)
            self.recording_thread = None
        
    def _recording_worker(self):
        """Worker thread for recording audio."""
        silence_chunks = 0
        required_silence_chunks = int(self.silence_duration * self.rate / self.chunk_size)
        
        while self.is_recording:
            try:
                data = self.audio_queue.get(timeout=0.1)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Check for silence
                energy = np.abs(audio_data).mean()
                if energy < self.vad_threshold * 32768:
                    silence_chunks += 1
                    if silence_chunks >= required_silence_chunks:
                        self.is_recording = False
                        break
                else:
                    silence_chunks = 0
                    
            except queue.Empty:
                continue
                
    def get_buffer_chunks(self):
        """Get the audio buffer as chunks."""
        buffer_array = np.array(list(self.audio_buffer), dtype=np.int16)
        num_chunks = len(buffer_array) // self.chunk_size
        
        chunks = []
        for i in range(num_chunks):
            start = i * self.chunk_size
            end = start + self.chunk_size
            chunk = buffer_array[start:end].tobytes()
            chunks.append(chunk)
            
        return chunks
    
    def get_audio_data(self):
        """Get all recorded audio data."""
        data = []
        while not self.audio_queue.empty():
            data.append(self.audio_queue.get())
        return b''.join(data)
    
    def save_audio(self, filename):
        """Save the recorded audio to a file."""
        audio_data = self.get_audio_data()
        if not audio_data:
            return False
            
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(audio_data)
        return True
    
    def __del__(self):
        """Clean up resources."""
        self.stop_stream()
        self.audio.terminate()
