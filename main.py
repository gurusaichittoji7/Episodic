from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()

app = FastAPI(title="Episodic - Personal Chatbot with Memory")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ── Config ───────────────────────────────────────────────────────
MEMORY_FILE = Path("memory.json")
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL_NAME = "claude-haiku-4-5"

SYSTEM_PROMPT = """You are Episodic, a personal AI assistant with memory.
You remember everything from this conversation and refer back to it naturally.
Be concise, thoughtful, and human in your responses."""

# ── Memory helpers ───────────────────────────────────────────────
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

# ── Routes ───────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    history = load_memory()

    # Build Anthropic-compatible messages list
    messages = []
    for turn in history:
        messages.append({"role": "user",      "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["assistant"]})

    # Append current message
    messages.append({"role": "user", "content": req.message})

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages
    )

    reply = response.content[0].text

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