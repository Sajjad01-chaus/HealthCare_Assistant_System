import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from routers import conversations, messages, audio, summary, search, websocket
from schemas import SUPPORTED_LANGUAGES

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Doctor-Patient Translation API",
    description="Real-time translation bridge between doctors and patients using AI",
    version="1.0.0",
)

# CORS - Allow frontend to connect
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
        "https://health-care-assistant-system.vercel.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount audio files directory for serving
AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_files")
os.makedirs(AUDIO_DIR, exist_ok=True)
app.mount("/api/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

# Register all routers
app.include_router(conversations.router)
app.include_router(messages.router)
app.include_router(audio.router)
app.include_router(summary.router)
app.include_router(search.router)
app.include_router(websocket.router)


# --- Health & Info Endpoints ---
@app.get("/")
def root():
    return {
        "app": "Healthcare Doctor-Patient Translation API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "ai_provider": "Groq (Llama 3.3 70B + Whisper large-v3)",
    }


@app.get("/api/languages")
def get_supported_languages():
    """Return list of supported languages."""
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in SUPPORTED_LANGUAGES.items()
        ]
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
