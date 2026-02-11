import uuid
import os
from TTS.api import TTS

# Load once (important)
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")

AUDIO_DIR = "backend/app/frontend/static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def synthesize_speech(text: str) -> str:
    filename = f"{uuid.uuid4()}.wav"
    filepath = os.path.join(AUDIO_DIR, filename)

    tts.tts_to_file(text=text, file_path=filepath)

    return f"/static/audio/{filename}"