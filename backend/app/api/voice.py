from fastapi import APIRouter, UploadFile, File
import uuid, os

from backend.app.services.stt import transcribe
from backend.app.services.command_parser import parse_command
from backend.app.db.session import SessionLocal
from backend.app.services.command_executor import execute_command
from backend.app.services.confirmation_state import (
    set_pending_command,
    get_pending_command,
    clear_pending_command
)
from backend.app.services.tts import synthesize_speech
router = APIRouter(prefix="/voice", tags=["voice"])

UPLOAD_DIR = "voice_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_voice(file: UploadFile = File(...)):
    filename = f"{uuid.uuid4()}.webm"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(await file.read())

    # 1. Speech → text
    text = transcribe(filepath)

    # 2. Text → command
    command = parse_command(text)

    # 3. Build result for every intent path
    if command.get("intent") == "undo":
        db = SessionLocal()
        result = execute_command(command, db)
        db.close()

    elif command.get("intent") == "confirm":
        pending = get_pending_command()

        if not pending:
            result = {
                "status": "ignored",
                "message": "Nothing to confirm"
            }
        else:
            db = SessionLocal()
            result = execute_command(pending, db)
            db.close()
            clear_pending_command()

    else:
        # 4. Normal command → execute once
        db = SessionLocal()
        execution_result = execute_command(command, db)
        db.close()

        # 5. If executor asks for confirmation
        if execution_result.get("status") in {"needs_confirmation", "pending"}:
            # If executor suggests an update, store THAT instead
            if execution_result.get("intent") == "update_price":
                set_pending_command({
                    "intent": "update_price",
                    "data": execution_result.get("data")
                })
                result = {
                    "status": "pending",
                    "message": execution_result.get("message")
                }
            else:
                set_pending_command(command)
                result = {
                    "status": "pending",
                    "message": "Please confirm the action"
                }
        else:
            result = execution_result

    speech_url = None
    if result.get("message"):
        speech_url = synthesize_speech(result["message"])
    
    return {
        "message": "Audio received",
        "filename": filename,
        "text": text,
        "command": command,
        "result": result,
        "speech_url": speech_url
    }
