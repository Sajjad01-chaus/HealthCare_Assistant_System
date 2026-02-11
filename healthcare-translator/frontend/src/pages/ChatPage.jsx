import { useState, useEffect, useRef } from "react";
import MessageBubble from "../components/MessageBubble";
import AudioRecorder from "../components/AudioRecorder";
import SummaryPanel from "../components/SummaryPanel";
import SearchBar from "../components/SearchBar";
import {
  createConversation,
  listConversations,
  getMessages,
  connectWebSocket,
  sendWSMessage,
  uploadAudio,
} from "../services/api";

const LANGUAGES = [
  { code: "en", name: "English", flag: "🇬🇧" },
  { code: "hi", name: "Hindi", flag: "🇮🇳" },
  { code: "es", name: "Spanish", flag: "🇪🇸" },
  { code: "fr", name: "French", flag: "🇫🇷" },
  { code: "de", name: "German", flag: "🇩🇪" },
  { code: "zh", name: "Chinese", flag: "🇨🇳" },
  { code: "ar", name: "Arabic", flag: "🇸🇦" },
  { code: "pt", name: "Portuguese", flag: "🇧🇷" },
  { code: "ru", name: "Russian", flag: "🇷🇺" },
  { code: "ja", name: "Japanese", flag: "🇯🇵" },
  { code: "bn", name: "Bengali", flag: "🇧🇩" },
  { code: "ta", name: "Tamil", flag: "🇮🇳" },
  { code: "te", name: "Telugu", flag: "🇮🇳" },
  { code: "ur", name: "Urdu", flag: "🇵🇰" },
];

