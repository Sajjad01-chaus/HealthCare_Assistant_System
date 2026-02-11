import os
import json
from groq import Groq
from typing import Optional
from schemas import SUPPORTED_LANGUAGES
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Model Configuration ---
TRANSLATION_MODEL = "llama-3.3-70b-versatile"
SUMMARY_MODEL = "llama-3.3-70b-versatile"
WHISPER_MODEL = "whisper-large-v3"


# ============================================================
# 1. TRANSLATION SERVICE
# ============================================================
async def translate_message(
    text: str,
    source_language: str,
    target_language: str,
    role: str = "doctor"
) -> str:
    """
    Translate a message between doctor and patient with medical context awareness.
    """
    if source_language == target_language:
        return text

    source_name = SUPPORTED_LANGUAGES.get(source_language, source_language)
    target_name = SUPPORTED_LANGUAGES.get(target_language, target_language)

    # Role-aware system prompt for medical accuracy
    system_prompt = f"""You are a professional medical interpreter specializing in doctor-patient communication.

CRITICAL RULES:
1. Translate the following message from {source_name} to {target_name}.
2. Preserve ALL medical terminology accurately. Use proper medical terms in the target language.
3. If the speaker is a PATIENT: use simple, clear language that a layperson would understand.
4. If the speaker is a DOCTOR: maintain professional medical terminology.
5. Preserve the emotional tone and urgency of the original message.
6. NEVER add, remove, or modify any medical information.
7. If a medical term has no direct translation, keep it in the original language and add a brief explanation in parentheses.
8. Return ONLY the translated text. No explanations, no notes, no prefixes.

Speaker role: {role.upper()}"""

    try:
        response = client.chat.completions.create(
            model=TRANSLATION_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.2,  # Low temp for accuracy
            max_tokens=2048,
        )
        translated = response.choices[0].message.content.strip()

        # Clean up any unwanted prefixes the model might add
        unwanted_prefixes = ["Translation:", "Translated:", "Here's the translation:", "Here is the translation:"]
        for prefix in unwanted_prefixes:
            if translated.lower().startswith(prefix.lower()):
                translated = translated[len(prefix):].strip()

        return translated

    except Exception as e:
        print(f"Translation error: {e}")
        raise Exception(f"Translation failed: {str(e)}")


# ============================================================
# 2. LANGUAGE DETECTION SERVICE
# ============================================================
async def detect_language(text: str) -> str:
    """
    Auto-detect the language of the input text.
    Returns language code (e.g., 'en', 'hi', 'es').
    """
    try:
        response = client.chat.completions.create(
            model=TRANSLATION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """Detect the language of the given text. 
Return ONLY the ISO 639-1 two-letter language code (e.g., 'en', 'hi', 'es', 'fr', 'de', 'zh', 'ar', 'ja', 'ko', 'bn', 'ta', 'te', 'ur').
Return ONLY the code, nothing else."""
                },
                {"role": "user", "content": text}
            ],
            temperature=0,
            max_tokens=10,
        )
        detected = response.choices[0].message.content.strip().lower()
        # Validate it's a known language code
        if detected in SUPPORTED_LANGUAGES:
            return detected
        return "en"  # Default fallback
    except Exception as e:
        print(f"Language detection error: {e}")
        return "en"


# ============================================================
# 3. MEDICAL SUMMARY SERVICE
# ============================================================
async def generate_medical_summary(messages: list) -> str:
    """
    Generate a structured medical summary from conversation messages.
    Extracts: symptoms, diagnoses, medications, follow-up actions.
    """
    # Format conversation history
    conversation_text = ""
    for msg in messages:
        role_label = "Doctor" if msg.role.value == "doctor" else "Patient"
        conversation_text += f"{role_label}: {msg.original_text}\n"
        if msg.translated_text:
            conversation_text += f"  [Translated: {msg.translated_text}]\n"

    system_prompt = """You are a medical documentation assistant. Analyze the following doctor-patient conversation and generate a structured clinical summary.

Your summary MUST include the following sections (use exactly these headings):

## Patient Complaints & Symptoms
- List all symptoms mentioned by the patient

## Doctor's Observations & Diagnosis
- List any diagnoses, assessments, or clinical observations made by the doctor

## Medications & Treatments
- List any medications prescribed, dosages mentioned, or treatments recommended

## Follow-up Actions
- List any follow-up appointments, tests ordered, lifestyle recommendations, or referrals

## Key Medical Terms Used
- List important medical terms that appeared in the conversation with brief explanations

RULES:
- Only include information explicitly stated in the conversation.
- If a section has no relevant information, write "Not discussed in this conversation."
- Use clear, professional medical language.
- Flag any potential urgency or red flags with ⚠️ emoji.
- Keep the summary concise but comprehensive."""

    try:
        response = client.chat.completions.create(
            model=SUMMARY_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please summarize this doctor-patient conversation:\n\n{conversation_text}"}
            ],
            temperature=0.3,
            max_tokens=2048,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Summary generation error: {e}")
        raise Exception(f"Summary generation failed: {str(e)}")


# ============================================================
# 4. AUDIO TRANSCRIPTION SERVICE (Whisper)
# ============================================================
async def transcribe_audio(file_path: str, language: Optional[str] = None) -> dict:
    """
    Transcribe audio using Groq's Whisper large-v3.
    Returns transcribed text and detected language.
    """
    try:
        with open(file_path, "rb") as audio_file:
            params = {
                "model": WHISPER_MODEL,
                "file": audio_file,
                "response_format": "verbose_json",
            }
            if language:
                params["language"] = language

            transcription = client.audio.transcriptions.create(**params)

        return {
            "text": transcription.text,
            "language": getattr(transcription, 'language', language or 'auto'),
            "duration": getattr(transcription, 'duration', None),
        }

    except Exception as e:
        print(f"Transcription error: {e}")
        raise Exception(f"Audio transcription failed: {str(e)}")
