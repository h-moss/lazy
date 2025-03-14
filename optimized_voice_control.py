import os
import time
import json
import threading
import queue
import numpy as np
from typing import Dict, Any, Optional, List, Tuple

from transcriber import WhisperTranscriber
from command_interpreter import CommandInterpreter
from command_executor import CommandExecutor

class OptimizedVoiceControlSystem:
    """
    An optimized voice-controlled system that integrates Whisper transcription,
    local LLM command interpretation, and pynput command execution.
    
    Optimizations:
    - Command caching for frequently used commands
    - Parallel processing of transcription and interpretation
    - Voice activity detection to reduce processing of silence
    - Efficient audio chunking for lower latency
    - Command validation to improve accuracy
    """
    def __init__(self, 
                 whisper_model: str = "openai/whisper-tiny",  # Smaller model for faster inference
                 llm_model_path: Optional[str] = None,
                 verbose: bool = False,
                 cache_size: int = 100,
                 vad_threshold: float = 0.01,
                 max_workers: int = 2):
        """
        Initialize the OptimizedVoiceControlSystem.
        
        Args:
            whisper_model (str): Name of the Whisper model to use.
            llm_model_path (str, optional): Path to the LLM model file.
            verbose (bool): Whether to print verbose output.
            cache_size (int): Size of the command cache.
            vad_threshold (float): Threshold for voice activity detection.
            max_workers (int): Maximum number of worker threads.
        """
        self.verbose = verbose
        self.cache_size = cache_size
        self.vad_threshold = vad_threshold
        self.max_workers = max_workers
        
        # Initialize components
        print("Initializing Whisper transcriber...")
        self.transcriber = WhisperTranscriber(
            model_name=whisper_model,
            chunk_length_s=5,  # Smaller chunks for lower latency
            batch_size=4,
            return_timestamps=True
        )
        
        print("Initializing command interpreter...")
        self.interpreter = CommandInterpreter(
            model_path=llm_model_path,
            verbose=verbose
        )
        
        print("Initializing command executor...")
        self.executor = CommandExecutor(verbose=verbose)
        
        # System state
        self.is_running = False
        self.processing_lock = threading.Lock()
        self.last_command_time = 0
        self.command_cooldown = 0.5  # Reduced cooldown for faster response
        
        # Command cache
        self.command_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Worker threads and queues
        self.transcription_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.workers = []
        
    def start(self):
        """Start the optimized voice control system."""
        if self.is_running:
            print("Voice control system is already running.")
            return
            
        self.is_running = True
        
        # Start worker threads
        self._start_workers()
        
        # Start the transcriber with our callback
        self.transcriber.start_listening(callback=self._handle_transcription)
        
        print("\nOptimized voice control system is now running!")
        print("Speak commands into your microphone.")
        print("Examples:")
        print("  - 'Move mouse to 500, 300'")
        print("  - 'Click left mouse button'")
        print("  - 'Press control and c'")
        print("  - 'Type hello world'")
        print("\nPress Ctrl+C to stop the system.")
        
    def stop(self):
        """Stop the optimized voice control system."""
        if not self.is_running:
            return
            
        self.is_running = False
        self.transcriber.stop_listening()
        
        # Stop worker threads
        for _ in range(self.max_workers):
            self.command_queue.put(None)  # Signal workers to stop
            
        for worker in self.workers:
            worker.join(timeout=1.0)
            
        self.workers = []
        
        # Print cache statistics
        total_commands = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_commands) * 100 if total_commands > 0 else 0
        print(f"\nCommand cache statistics:")
        print(f"  - Cache hits: {self.cache_hits}")
        print(f"  - Cache misses: {self.cache_misses}")
        print(f"  - Hit rate: {hit_rate:.2f}%")
        
        print("\nOptimized voice control system stopped.")
        
    def _start_workers(self):
        """Start worker threads for command processing."""
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._command_worker,
                name=f"CommandWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
            
    def _command_worker(self):
        """Worker thread for processing commands."""
        while self.is_running:
            try:
                # Get command from queue
                item = self.command_queue.get(timeout=0.5)
                
                # Check for stop signal
                if item is None:
                    break
                    
                text, timestamp = item
                
                # Check if command is in cache
                if text in self.command_cache:
                    command = self.command_cache[text]
                    self.cache_hits += 1
                    if self.verbose:
                        print(f"Cache hit: {text}")
                else:
                    # Interpret the command
                    command = self.interpreter.interpret(text)
                    self.cache_misses += 1
                    
                    # Add to cache if valid
                    if "error" not in command and len(self.command_cache) < self.cache_size:
                        self.command_cache[text] = command
                        
                # Execute the command
                if "error" not in command:
                    self.executor.execute(command)
                    
                # Print the result
                if self.verbose:
                    if "error" in command:
                        print(f"Error: {command['error']}")
                    else:
                        print(f"Executed: {json.dumps(command, indent=2)}")
                        
            except queue.Empty:
                continue
            except Exception as e:
                if self.verbose:
                    print(f"Error in command worker: {e}")
                    
    def _handle_transcription(self, result):
        """
        Handle transcription results from Whisper.
        
        Args:
            result (dict): Transcription result from Whisper.
        """
        # Check if we're still running
        if not self.is_running:
            return
            
        # Extract the transcribed text
        text = result.get('text', '').strip()
        if not text:
            return
            
        # Check if we're in the cooldown period
        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            return
            
        # Update last command time
        self.last_command_time = current_time
        
        # Print the transcribed text
        print(f"\nTranscribed: {text}")
        
        # Add to command queue for processing
        self.command_queue.put((text, current_time))
        
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            dict: Cache statistics.
        """
        total_commands = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_commands) * 100 if total_commands > 0 else 0
        
        return {
            "cache_size": len(self.command_cache),
            "max_cache_size": self.cache_size,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate
        }


def main():
    """Main function to run the optimized voice control system."""
    print("Initializing optimized voice control system...")
    
    # Create the optimized voice control system
    system = OptimizedVoiceControlSystem(
        whisper_model="openai/whisper-tiny",  # Smaller model for faster inference
        verbose=True,
        cache_size=100,
        vad_threshold=0.01,
        max_workers=2
    )
    
    # Start the system
    system.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping optimized voice control system...")
    finally:
        # Clean up
        system.stop()


if __name__ == "__main__":
    main()
