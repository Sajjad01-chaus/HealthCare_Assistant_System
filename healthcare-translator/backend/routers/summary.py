from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Conversation, Message, ConversationSummary
from schemas import SummaryResponse
from services.groq_service import generate_medical_summary

router = APIRouter(prefix="/api/conversations/{conversation_id}/summary", tags=["summary"])


@router.post("/", response_model=SummaryResponse)
async def create_summary(conversation_id: str, db: Session = Depends(get_db)):
    """Generate an AI-powered medical summary of the conversation."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

    if not messages:
        raise HTTPException(status_code=400, detail="No messages to summarize")

    # Generate summary using Groq
    try:
        summary_text = await generate_medical_summary(messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

    # Save summary
    summary = ConversationSummary(
        conversation_id=conversation_id,
        summary_text=summary_text,
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)

    return SummaryResponse.model_validate(summary)


@router.get("/", response_model=List[SummaryResponse])
def get_summaries(conversation_id: str, db: Session = Depends(get_db)):
    """Get all summaries for a conversation."""
    summaries = db.query(ConversationSummary).filter(
        ConversationSummary.conversation_id == conversation_id
    ).order_by(ConversationSummary.created_at.desc()).all()
    return [SummaryResponse.model_validate(s) for s in summaries]
