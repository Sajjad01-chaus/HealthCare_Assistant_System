from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Conversation, Message, MessageTypeEnum
from schemas import MessageCreate, MessageResponse
from services.groq_service import translate_message

router = APIRouter(prefix="/api/conversations/{conversation_id}/messages", tags=["messages"])


@router.get("/", response_model=List[MessageResponse])
def get_messages(conversation_id: str, db: Session = Depends(get_db)):
    """Get all messages for a conversation (with translations)."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

    return [MessageResponse.model_validate(msg) for msg in messages]


@router.post("/", response_model=MessageResponse)
async def send_message(conversation_id: str, data: MessageCreate, db: Session = Depends(get_db)):
    """Send a message and get automatic translation."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Determine target language based on role
    if data.role.value == "doctor":
        target_language = conv.patient_language
    else:
        target_language = conv.doctor_language

    # Translate the message
    translated_text = None
    try:
        translated_text = await translate_message(
            text=data.original_text,
            source_language=data.original_language,
            target_language=target_language,
            role=data.role.value,
        )
    except Exception as e:
        print(f"Translation failed: {e}")
        translated_text = f"[Translation unavailable: {str(e)}]"

    # Save message to database
    message = Message(
        conversation_id=conversation_id,
        role=data.role,
        message_type=data.message_type,
        original_text=data.original_text,
        original_language=data.original_language,
        translated_text=translated_text,
        target_language=target_language,
        audio_file_path=data.audio_file_path,
        audio_duration=data.audio_duration,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return MessageResponse.model_validate(message)
