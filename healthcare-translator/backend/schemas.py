from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


# --- Enums ---
class RoleEnum(str, Enum):
    doctor = "doctor"
    patient = "patient"


class MessageTypeEnum(str, Enum):
    text = "text"
    audio = "audio"


# --- Conversation Schemas ---
class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    doctor_language: str = "en"
    patient_language: str = "hi"


class ConversationResponse(BaseModel):
    id: str
    title: str
    doctor_language: str
    patient_language: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True


# --- Message Schemas ---
class MessageCreate(BaseModel):
    role: RoleEnum
    original_text: str
    original_language: str
    message_type: MessageTypeEnum = MessageTypeEnum.text
    audio_file_path: Optional[str] = None
    audio_duration: Optional[str] = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: RoleEnum
    message_type: MessageTypeEnum
    original_text: str
    original_language: str
    translated_text: Optional[str] = None
    target_language: Optional[str] = None
    audio_file_path: Optional[str] = None
    audio_duration: Optional[str] = None
    tts_audio_path: Optional[str] = None  # TTS audio of translated text
    created_at: datetime

    class Config:
        from_attributes = True


# --- WebSocket Message Schema ---
class WSMessage(BaseModel):
    type: str  # "text" | "audio_transcription"
    role: RoleEnum
    content: str
    source_language: str
    target_language: str


class WSResponse(BaseModel):
    type: str  # "message" | "error" | "system"
    message: Optional[MessageResponse] = None
    error: Optional[str] = None
    system_text: Optional[str] = None


# --- Translation Schemas ---
class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str
    role: RoleEnum = RoleEnum.doctor


class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str


# --- Summary Schemas ---
class SummaryResponse(BaseModel):
    id: str
    conversation_id: str
    summary_text: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Search Schemas ---
class SearchResult(BaseModel):
    message_id: str
    conversation_id: str
    conversation_title: str
    role: RoleEnum
    original_text: str
    translated_text: Optional[str]
    created_at: datetime
    match_context: str  # Highlighted snippet

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResult]


# --- Supported Languages ---
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ar": "Arabic",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
}
