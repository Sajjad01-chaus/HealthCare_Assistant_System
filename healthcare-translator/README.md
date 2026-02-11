# 🏥 MediTranslate — Healthcare Doctor-Patient Translation App

> Real-time AI-powered translation bridge between doctors and patients, featuring voice input/output, medical-context-aware translation, and intelligent clinical summarization.

**🔗 Live Demo:** https://health-care-assistant-system.vercel.app  
**📂 Repository:** https://github.com/Sajjad01-chaus/HealthCare_Assistant_System/

---

## 📌 Project Overview

MediTranslate is a full-stack web application that enables real-time communication between doctors and patients who speak different languages. It features a complete **multimodal voice pipeline** — doctors and patients can speak in their language and the other person **hears** the translation spoken aloud. The app also supports text chat, conversation persistence, keyword search, and intelligent medical summarization.

Built for the Pre-Interview Take-Home Assignment — designed and developed within a **12-hour** time constraint.

---

## ✅ Features Attempted & Completed

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 1 | **Real-Time Translation** | ✅ Complete | WebSocket-based instant translation between Doctor ↔ Patient |
| 2 | **Text Chat Interface** | ✅ Complete | WhatsApp-style UI with role-based message bubbles |
| 3 | **Voice Input + Audio Output** | ✅ Complete | Record → Transcribe → Translate → **Speak translated audio to listener** |
| 4 | **Conversation Logging** | ✅ Complete | All messages persisted in PostgreSQL with timestamps |
| 5 | **Conversation Search** | ✅ Complete | Keyword search across messages with highlighted context |
| 6 | **AI Medical Summary** | ✅ Complete | Structured extraction of symptoms, diagnoses, medications, follow-ups |

### Bonus Features
- 🔊 **Text-to-Speech Output** — Translations are spoken aloud via Edge-TTS / gTTS neural voices
- 🔊 **Auto-Speak Toggle** — Incoming translations auto-play as audio for hands-free operation
- 🔗 **Shareable Room Links** — Doctor shares a URL for the patient to join the same room
- 🌐 **20 Languages Supported** — English, Hindi, Bengali, Tamil, Telugu, Urdu, Chinese, Korean, Japanese, Arabic, Spanish, French, German, Portuguese, Russian, Italian, Dutch, Thai, Vietnamese, Turkish
- 🎯 **Role Toggle** — Switch between Doctor/Patient view on the same device
- 📱 **Mobile-Responsive UI** — Works on phones and tablets
- 🗣️ **Auto Language Detection** — Whisper auto-detects the spoken language
- 🩺 **Role-Aware Translation** — Doctor messages preserve medical terminology; Patient messages use simple language

---

## 🔊 Voice Pipeline — The Key Differentiator

MediTranslate lets participants **hear** the translation — critical in a clinical setting where a patient may not be able to read a screen.

```
Doctor speaks Korean 🎤
    │
    ▼
Browser records audio (WebM)
    │
    ▼
Groq Whisper large-v3 → Transcribes: "환자가 두통이 있습니다"
    │
    ▼
Groq Llama 3.3 70B → Translates to Chinese: "患者头痛"
    │                   (medical-context-aware, role-adapted)
    ▼
Edge-TTS / gTTS → Generates Chinese audio
    │
    ▼
WebSocket broadcasts to room:
    → Patient SEES: Korean original + Chinese translation
    → Patient HEARS: Chinese audio auto-plays 🔊
```

### Three-Layer Audio Fallback
1. **Primary:** Server-side Edge-TTS (high-quality Microsoft neural voices)
2. **Fallback:** Google TTS (gTTS) if Edge-TTS fails
3. **Manual:** Click 🔊 button on any message to hear it

### Doctor vs Patient Voices
Each language has distinct voices so participants can distinguish who is speaking:

| Language | Patient Voice | Doctor Voice |
|----------|--------------|--------------|
| English | Jenny (female) | Guy (male) |
| Hindi | Swara (female) | Madhur (male) |
| Chinese | Xiaoxiao (female) | Yunxi (male) |
| Korean | SunHi (female) | InJoon (male) |
| *...and 16 more* | | |

---

## 🛠️ Tech Stack

| Layer | Technology | Why This Choice |
|-------|-----------|-----------------|
| **Frontend** | React 18 (Vite) + Tailwind CSS | Fast build times, utility-first CSS for rapid UI development |
| **Backend** | FastAPI (Python) | Async-native, WebSocket support, fast development |
| **Database** | SQLite (dev) → PostgreSQL (prod) | Zero-config locally, production-ready on Render |
| **Real-Time** | WebSockets (native FastAPI) | True bidirectional communication, no polling overhead |
| **Translation** | Groq API — Llama 3.3 70B | Blazing fast inference (276 tok/s), reliable free tier, strong multilingual |
| **Speech-to-Text** | Groq API — Whisper large-v3 | Fastest Whisper endpoint available, multilingual, same API key |
| **Text-to-Speech** | Edge-TTS + gTTS fallback | Free neural voices, 20+ languages, distinct doctor/patient voices |
| **Medical Summary** | Groq API — Llama 3.3 70B | Strong reasoning for structured medical extraction |
| **Deployment** | Render (backend) + Vercel (frontend) | Free tier, easy CI/CD, WebSocket support |

