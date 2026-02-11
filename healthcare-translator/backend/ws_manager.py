from fastapi import WebSocket
from typing import Dict, List
import json


class ConnectionManager:
    """
    Manages WebSocket connections per conversation room.
    Enables real-time WhatsApp-like messaging between Doctor and Patient.
    """

    def __init__(self):
        # { conversation_id: [websocket1, websocket2, ...] }
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        """Accept and register a WebSocket connection to a conversation room."""
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)
        print(f"[WS] Client connected to room: {conversation_id} | Total: {len(self.active_connections[conversation_id])}")

    def disconnect(self, websocket: WebSocket, conversation_id: str):
        """Remove a WebSocket connection from a conversation room."""
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].remove(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]
            print(f"[WS] Client disconnected from room: {conversation_id}")

    async def broadcast_to_room(self, conversation_id: str, message: dict):
        """Broadcast a message to ALL clients in a conversation room."""
        if conversation_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[conversation_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            # Clean up broken connections
            for conn in disconnected:
                self.active_connections[conversation_id].remove(conn)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send a message to a specific client."""
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    def get_room_count(self, conversation_id: str) -> int:
        """Get number of connected clients in a room."""
        return len(self.active_connections.get(conversation_id, []))


# Singleton instance
manager = ConnectionManager()
