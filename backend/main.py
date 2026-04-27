from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import game, action

app = FastAPI(title="AI Dungeon Master", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game.router)
app.include_router(action.router)


@app.get("/")
def root():
    return {"message": "AI Dungeon Master API is running ⚔️"}