### Why Groq + Llama 3.3 for Translation?

After researching current LLM translation benchmarks (Feb 2026):
- **Qwen-MT (Turbo)** — best-in-class translation model (92 languages) but requires Alibaba Cloud setup, too much overhead for a 12-hour sprint
- **Gemini 2.5 Flash** — excels at Indian languages but free tier was slashed in Dec 2025 (10 RPM, 250 RPD), risky for demo evaluation
- **Llama 3.3 70B on Groq** — strong multilingual capabilities, 276 tokens/second inference, reliable free tier. Optimal for demo stability + speed

The key differentiator is **medical-context-aware prompts** — the system uses role-aware translation that preserves medical terminology accuracy while adapting complexity for patient vs. doctor communication.

---

## 🤖 AI Tools & Resources Leveraged

| Tool | How I Used It |
|------|---------------|
| **Claude (Anthropic)** | Architecture planning, code generation assistance, research on translation LLMs |
| **Groq API** | Core AI provider for translation (Llama 3.3), transcription (Whisper), and summarization |
| **Edge-TTS + gTTS** | Neural text-to-speech for translated audio output |
| **GitHub Copilot** | Code autocompletion during development |
| **Tailwind CSS docs** | UI styling reference |
| **FastAPI docs** | WebSocket implementation reference |

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────┐
│         FRONTEND (React + Vite + Tailwind)         │
│  Role Toggle · Chat UI · Audio Recorder            │
│  Auto-Speak Toggle · TTS Playback                  │
│  Search Modal · Summary Panel · Share Link         │
└────────────┬───────────┬──────────────────────────┘
             │ WebSocket │ REST API
┌────────────▼───────────▼──────────────────────────┐
│              BACKEND (FastAPI)                     │
│  /ws/{id}            Real-time messaging + TTS     │
│  /api/conversations   CRUD operations              │
│  /api/audio           Voice pipeline:              │
│                       Record → Whisper → Translate │
│                       → TTS → Broadcast            │
│  /api/tts             Standalone TTS endpoint      │
│  /api/search          Keyword search               │
│  /api/summary         Medical AI summary           │
│  /api/health          Service health check         │
└──────┬──────────┬──────────┬──────────────────────┘
       │          │          │
┌──────▼─────┐ ┌──▼────────┐ ┌▼──────────────┐
│ PostgreSQL  │ │ Groq API  │ │ Edge-TTS/gTTS │
│ (Messages,  │ │ Llama 3.3 │ │ (Neural       │
│  Summaries, │ │ Whisper   │ │  Voices)      │
│  History)   │ │ large-v3  │ │               │
└────────────┘ └───────────┘ └───────────────┘
```

### Data Flow: Text Message
```
User types message → WebSocket → Llama 3.3 translates
  → Edge-TTS generates audio → Store in DB → Broadcast to room
```

### Data Flow: Voice Message
```
User records audio → Upload → Whisper transcribes → Llama 3.3 translates
  → Edge-TTS generates speech in target language → Store in DB
  → Broadcast original audio + transcription + translation + TTS audio
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Run the server
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` — you're ready to go!

---

## ⚠️ Known Limitations & Trade-offs

| Limitation | Reason | Potential Fix |
|-----------|--------|---------------|
| Audio files stored locally | No cloud storage (S3) in 12hr sprint | Integrate S3 or Cloudinary |
| No user authentication | Focused on core features within time limit | Add JWT auth with role-based access |
| Translation accuracy varies | Llama 3.3 strongest in top-20 languages | Add specialized models as fallback |
| Browser may block autoplay | Browser security policy | Click any 🔊 button once to enable |
| Render free tier cold starts | First request after 15min idle takes ~50s | Use UptimeRobot to keep warm |

---

## 📁 Project Structure

```
healthcare-translator/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # SQLAlchemy connection
│   ├── models.py                # Database models
│   ├── schemas.py               # Pydantic schemas + 20 languages
│   ├── ws_manager.py            # WebSocket room-based connection manager
│   ├── routers/
│   │   ├── conversations.py     # Conversation CRUD
│   │   ├── messages.py          # Message send/receive with translation
│   │   ├── audio.py             # Voice pipeline: Record → STT → Translate → TTS
│   │   ├── summary.py           # AI medical summary
│   │   ├── search.py            # Keyword search
│   │   └── websocket.py         # Real-time WebSocket handler with TTS
│   ├── services/
│   │   ├── groq_service.py      # Groq: Llama translation + Whisper STT + Summaries
│   │   └── tts_service.py       # Edge-TTS + gTTS fallback (20 languages)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AudioRecorder.jsx
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── SearchBar.jsx
│   │   │   └── SummaryPanel.jsx
│   │   ├── pages/
│   │   │   └── ChatPage.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── render.yaml
├── vercel.json
├── .gitignore
└── README.md
```

---

## 📝 License

Built for assessment purposes. Not intended for production medical use without proper regulatory compliance.
