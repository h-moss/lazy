import torch
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available

pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-large-v3",
    torch_dtype=torch.float16,
    device="mps" if torch.backends.mps.is_available() else "cpu",
    model_kwargs={"attn_implementation": "flash_attention_2"}
    if is_flash_attn_2_available()
    else {"attn_implementation": "sdpa"},
)


def transcribe(waveform):
    outputs = pipe(
        waveform,
        chunk_length_s=30,
        batch_size=24,
        return_timestamps=True,
    )

    return outputs
