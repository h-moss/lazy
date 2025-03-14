import time
from typing import Dict, Any, Optional

from src.core.transcriber import WhisperTranscriber
from src.core.command_interpreter import CommandInterpreter
from src.core.command_executor import CommandExecutor
from src.core.command_worker import CommandWorker

class OptimizedVoiceControlSystem:
    """An optimized voice-controlled system with improved performance."""
    
    def __init__(self, whisper_model="openai/whisper-tiny", llm_model_path=None, 
                 verbose=False, cache_size=100, max_workers=2):
        self.verbose = verbose
        
        self.transcriber = WhisperTranscriber(
            model_name=whisper_model,
            chunk_length_s=5,
            batch_size=4
        )
        
        self.interpreter = CommandInterpreter(
            model_path=llm_model_path,
            verbose=verbose
        )
        
        self.executor = CommandExecutor(verbose=verbose)
        
        self.command_worker = CommandWorker(
            interpreter=self.interpreter,
            executor=self.executor,
            verbose=verbose
        )
        
        self.is_running = False
        self.last_command_time = 0
        self.command_cooldown = 0.5
        self.max_workers = max_workers
        
    def start(self):
        """Start the voice control system."""
        if self.is_running:
            return
            
        self.is_running = True
        self.command_worker.start(self.max_workers)
        self.transcriber.start_listening(callback=self._handle_transcription)
        
        print("\nOptimized voice control system is now running!")
        print("Speak commands into your microphone.")
        
    def stop(self):
        """Stop the voice control system."""
        if not self.is_running:
            return
            
        self.is_running = False
        self.transcriber.stop_listening()
        self.command_worker.stop()
        
        print("\nOptimized voice control system stopped.")
        
    def _handle_transcription(self, result):
        """Handle transcription results from Whisper."""
        if not self.is_running:
            return
            
        text = result.get('text', '').strip()
        if not text:
            return
            
        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            return
            
        self.last_command_time = current_time
        print(f"\nTranscribed: {text}")
        
        self.command_worker.add_command(text, current_time)
        
    def get_cache_stats(self):
        """Get command cache statistics."""
        return self.command_worker.get_cache_stats()


def main():
    """Main function to run the optimized voice control system."""
    print("Initializing optimized voice control system...")
    
    system = OptimizedVoiceControlSystem(
        whisper_model="openai/whisper-tiny",
        verbose=True,
        cache_size=100,
        max_workers=2
    )
    
    system.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping optimized voice control system...")
    finally:
        system.stop()


if __name__ == "__main__":
    main()