export default function ChatPage() {
  // State
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [role, setRole] = useState("doctor");
  const [doctorLang, setDoctorLang] = useState("en");
  const [patientLang, setPatientLang] = useState("hi");
  const [sending, setSending] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [participants, setParticipants] = useState(0);
  const [showSidebar, setShowSidebar] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(true);  // Auto-play TTS for incoming messages

  const wsRef = useRef(null);
  const chatEndRef = useRef(null);

  // Scroll to bottom on new message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Connect WebSocket when active conversation changes
  useEffect(() => {
    if (!activeConv) return;

    // Load existing messages
    loadMessages(activeConv.id);

    // Connect WebSocket
    if (wsRef.current) wsRef.current.close();
    wsRef.current = connectWebSocket(
      activeConv.id,
      (data) => {
        if (data.type === "message") {
          setMessages((prev) => [...prev, data.message]);
        } else if (data.type === "system") {
          setParticipants(data.participants || 0);
        }
      },
      (err) => console.error("WS Error:", err),
      () => console.log("WS Closed")
    );

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [activeConv?.id]);

  // API calls
  const loadConversations = async () => {
    try {
      const data = await listConversations();
      setConversations(data);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  };

  const loadMessages = async (convId) => {
    try {
      const data = await getMessages(convId);
      setMessages(data);
    } catch (err) {
      console.error("Failed to load messages:", err);
    }
  };

  const handleNewConversation = async () => {
    try {
      const conv = await createConversation({
        title: `Consultation - ${new Date().toLocaleDateString()}`,
        doctor_language: doctorLang,
        patient_language: patientLang,
      });
      setConversations((prev) => [conv, ...prev]);
      setActiveConv(conv);
      setMessages([]);
      setShowSidebar(false);
    } catch (err) {
      console.error("Failed to create conversation:", err);
    }
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputText.trim() || !activeConv || sending) return;

    const srcLang = role === "doctor" ? doctorLang : patientLang;
    const tgtLang = role === "doctor" ? patientLang : doctorLang;

    setSending(true);
    sendWSMessage(wsRef.current, {
      type: "text",
      role: role,
      content: inputText,
      source_language: srcLang,
      target_language: tgtLang,
    });

    setInputText("");
    // Reset sending after a brief delay (WS will broadcast the message)
    setTimeout(() => setSending(false), 500);
  };

  const handleAudioRecording = async (audioBlob) => {
    if (!activeConv) return;
    setSending(true);
    try {
      const srcLang = role === "doctor" ? doctorLang : patientLang;
      const result = await uploadAudio(activeConv.id, audioBlob, role, srcLang);
      setMessages((prev) => [...prev, result]);
    } catch (err) {
      console.error("Audio upload failed:", err);
    } finally {
      setSending(false);
    }
  };

  const myLang = role === "doctor" ? doctorLang : patientLang;
  const theirLang = role === "doctor" ? patientLang : doctorLang;

  // Share link for conversation
  const shareLink = activeConv
    ? `${window.location.origin}?conv=${activeConv.id}`
    : null;

  return (
    <div className="h-screen flex flex-col bg-slate-50 overflow-hidden">
      {/* ========== TOP HEADER ========== */}
      <header className="bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="md:hidden w-9 h-9 rounded-lg bg-slate-100 flex items-center justify-center"
          >
            ☰
          </button>
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 bg-gradient-to-br from-blue-600 to-cyan-500 rounded-xl flex items-center justify-center text-white text-lg shadow-lg shadow-blue-500/20">
              🏥
            </div>
            <div>
              <h1 className="text-base font-bold text-slate-800 leading-tight">MediTranslate</h1>
              <p className="text-xs text-slate-400">Doctor-Patient Translation</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Role Toggle */}
          <div className="flex bg-slate-100 rounded-xl p-0.5">
            <button
              onClick={() => setRole("doctor")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                role === "doctor"
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              🩺 Doctor
            </button>
            <button
              onClick={() => setRole("patient")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                role === "patient"
                  ? "bg-emerald-600 text-white shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              🧑 Patient
            </button>
          </div>

          {/* Participants indicator */}
          {activeConv && participants > 0 && (
            <span className="text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded-full">
              👥 {participants}
            </span>
          )}
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* ========== SIDEBAR ========== */}
        <aside
          className={`${
            showSidebar ? "translate-x-0" : "-translate-x-full"
          } md:translate-x-0 fixed md:relative z-40 w-72 bg-white border-r border-slate-200 h-full flex flex-col transition-transform`}
        >
          {/* Language Settings */}
          <div className="p-4 border-b border-slate-100">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Languages</h3>
            <div className="space-y-2">
              <div>
                <label className="text-xs text-slate-500 mb-1 block">🩺 Doctor speaks</label>
                <select
                  value={doctorLang}
                  onChange={(e) => setDoctorLang(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {LANGUAGES.map((l) => (
                    <option key={l.code} value={l.code}>
                      {l.flag} {l.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-500 mb-1 block">🧑 Patient speaks</label>
                <select
                  value={patientLang}
                  onChange={(e) => setPatientLang(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  {LANGUAGES.map((l) => (
                    <option key={l.code} value={l.code}>
                      {l.flag} {l.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* New conversation button */}
          <div className="p-4">
            <button
              onClick={handleNewConversation}
              className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-cyan-500 text-white rounded-xl text-sm font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all"
            >
              + New Consultation
            </button>
          </div>

          {/* Conversation list */}
          <div className="flex-1 overflow-y-auto px-3">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 px-1">
              History
            </h3>
            {conversations.length === 0 && (
              <p className="text-xs text-slate-400 text-center py-4">No conversations yet</p>
            )}
            {conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => {
                  setActiveConv(conv);
                  setDoctorLang(conv.doctor_language);
                  setPatientLang(conv.patient_language);
                  setShowSidebar(false);
                }}
                className={`w-full text-left p-3 rounded-xl mb-1.5 transition-all ${
                  activeConv?.id === conv.id
                    ? "bg-blue-50 border border-blue-200"
                    : "hover:bg-slate-50 border border-transparent"
                }`}
              >
                <p className="text-sm font-medium text-slate-700 truncate">{conv.title}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-slate-400">
                    {new Date(conv.created_at).toLocaleDateString()}
                  </span>
                  <span className="text-xs text-slate-300">•</span>
                  <span className="text-xs text-slate-400">{conv.message_count || 0} msgs</span>
                </div>
              </button>
            ))}
          </div>
        </aside>

        {/* ========== MAIN CHAT AREA ========== */}
        <main className="flex-1 flex flex-col min-w-0">
          {!activeConv ? (
            /* Empty state */
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center max-w-md px-4">
                <div className="text-6xl mb-4">🏥</div>
                <h2 className="text-2xl font-bold text-slate-800 mb-2">MediTranslate</h2>
                <p className="text-slate-500 mb-6">
                  Real-time AI-powered translation bridge between doctors and patients.
                  Break language barriers in healthcare.
                </p>
                <button
                  onClick={handleNewConversation}
                  className="px-8 py-3 bg-gradient-to-r from-blue-600 to-cyan-500 text-white rounded-xl font-semibold hover:shadow-xl hover:shadow-blue-500/25 transition-all"
                >
                  Start New Consultation
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* Chat toolbar */}
              <div className="bg-white border-b border-slate-200 px-4 py-2 flex items-center justify-between shrink-0">
                <div className="flex items-center gap-2 min-w-0">
                  <h2 className="text-sm font-semibold text-slate-700 truncate">
                    {activeConv.title}
                  </h2>
                  <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full shrink-0">
                    {LANGUAGES.find((l) => l.code === doctorLang)?.flag}{" "}
                    ↔{" "}
                    {LANGUAGES.find((l) => l.code === patientLang)?.flag}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => setAutoSpeak(!autoSpeak)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                      autoSpeak
                        ? "bg-violet-100 text-violet-700 hover:bg-violet-200"
                        : "bg-slate-100 text-slate-400 hover:bg-slate-200"
                    }`}
                    title={autoSpeak ? "Auto-speak ON — translations will be read aloud" : "Auto-speak OFF"}
                  >
                    {autoSpeak ? "🔊 Auto-Speak ON" : "🔇 Auto-Speak OFF"}
                  </button>
                  <button
                    onClick={() => setShowSearch(true)}
                    className="px-3 py-1.5 bg-slate-100 text-slate-600 rounded-lg text-xs font-medium hover:bg-slate-200 transition-colors"
                    title="Search conversations"
                  >
                    🔍 Search
                  </button>
                  <button
                    onClick={() => setShowSummary(true)}
                    className="px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg text-xs font-medium hover:bg-blue-200 transition-colors"
                    title="Generate AI summary"
                  >
                    📋 Summary
                  </button>
                  {shareLink && (
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(shareLink);
                        alert("Room link copied! Share with patient to join.");
                      }}
                      className="px-3 py-1.5 bg-emerald-100 text-emerald-700 rounded-lg text-xs font-medium hover:bg-emerald-200 transition-colors"
                      title="Copy shareable room link"
                    >
                      🔗 Share
                    </button>
                  )}
                </div>
              </div>

              {/* Messages area */}
              <div className="flex-1 overflow-y-auto px-4 py-4">
                {messages.length === 0 && (
                  <div className="text-center py-16">
                    <div className="text-4xl mb-3">💬</div>
                    <p className="text-slate-400 text-sm">
                      Start the conversation. Messages will be translated in real-time.
                    </p>
                    <p className="text-slate-300 text-xs mt-1">
                      You are speaking as <strong>{role === "doctor" ? "Doctor" : "Patient"}</strong> in{" "}
                      <strong>{LANGUAGES.find((l) => l.code === myLang)?.name}</strong>
                    </p>
                  </div>
                )}
                {messages.map((msg) => (
                  <MessageBubble key={msg.id} message={msg} viewerRole={role} autoSpeak={autoSpeak} />
                ))}
                <div ref={chatEndRef} />
              </div>

              {/* Input area */}
              <div className="bg-white border-t border-slate-200 px-4 py-3 shrink-0">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    role === "doctor"
                      ? "bg-blue-100 text-blue-700"
                      : "bg-emerald-100 text-emerald-700"
                  }`}>
                    Speaking as {role === "doctor" ? "🩺 Doctor" : "🧑 Patient"}
                  </span>
                  <span className="text-xs text-slate-400">
                    {LANGUAGES.find((l) => l.code === myLang)?.flag}{" "}
                    {LANGUAGES.find((l) => l.code === myLang)?.name} →{" "}
                    {LANGUAGES.find((l) => l.code === theirLang)?.flag}{" "}
                    {LANGUAGES.find((l) => l.code === theirLang)?.name}
                  </span>
                </div>
                <form onSubmit={handleSendMessage} className="flex items-center gap-2">
                  <AudioRecorder onRecordingComplete={handleAudioRecording} disabled={sending} />
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder={`Type a message in ${LANGUAGES.find((l) => l.code === myLang)?.name}...`}
                    disabled={sending}
                    className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
                  />
                  <button
                    type="submit"
                    disabled={!inputText.trim() || sending}
                    className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-cyan-500 text-white rounded-xl text-sm font-semibold hover:shadow-lg hover:shadow-blue-500/25 disabled:opacity-50 disabled:shadow-none transition-all"
                  >
                    {sending ? (
                      <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin inline-block"></span>
                    ) : (
                      "Send"
                    )}
                  </button>
                </form>
              </div>
            </>
          )}
        </main>
      </div>

      {/* Modals */}
      {showSummary && activeConv && (
        <SummaryPanel conversationId={activeConv.id} onClose={() => setShowSummary(false)} />
      )}
      {showSearch && (
        <SearchBar conversationId={activeConv?.id} onClose={() => setShowSearch(false)} />
      )}
    </div>
  );
}
