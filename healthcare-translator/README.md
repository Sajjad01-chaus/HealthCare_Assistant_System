# 🏥 MediTranslate — Healthcare Doctor-Patient Translation App

> Real-time AI-powered translation bridge between doctors and patients, breaking language barriers in healthcare.

**🔗 Live Demo:** [your-deployed-link-here]  
**📂 Repository:** [your-github-link-here]

---

## 📌 Project Overview

MediTranslate is a full-stack web application that enables real-time communication between doctors and patients who speak different languages. It supports text chat, voice messages (with automatic transcription), AI-powered translation, conversation persistence, keyword search, and intelligent medical summarization.

Built for the Pre-Interview Take-Home Assignment — designed and developed within a **12-hour** time constraint.

---

## ✅ Features Attempted & Completed

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 1 | **Real-Time Translation** | ✅ Complete | WebSocket-based instant translation between Doctor ↔ Patient |
| 2 | **Text Chat Interface** | ✅ Complete | Clean WhatsApp-style UI with role-based message bubbles |
| 3 | **Audio Recording & Storage** | ✅ Complete | Browser-based recording → Whisper transcription → translation → playable in chat |
| 4 | **Conversation Logging** | ✅ Complete | All messages persisted in PostgreSQL with timestamps |
| 5 | **Conversation Search** | ✅ Complete | Keyword search across messages with highlighted context |
| 6 | **AI Medical Summary** | ✅ Complete | Structured extraction of symptoms, diagnoses, medications, follow-ups |

### Bonus Features
- 🔗 **Shareable Room Links** — Doctor can share a URL for the patient to join
- 🌐 **20 Languages Supported** — Including Hindi, Bengali, Tamil, Telugu, Urdu, Arabic, etc.
- 🎯 **Role Toggle** — Switch between Doctor/Patient view on the same device
- 📱 **Mobile-Responsive UI** — Works on phones and tablets
- 🗣️ **Auto Language Detection** — Whisper auto-detects the spoken language

---

## 🛠️ Tech Stack

| Layer | Technology | Why This Choice |
|-------|-----------|-----------------|
| **Frontend** | React 18 (Vite) + Tailwind CSS | Fast build times, utility-first CSS for rapid UI development |
| **Backend** | FastAPI (Python) | Async-native, WebSocket support, fast development |
| **Database** | SQLite (dev) → PostgreSQL (prod) | Zero-config locally, production-ready on Render |
| **Real-Time** | WebSockets (native FastAPI) | True bidirectional communication, no polling overhead |
| **Translation** | Groq API — Llama 3.3 70B | Blazing fast inference (276 tok/s), free tier, strong multilingual support |
| **Speech-to-Text** | Groq API — Whisper large-v3 | Fastest Whisper available, multilingual, same API key |
| **Medical Summary** | Groq API — Llama 3.3 70B | Strong reasoning for structured medical extraction |
| **Deployment** | Render (backend) + Vercel (frontend) | Free tier, easy CI/CD |

### Why Groq + Llama 3.3 for Translation?

After researching current LLM translation benchmarks (Feb 2026):
- **Qwen-MT (Turbo)** is the current best-in-class translation model (92 languages, $0.5/M tokens) but requires Alibaba Cloud setup — too much overhead for a 12-hour sprint
- **Gemini 2.5 Flash** excels at Indian languages but free tier was slashed in Dec 2025 (5 RPM, 100 RPD) — risky for demo evaluation
- **Llama 3.3 70B on Groq** offers strong multilingual capabilities, 276 tokens/second inference speed, and a reliable free tier — optimal for demo stability + speed

The key differentiator is **medical-context-aware prompts** — the system uses role-aware translation that preserves medical terminology accuracy while adapting complexity for patient vs. doctor communication.

---

## 🤖 AI Tools & Resources Leveraged

| Tool | How I Used It |
|------|---------------|
| **Claude (Anthropic)** | Architecture planning, code generation assistance, research on translation LLMs |
| **Groq API** | Core AI provider for translation, transcription, and summarization |
| **GitHub Copilot** | Code autocompletion during development |
| **Tailwind CSS docs** | UI styling reference |
| **FastAPI docs** | WebSocket implementation reference |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│         FRONTEND (React + Vite + Tailwind)    │
│  Role Toggle · Chat UI · Audio Recorder       │
│  Search Modal · Summary Panel                 │
└────────────┬───────────┬─────────────────────┘
             │ WebSocket │ REST API
┌────────────▼───────────▼─────────────────────┐
│            BACKEND (FastAPI)                   │
│  /ws/{id}           Real-time messaging        │
│  /api/conversations  CRUD operations           │
│  /api/audio          Upload → Whisper → Store  │
│  /api/search         Keyword search            │
│  /api/summary        Medical AI summary        │
└──────────────────┬───────────────────────────┘
                   │
            ┌──────▼──────┐     ┌─────────────┐
            │ PostgreSQL   │     │  Groq API    │
            │ (Messages,   │     │  Llama 3.3   │
            │  History)    │     │  Whisper v3   │
            └─────────────┘     └─────────────┘
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

# Create .env file
cp .env.example .env.local
# Set VITE_API_URL if backend is not on localhost:8000

# Run the dev server
npm run dev
```

Open `http://localhost:5173` — you're ready to go!

---

## ⚠️ Known Limitations & Trade-offs

| Limitation | Reason | Potential Fix |
|-----------|--------|---------------|
| Audio files stored locally | File storage not on cloud (S3/Cloudinary) in 12hr | Integrate S3 or Cloudinary for production |
| No user authentication | Focused on core features within time limit | Add JWT auth with role-based access |
| Translation accuracy for rare languages | Llama 3.3 is strongest in top-20 languages | Add Qwen-MT or Gemini as fallback for specific language pairs |
| No real-time typing indicator | WebSocket supports it but not implemented in UI | Add "typing..." event broadcasting |
| Summary doesn't persist audio analysis | Audio is transcribed then treated as text | Could analyze audio tone/urgency directly |

---

## 📁 Project Structure

```
healthcare-translator/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy connection
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas + language list
│   ├── ws_manager.py        # WebSocket connection manager
│   ├── routers/
│   │   ├── conversations.py # Conversation CRUD
│   │   ├── messages.py      # Message send/receive
│   │   ├── audio.py         # Audio upload + transcription
│   │   ├── summary.py       # AI medical summary
│   │   ├── search.py        # Conversation search
│   │   └── websocket.py     # Real-time WebSocket handler
│   ├── services/
│   │   └── groq_service.py  # All Groq AI integration
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
├── render.yaml              # Render deployment config
├── vercel.json              # Vercel deployment config
├── .gitignore
└── README.md
```

---

## 📝 License

Built for assessment purposes. Not intended for production medical use.
