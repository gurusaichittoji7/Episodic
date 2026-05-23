from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = FastAPI(title="Episodic - Personal Chatbot with Memory")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ── Config ──────────────────────────────────────────────────────────────────
MEMORY_FILE = Path("memory.json")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-flash"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

SYSTEM_PROMPT = """You are Episodic, a personal AI assistant with memory.
You remember everything from this conversation and refer back to it naturally.
Be concise, thoughtful, and human in your responses."""

# ── Memory helpers ───────────────────────────────────────────────────────────
def load_memory() -> list[dict]:
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(history: list[dict]):
    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def clear_memory():
    if MEMORY_FILE.exists():
        MEMORY_FILE.unlink()

# ── Routes ───────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    history = load_memory()

    # Build Gemini-compatible history (alternating user/model)
    gemini_history = []
    for turn in history:
        gemini_history.append({"role": "user",  "parts": [turn["user"]]})
        gemini_history.append({"role": "model", "parts": [turn["assistant"]]})

    # Start chat session with history context
    chat_session = model.start_chat(history=gemini_history)

    # Prepend system prompt only on first message
    user_input = req.message
    if not history:
        user_input = f"{SYSTEM_PROMPT}\n\nUser: {req.message}"

    response = chat_session.send_message(user_input)
    reply = response.text

    # Persist turn to memory
    history.append({"user": req.message, "assistant": reply})
    save_memory(history)

    return {"reply": reply, "turn": len(history)}

@app.delete("/memory")
async def reset_memory():
    clear_memory()
    return {"status": "Memory cleared. Fresh start."}

@app.get("/memory")
async def get_memory():
    history = load_memory()
    return {"history": history, "turns": len(history)}