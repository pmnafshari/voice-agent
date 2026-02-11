from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu")

def transcribe(audio_path: str) -> str:
    segments, _ = model.transcribe(audio_path)
    text = " ".join(segment.text for segment in segments)
    return text.strip()