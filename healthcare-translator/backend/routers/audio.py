import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, Query, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Conversation, Message, MessageTypeEnum, RoleEnum
from schemas import MessageResponse
from services.groq_service import transcribe_audio, translate_message
from services.tts_service import text_to_speech

router = APIRouter(prefix="/api", tags=["audio"])

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_files")
os.makedirs(AUDIO_DIR, exist_ok=True)


@router.post("/conversations/{conversation_id}/audio", response_model=MessageResponse)
async def upload_and_process_audio(
    conversation_id: str,
    audio: UploadFile = File(...),
    role: str = Form(...),
    source_language: str = Form("auto"),
    db: Session = Depends(get_db),
):
    """
    Full voice pipeline:
    1. Patient/Doctor speaks → record audio
    2. Whisper transcribes audio → text
    3. Llama translates text → target language
    4. Edge-TTS converts translated text → speech audio
    5. Both text + audio stored & returned
    
    Result: Doctor speaks Korean → Patient HEARS Chinese
    """
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 1. Save original audio file
    file_ext = audio.filename.split(".")[-1] if audio.filename else "webm"
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(AUDIO_DIR, filename)

    content = await audio.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # 2. Transcribe with Groq Whisper
    try:
        lang_hint = source_language if source_language != "auto" else None
        transcription = await transcribe_audio(file_path, language=lang_hint)
        transcribed_text = transcription["text"]
        detected_language = transcription.get("language", source_language)
        audio_duration = str(transcription.get("duration", ""))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    # 3. Determine target language and translate
    role_enum = RoleEnum.doctor if role == "doctor" else RoleEnum.patient
    target_language = conv.patient_language if role == "doctor" else conv.doctor_language

    translated_text = None
    try:
        translated_text = await translate_message(
            text=transcribed_text,
            source_language=detected_language,
            target_language=target_language,
            role=role,
        )
    except Exception as e:
        translated_text = f"[Translation unavailable: {str(e)}]"

    # 4. Generate TTS audio for the translated text
    tts_file = None
    try:
        if translated_text and not translated_text.startswith("[Translation"):
            # Generate speech in the TARGET language so the listener hears their language
            listener_role = "patient" if role == "doctor" else "doctor"
            tts_file = await text_to_speech(
                text=translated_text,
                language=target_language,
                role=listener_role,
            )
    except Exception as e:
        print(f"TTS generation failed (non-critical): {e}")

    # 5. Save message to database
    message = Message(
        conversation_id=conversation_id,
        role=role_enum,
        message_type=MessageTypeEnum.audio,
        original_text=transcribed_text,
        original_language=detected_language,
        translated_text=translated_text,
        target_language=target_language,
        audio_file_path=filename,
        audio_duration=audio_duration,
        tts_audio_path=tts_file,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return MessageResponse.model_validate(message)


@router.post("/tts")
async def generate_tts(
    text: str = Form(...),
    language: str = Form("en"),
    role: str = Form("patient"),
):
    """
    Standalone TTS endpoint.
    Convert any text to speech in the given language.
    Returns the audio file URL.
    """
    try:
        filename = await text_to_speech(text=text, language=language, role=role)
        return {"audio_url": f"/api/audio/{filename}", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


@router.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve stored audio files (original recordings + TTS generated)."""
    file_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    # Determine media type based on extension
    if filename.endswith(".mp3"):
        media_type = "audio/mpeg"
    elif filename.endswith(".webm"):
        media_type = "audio/webm"
    elif filename.endswith(".wav"):
        media_type = "audio/wav"
    else:
        media_type = "audio/mpeg"

    return FileResponse(file_path, media_type=media_type)
