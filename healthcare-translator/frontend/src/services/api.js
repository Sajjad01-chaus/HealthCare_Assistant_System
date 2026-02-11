const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const WS_BASE = API_BASE.replace("http", "ws");

// ============================================================
// CONVERSATIONS
// ============================================================
export async function createConversation(data) {
  const res = await fetch(`${API_BASE}/api/conversations/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function listConversations() {
  const res = await fetch(`${API_BASE}/api/conversations/`);
  return res.json();
}

export async function getConversation(id) {
  const res = await fetch(`${API_BASE}/api/conversations/${id}`);
  return res.json();
}

export async function deleteConversation(id) {
  const res = await fetch(`${API_BASE}/api/conversations/${id}`, { method: "DELETE" });
  return res.json();
}

// ============================================================
// MESSAGES (REST fallback - primary is WebSocket)
// ============================================================
export async function getMessages(conversationId) {
  const res = await fetch(`${API_BASE}/api/conversations/${conversationId}/messages/`);
  return res.json();
}

export async function sendMessage(conversationId, data) {
  const res = await fetch(`${API_BASE}/api/conversations/${conversationId}/messages/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

// ============================================================
// AUDIO
// ============================================================
export async function uploadAudio(conversationId, audioBlob, role, sourceLanguage) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");
  formData.append("role", role);
  formData.append("source_language", sourceLanguage);

  const res = await fetch(`${API_BASE}/api/conversations/${conversationId}/audio`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

export function getAudioUrl(filename) {
  return `${API_BASE}/api/audio/${filename}`;
}

// ============================================================
// SUMMARY
// ============================================================
export async function generateSummary(conversationId) {
  const res = await fetch(`${API_BASE}/api/conversations/${conversationId}/summary/`, {
    method: "POST",
  });
  return res.json();
}

export async function getSummaries(conversationId) {
  const res = await fetch(`${API_BASE}/api/conversations/${conversationId}/summary/`);
  return res.json();
}

// ============================================================
// SEARCH
// ============================================================
export async function searchMessages(query, conversationId = null) {
  let url = `${API_BASE}/api/search/?q=${encodeURIComponent(query)}`;
  if (conversationId) url += `&conversation_id=${conversationId}`;
  const res = await fetch(url);
  return res.json();
}

// ============================================================
// TEXT-TO-SPEECH
// ============================================================
export async function generateTTS(text, language, role = "patient") {
  const formData = new FormData();
  formData.append("text", text);
  formData.append("language", language);
  formData.append("role", role);

  const res = await fetch(`${API_BASE}/api/tts`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

// ============================================================
// LANGUAGES
// ============================================================
export async function getLanguages() {
  const res = await fetch(`${API_BASE}/api/languages`);
  return res.json();
}

// ============================================================
// WEBSOCKET
// ============================================================
export function connectWebSocket(conversationId, onMessage, onError, onClose) {
  const ws = new WebSocket(`${WS_BASE}/ws/${conversationId}`);

  ws.onopen = () => {
    console.log(`[WS] Connected to room: ${conversationId}`);
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.error("[WS] Parse error:", e);
    }
  };

  ws.onerror = (error) => {
    console.error("[WS] Error:", error);
    if (onError) onError(error);
  };

  ws.onclose = (event) => {
    console.log("[WS] Disconnected:", event.code, event.reason);
    if (onClose) onClose(event);
  };

  return ws;
}

export function sendWSMessage(ws, message) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message));
  }
}
