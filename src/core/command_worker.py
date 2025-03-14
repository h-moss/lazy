import threading
import queue
import time
from typing import Dict, Any, Optional

class CommandWorker:
    """Worker thread for processing commands."""
    
    def __init__(self, interpreter, executor, verbose=False):
        self.interpreter = interpreter
        self.executor = executor
        self.verbose = verbose
        self.command_queue = queue.Queue()
        self.is_running = False
        self.workers = []
        self.command_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_size = 100
        
    def start(self, max_workers=2):
        self.is_running = True
        for i in range(max_workers):
            worker = threading.Thread(
                target=self._worker_thread,
                name=f"CommandWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
            
    def stop(self):
        self.is_running = False
        for _ in range(len(self.workers)):
            self.command_queue.put(None)
            
        for worker in self.workers:
            worker.join(timeout=1.0)
            
        self.workers = []
        
    def add_command(self, text, timestamp):
        self.command_queue.put((text, timestamp))
        
    def _worker_thread(self):
        while self.is_running:
            try:
                item = self.command_queue.get(timeout=0.5)
                
                if item is None:
                    break
                    
                text, timestamp = item
                
                if text in self.command_cache:
                    command = self.command_cache[text]
                    self.cache_hits += 1
                    if self.verbose:
                        print(f"Cache hit: {text}")
                else:
                    command = self.interpreter.interpret(text)
                    self.cache_misses += 1
                    
                    if "error" not in command and len(self.command_cache) < self.cache_size:
                        self.command_cache[text] = command
                        
                if "error" not in command:
                    self.executor.execute(command)
                    
                if self.verbose:
                    if "error" in command:
                        print(f"Error: {command['error']}")
                    else:
                        print(f"Executed command: {text}")
                        
            except queue.Empty:
                continue
            except Exception as e:
                if self.verbose:
                    print(f"Error in command worker: {e}")
                    
    def get_cache_stats(self):
        total_commands = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_commands) * 100 if total_commands > 0 else 0
        
        return {
            "cache_size": len(self.command_cache),
            "max_cache_size": self.cache_size,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate
        }
