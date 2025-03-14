import os
import time
from transcriber import WhisperTranscriber

def main():
    """
    Main function to demonstrate Whisper transcription setup.
    """
    print("Setting up Whisper transcription system...")
    
    # Initialize the transcriber with a smaller model for faster processing
    transcriber = WhisperTranscriber(
        model_name="openai/whisper-small",  # Use smaller model for faster processing
        chunk_length_s=10,                  # Smaller chunks for lower latency
        batch_size=4                        # Adjust based on available memory
    )
    
    # Define callback function for transcription results
    def handle_transcription(result):
        text = result.get('text', '').strip()
        if text:
            print(f"\nTranscribed: {text}")
            print("Ready for next command...")
    
    # Start listening for audio
    print("\nInitializing audio capture...")
    transcriber.start_listening(callback=handle_transcription)
    
    print("\nWhisper transcription system is ready!")
    print("Speak into your microphone to test the system.")
    print("Your spoken commands will be transcribed to text.")
    print("Press Ctrl+C to exit.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping Whisper transcription system...")
    finally:
        # Clean up
        transcriber.stop_listening()
        print("Whisper transcription system stopped.")

if __name__ == "__main__":
    main()
