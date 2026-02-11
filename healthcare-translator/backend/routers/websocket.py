from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Conversation, Message, MessageTypeEnum, RoleEnum
from services.groq_service import translate_message
from services.tts_service import text_to_speech
from ws_manager import manager
import json
from datetime import datetime, timezone

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """
    WebSocket endpoint for real-time doctor-patient communication.

    Client sends JSON:
    {
        "type": "text",
        "role": "doctor" | "patient",
        "content": "message text",
        "source_language": "en",
        "target_language": "hi"
    }

    Server broadcasts to room:
    {
        "type": "message",
        "message": { ...full message object with tts_audio_path... }
    }
    """
    # Get DB session
    db = SessionLocal()

    try:
        # Verify conversation exists
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv:
            await websocket.close(code=4004, reason="Conversation not found")
            return

        # Connect to room
        await manager.connect(websocket, conversation_id)

        # Notify room about new connection
        room_count = manager.get_room_count(conversation_id)
        await manager.broadcast_to_room(conversation_id, {
            "type": "system",
            "system_text": f"A participant joined. {room_count} participant(s) in room.",
            "participants": room_count,
        })

        # Listen for messages
        while True:
            data = await websocket.receive_json()

            msg_type = data.get("type", "text")
            role_str = data.get("role", "doctor")
            content = data.get("content", "")
            source_language = data.get("source_language", "en")
            target_language = data.get("target_language", "hi")

            if not content.strip():
                await manager.send_personal(websocket, {
                    "type": "error",
                    "error": "Empty message"
                })
                continue

            # Translate the message
            role_enum = RoleEnum.doctor if role_str == "doctor" else RoleEnum.patient
            translated_text = ""
            try:
                translated_text = await translate_message(
                    text=content,
                    source_language=source_language,
                    target_language=target_language,
                    role=role_str,
                )
            except Exception as e:
                translated_text = f"[Translation error: {str(e)}]"

            # Generate TTS for the translated text
            tts_file = None
            try:
                if translated_text and not translated_text.startswith("[Translation"):
                    listener_role = "patient" if role_str == "doctor" else "doctor"
                    tts_file = await text_to_speech(
                        text=translated_text,
                        language=target_language,
                        role=listener_role,
                    )
            except Exception as e:
                print(f"TTS generation failed (non-critical): {e}")

            # Save to database
            message = Message(
                conversation_id=conversation_id,
                role=role_enum,
                message_type=MessageTypeEnum.text,
                original_text=content,
                original_language=source_language,
                translated_text=translated_text,
                target_language=target_language,
                tts_audio_path=tts_file,
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            # Broadcast translated message + TTS audio to all in room
            await manager.broadcast_to_room(conversation_id, {
                "type": "message",
                "message": {
                    "id": message.id,
                    "conversation_id": message.conversation_id,
                    "role": message.role.value,
                    "message_type": message.message_type.value,
                    "original_text": message.original_text,
                    "original_language": message.original_language,
                    "translated_text": message.translated_text,
                    "target_language": message.target_language,
                    "audio_file_path": message.audio_file_path,
                    "audio_duration": message.audio_duration,
                    "tts_audio_path": message.tts_audio_path,
                    "created_at": message.created_at.isoformat(),
                }
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
        room_count = manager.get_room_count(conversation_id)
        await manager.broadcast_to_room(conversation_id, {
            "type": "system",
            "system_text": f"A participant left. {room_count} participant(s) in room.",
            "participants": room_count,
        })
    except Exception as e:
        print(f"[WS] Error: {e}")
        manager.disconnect(websocket, conversation_id)
    finally:
        db.close()
