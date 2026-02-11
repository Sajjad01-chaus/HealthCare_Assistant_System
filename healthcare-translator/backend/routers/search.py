from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import Message, Conversation
from schemas import SearchResponse, SearchResult

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/", response_model=SearchResponse)
def search_messages(
    q: str = Query(..., min_length=1, description="Search query"),
    conversation_id: str = Query(None, description="Optional: limit search to a specific conversation"),
    db: Session = Depends(get_db),
):
    """Search keyword/phrases across all logged conversations."""
    query = db.query(Message, Conversation).join(
        Conversation, Message.conversation_id == Conversation.id
    )

    if conversation_id:
        query = query.filter(Message.conversation_id == conversation_id)

    # Search in both original and translated text
    search_filter = or_(
        Message.original_text.ilike(f"%{q}%"),
        Message.translated_text.ilike(f"%{q}%"),
    )
    query = query.filter(search_filter)
    results = query.order_by(Message.created_at.desc()).limit(50).all()

    search_results = []
    for msg, conv in results:
        # Create highlighted context snippet
        match_context = _highlight_match(msg.original_text, q)
        if not match_context and msg.translated_text:
            match_context = _highlight_match(msg.translated_text, q)

        search_results.append(SearchResult(
            message_id=msg.id,
            conversation_id=msg.conversation_id,
            conversation_title=conv.title,
            role=msg.role,
            original_text=msg.original_text,
            translated_text=msg.translated_text,
            created_at=msg.created_at,
            match_context=match_context,
        ))

    return SearchResponse(
        query=q,
        total_results=len(search_results),
        results=search_results,
    )


def _highlight_match(text: str, query: str, context_chars: int = 80) -> str:
    """Create a context snippet with the match highlighted using ** markers."""
    lower_text = text.lower()
    lower_query = query.lower()
    idx = lower_text.find(lower_query)

    if idx == -1:
        return text[:context_chars * 2]

    start = max(0, idx - context_chars)
    end = min(len(text), idx + len(query) + context_chars)

    snippet = ""
    if start > 0:
        snippet += "..."
    snippet += text[start:idx]
    snippet += f"**{text[idx:idx + len(query)]}**"
    snippet += text[idx + len(query):end]
    if end < len(text):
        snippet += "..."

    return snippet
