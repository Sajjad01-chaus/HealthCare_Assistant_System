from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from database import get_db
from models import Conversation, Message
from schemas import ConversationCreate, ConversationResponse

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationResponse)
def create_conversation(data: ConversationCreate, db: Session = Depends(get_db)):
    conversation = Conversation(
        title=data.title,
        doctor_language=data.doctor_language,
        patient_language=data.patient_language,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        doctor_language=conversation.doctor_language,
        patient_language=conversation.patient_language,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=0,
    )


@router.get("/", response_model=List[ConversationResponse])
def list_conversations(db: Session = Depends(get_db)):
    conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    result = []
    for conv in conversations:
        msg_count = db.query(func.count(Message.id)).filter(Message.conversation_id == conv.id).scalar()
        result.append(ConversationResponse(
            id=conv.id,
            title=conv.title,
            doctor_language=conv.doctor_language,
            patient_language=conv.patient_language,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=msg_count,
        ))
    return result


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msg_count = db.query(func.count(Message.id)).filter(Message.conversation_id == conv.id).scalar()
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        doctor_language=conv.doctor_language,
        patient_language=conv.patient_language,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=msg_count,
    )


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted"}
