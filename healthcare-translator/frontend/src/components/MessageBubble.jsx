import { useEffect } from "react";
import { getAudioUrl } from "../services/api";

const LANG_NAMES = {
  en: "English", hi: "Hindi", es: "Spanish", fr: "French", de: "German",
  zh: "Chinese", ar: "Arabic", pt: "Portuguese", ru: "Russian", ja: "Japanese",
  ko: "Korean", bn: "Bengali", ta: "Tamil", te: "Telugu", ur: "Urdu",
  mr: "Marathi", gu: "Gujarati", kn: "Kannada", ml: "Malayalam", pa: "Punjabi",
};

export default function MessageBubble({ message, viewerRole, autoSpeak = false }) {
  const isOwn = message.role === viewerRole;
  const isDoctor = message.role === "doctor";
  const isAudio = message.message_type === "audio";

  const time = new Date(message.created_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  // AUTO-PLAY: When a new message arrives from the OTHER person, speak the translation aloud
  useEffect(() => {
    if (autoSpeak && !isOwn && message.tts_audio_path) {
      const audio = new Audio(getAudioUrl(message.tts_audio_path));
      audio.volume = 0.8;
      audio.play().catch((e) => console.log("Autoplay blocked — click to enable:", e));
    }
  }, [message.id]);

  // Manual TTS play — server TTS (high quality) with browser fallback
  const handlePlayTranslation = () => {
    if (message.tts_audio_path) {
      const audio = new Audio(getAudioUrl(message.tts_audio_path));
      audio.play();
    } else if (message.translated_text && "speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(message.translated_text);
      utterance.lang = message.target_language || "en";
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };

  const handlePlayOriginal = () => {
    if (message.original_text && "speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(message.original_text);
      utterance.lang = message.original_language || "en";
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <div className={`flex ${isOwn ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`max-w-[80%] md:max-w-[65%]`}>
        {/* Role badge */}
        <div className={`flex items-center gap-1.5 mb-1 ${isOwn ? "justify-end" : "justify-start"}`}>
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
            isDoctor ? "bg-blue-100 text-blue-700" : "bg-emerald-100 text-emerald-700"
          }`}>
            {isDoctor ? "🩺 Doctor" : "🧑 Patient"}
          </span>
          <span className="text-xs text-slate-400">{time}</span>
        </div>

        {/* ---- ORIGINAL MESSAGE BUBBLE ---- */}
        <div className={`rounded-2xl px-4 py-3 shadow-sm ${
          isOwn
            ? isDoctor ? "bg-blue-600 text-white rounded-br-md" : "bg-emerald-600 text-white rounded-br-md"
            : "bg-white text-slate-800 border border-slate-200 rounded-bl-md"
        }`}>
          {/* Audio player for voice messages */}
          {isAudio && message.audio_file_path && (
            <div className="mb-2">
              <audio
                controls
                src={getAudioUrl(message.audio_file_path)}
                className="w-full h-8 rounded"
                style={{ filter: isOwn ? "invert(1) brightness(2)" : "none" }}
              />
              <span className={`text-xs ${isOwn ? "text-white/60" : "text-slate-400"}`}>
                🎤 Voice message {message.audio_duration ? `(${message.audio_duration}s)` : ""}
              </span>
            </div>
          )}

          {/* Original text + play original button */}
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm leading-relaxed flex-1">{message.original_text}</p>
            <button
              onClick={handlePlayOriginal}
              className={`shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs transition-colors ${
                isOwn ? "bg-white/20 hover:bg-white/30 text-white" : "bg-slate-100 hover:bg-slate-200 text-slate-500"
              }`}
              title="Listen to original"
            >
              🔊
            </button>
          </div>
          <span className={`text-xs ${isOwn ? "text-white/50" : "text-slate-400"}`}>
            {LANG_NAMES[message.original_language] || message.original_language}
          </span>
        </div>

        {/* ---- TRANSLATED TEXT + TTS PLAY BUTTON ---- */}
        {message.translated_text && (
          <div className={`mt-1.5 rounded-2xl px-4 py-2.5 border-2 border-dashed ${
            isOwn
              ? "border-slate-300 bg-slate-50 text-slate-700 rounded-br-md"
              : isDoctor
                ? "border-blue-200 bg-blue-50 text-blue-800 rounded-bl-md"
                : "border-emerald-200 bg-emerald-50 text-emerald-800 rounded-bl-md"
          }`}>
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm leading-relaxed italic flex-1">{message.translated_text}</p>
              <button
                onClick={handlePlayTranslation}
                className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center text-white text-sm shadow-sm hover:shadow-md transition-all"
                title="Listen to translation"
              >
                🔊
              </button>
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs text-slate-400">
                🌐 {LANG_NAMES[message.target_language] || message.target_language}
              </span>
              {message.tts_audio_path && (
                <span className="text-xs text-blue-400">• AI Voice</span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
