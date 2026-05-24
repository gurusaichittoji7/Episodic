# 🧠 Episodic
### *Named after episodic memory, the human brain's ability to recall specific past experiences.*

## Live Demo
http://44.249.245.134

## What it does
Episodic is a personal AI chatbot that remembers every conversation. Unlike standard LLM APIs which are stateless, Episodic persists your full chat history to a JSON file and passes the entire context back to Claude on every turn simulating human,like memory.

## Tech Stack
- **FastAPI** — backend framework
- **Claude Haiku** — LLM (Anthropic)
- **JSON file** — persistent memory storage
- **Nginx + systemd** — production serving & auto-restart
- **AWS Lightsail** — cloud deployment

## Local Setup
```bash
git clone https://github.com/gurusaichittoji7/episodic.git
cd episodic
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your ANTHROPIC_API_KEY
python -m uvicorn main:app --reload
```
Open http://localhost:8000


## How Memory Works
```
User sends message
       ↓
Load memory.json → [turn1, turn2, turn3, ...]
       ↓
Rebuild full conversation history
       ↓
Send to Claude with complete context
       ↓
Append new turn to memory.json
       ↓
Return reply to frontend
```