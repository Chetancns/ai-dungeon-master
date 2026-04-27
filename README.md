# ⚔️ AI Dungeon Master

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-latest-orange)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-purple?logo=openai)
![Vanilla JS](https://img.shields.io/badge/Frontend-Vanilla%20JS-yellow?logo=javascript)

A full-stack AI-powered RPG web application where users can **create or join game sessions**. GPT-4o acts as the Dungeon Master, narrating the story and responding to player actions. LangChain provides per-session memory so the DM remembers everything that happened in the game.

---

## ✨ Features

- 🎲 **AI Dungeon Master** — GPT-4o narrates vivid, immersive stories tailored to your chosen genre
- 🧠 **Persistent Memory** — LangChain `ConversationBufferMemory` keeps full context per game session
- 🎮 **Multiplayer (1–4 players)** — Create a game, share the 6-character ID, friends join instantly
- 🌍 **5 Game Styles** — Fantasy, Sci-Fi, Horror, Mystery, Post-Apocalyptic
- 🗡️ **5 Character Classes** — Warrior, Mage, Rogue, Ranger, Cleric
- 🎨 **Dark Fantasy UI** — Parchment-style story log, gold accents, responsive design
- ⚡ **Real-time Sync** — Polling every 2 seconds keeps all players in sync
- 🔒 **No Auth Required** — UUID-based player IDs stored in `localStorage`

---

## 📸 Screenshots

<img width="1105" height="866" alt="image" src="https://github.com/user-attachments/assets/d48ba333-c5e4-4585-8088-f1ae0aae6b3d" />


---

## 🗂️ Project Structure

```
ai-dungeon-master/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── routers/
│   │   ├── game.py              # Game CRUD routes
│   │   └── action.py            # Player action route
│   ├── services/
│   │   ├── dm_service.py        # LangChain + GPT-4o Dungeon Master
│   │   └── game_service.py      # In-memory game session management
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── memory/
│   │   └── session_memory.py    # Per-game ConversationBufferMemory
│   └── requirements.txt
├── frontend/
│   ├── index.html               # Landing page (Create / Join)
│   ├── lobby.html               # Game lobby
│   ├── game.html                # Main game screen
│   ├── css/
│   │   └── style.css            # Dark fantasy theme
│   └── js/
│       ├── app.js               # Landing page logic
│       ├── lobby.js             # Lobby polling + start game
│       └── game.js              # Game loop, actions, story rendering
├── .env.example
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone the repository
```bash
git clone https://github.com/Chetancns/ai-dungeon-master.git
cd ai-dungeon-master
```

### 2. Install Python dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Configure your OpenAI API key
```bash
cp .env.example .env
# Edit .env and replace with your actual key:
# OPENAI_API_KEY=sk-...
```

### 4. Start the backend server
```bash
uvicorn backend.main:app --reload
```
The API will be available at `http://localhost:8000`.  
Interactive API docs: `http://localhost:8000/docs`

### 5. Open the frontend
Open `frontend/index.html` in your browser (or use VS Code **Live Server** extension for the best experience).

---

## 🎮 How to Play

1. **Create a Game** — Fill in your name, character details, choose a game style and max players. You'll receive a **6-character Game ID**.
2. **Share the ID** — Give the Game ID to your friends so they can join via the **Join Game** form.
3. **Wait in the Lobby** — All players appear in the lobby. The creator starts the game when ready.
4. **Adventure Begins** — The AI Dungeon Master sets the scene with an immersive opening narration.
5. **Take Actions** — Type what your character does and submit. The DM responds, advancing the story for everyone.
6. **Enjoy the Story** — The DM remembers the full session history and weaves all players' actions together.

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/game/create` | Create a new game session |
| `POST` | `/api/game/join/{game_id}` | Join an existing game |
| `GET`  | `/api/game/{game_id}` | Get full game state (lobby/game polling) |
| `POST` | `/api/game/{game_id}/start` | Start the game (creator only) |
| `POST` | `/api/game/{game_id}/leave` | Leave a game session |
| `POST` | `/api/action/{game_id}` | Submit a player action → get DM response |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) + Python |
| **AI / LLM** | [OpenAI GPT-4o](https://openai.com/) via [LangChain](https://langchain.com/) |
| **Memory** | LangChain `InMemoryChatMessageHistory` (per session) |
| **Frontend** | Vanilla HTML / CSS / JavaScript |
| **Fonts** | Google Fonts — Cinzel + Lato |
| **Session Storage** | In-memory Python dict (no database required) |

---

## 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key for GPT-4o access |

---

## 📄 License

MIT — use freely, modify, and share!
