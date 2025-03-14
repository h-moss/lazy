#!/usr/bin/env python3
"""
Script to download LLM model from Hugging Face for the voice control system.
"""
import os
import argparse
from huggingface_hub import hf_hub_download
from transformers import pipeline

def main():
    """Download LLM model from Hugging Face."""
    parser = argparse.ArgumentParser(description='Download LLM model from Hugging Face')
    parser.add_argument('--llm-model', type=str, default='TheBloke/Llama-2-7B-GGML',
                        help='LLM model to download (default: TheBloke/Llama-2-7B-GGML)')
    parser.add_argument('--llm-file', type=str, default='llama-2-7b.ggmlv3.q4_0.bin',
                        help='Specific LLM model file to download')
    parser.add_argument('--output-dir', type=str, default='models',
                        help='Directory to save models (default: models)')
    parser.add_argument('--preload-whisper', action='store_true',
                        help='Preload Whisper model to cache')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Download LLM model
    print(f"Downloading LLM model {args.llm_model}/{args.llm_file}...")
    llm_path = hf_hub_download(
        repo_id=args.llm_model,
        filename=args.llm_file,
        cache_dir=args.output_dir
    )
    print(f"Downloaded LLM model to: {llm_path}")
    
    # Create a symlink for easier access
    symlink_path = os.path.join(args.output_dir, "llm_model.bin")
    if os.path.exists(symlink_path):
        os.remove(symlink_path)
    os.symlink(llm_path, symlink_path)
    print(f"Created symlink at: {symlink_path}")
    
    # Optionally preload Whisper model
    if args.preload_whisper:
        print("Preloading Whisper model to cache...")
        # This will download the model to the cache
        _ = pipeline("automatic-speech-recognition", model="openai/whisper-small")
        print("Whisper model cached successfully")
    
    print("Model download complete!")

if __name__ == "__main__":
    main()
