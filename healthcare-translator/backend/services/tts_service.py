import os
import uuid
import edge_tts
import asyncio
from gtts import gTTS

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio_files")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Language code → Edge TTS voice mapping (high quality neural voices)
VOICE_MAP = {
    "en": "en-US-JennyNeural",
    "hi": "hi-IN-SwaraNeural",
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "ar": "ar-SA-ZariyahNeural",
    "pt": "pt-BR-FranciscaNeural",
    "ru": "ru-RU-SvetlanaNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "bn": "bn-IN-TanishaaNeural",
    "ta": "ta-IN-PallaviNeural",
    "te": "te-IN-ShrutiNeural",
    "ur": "ur-PK-UzmaNeural",
    "mr": "mr-IN-AarohiNeural",
    "gu": "gu-IN-DhwaniNeural",
    "kn": "kn-IN-SapnaNeural",
    "ml": "ml-IN-SobhanaNeural",
    "pa": "pa-IN-GurpreetNeural",
}

# Doctor vs Patient voice variants (use different voice style for distinction)
DOCTOR_VOICE_OVERRIDE = {
    "en": "en-US-GuyNeural",
    "hi": "hi-IN-MadhurNeural",
    "es": "es-ES-AlvaroNeural",
    "fr": "fr-FR-HenriNeural",
    "de": "de-DE-ConradNeural",
    "zh": "zh-CN-YunxiNeural",
    "ar": "ar-SA-HamedNeural",
    "pt": "pt-BR-AntonioNeural",
    "ru": "ru-RU-DmitryNeural",
    "ja": "ja-JP-KeitaNeural",
    "ko": "ko-KR-InJoonNeural",
}


async def text_to_speech(
    text: str,
    language: str,
    role: str = "patient",
) -> str:
    # Select voice for edge-tts
    if role == "doctor" and language in DOCTOR_VOICE_OVERRIDE:
        voice = DOCTOR_VOICE_OVERRIDE[language]
    else:
        voice = VOICE_MAP.get(language, "en-US-JennyNeural")

    filename = f"tts_{uuid.uuid4()}.mp3"
    file_path = os.path.join(AUDIO_DIR, filename)

    try:
        # ATTEMPT 1: High-quality Edge TTS
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(file_path)
        return filename
    except Exception as e:
        print(f"Edge TTS error (likely 403): {e}. Trying gTTS fallback...")
        
        try:
            # ATTEMPT 2: Reliable Google TTS Fallback
            # gTTS expects simple codes like 'hi' or 'en'
            tts = gTTS(text=text, lang=language)
            tts.save(file_path)
            print(f"Successfully generated audio via gTTS: {filename}")
            return filename
        except Exception as e2:
            print(f"Critical TTS failure: {e2}")
            # Final fallback to English if the target language fails in gTTS too
            try:
                tts = gTTS(text=text, lang='en')
                tts.save(file_path)
                return filename
            except:
                raise Exception(f"Text-to-speech completely failed: {str(e2)}")