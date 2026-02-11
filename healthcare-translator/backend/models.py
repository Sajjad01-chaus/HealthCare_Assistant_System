import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class RoleEnum(str, enum.Enum):
    doctor = "doctor"
    patient = "patient"


class MessageTypeEnum(str, enum.Enum):
    text = "text"
    audio = "audio"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, default="New Conversation")
    doctor_language = Column(String, default="en")
    patient_language = Column(String, default="hi")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(SAEnum(RoleEnum), nullable=False)
    message_type = Column(SAEnum(MessageTypeEnum), default=MessageTypeEnum.text)

    # Original content
    original_text = Column(Text, nullable=False)
    original_language = Column(String, nullable=False)

    # Translated content
    translated_text = Column(Text, nullable=True)
    target_language = Column(String, nullable=True)

    # Audio fields
    audio_file_path = Column(String, nullable=True)
    audio_duration = Column(String, nullable=True)
    tts_audio_path = Column(String, nullable=True)  # TTS-generated audio of translated text

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="messages")


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    summary_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
