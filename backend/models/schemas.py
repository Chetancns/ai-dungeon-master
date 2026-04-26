from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class GameStyle(str, Enum):
    fantasy = "Fantasy"
    sci_fi = "Sci-Fi"
    horror = "Horror"
    mystery = "Mystery"
    post_apocalyptic = "Post-Apocalyptic"


class CharacterClass(str, Enum):
    warrior = "Warrior"
    mage = "Mage"
    rogue = "Rogue"
    ranger = "Ranger"
    cleric = "Cleric"


class GameStatus(str, Enum):
    waiting = "waiting"
    in_progress = "in_progress"
    finished = "finished"


class Player(BaseModel):
    player_id: str
    player_name: str
    character_name: str
    character_class: str


class StoryEvent(BaseModel):
    role: str  # "dm" or "player"
    player_name: Optional[str] = None
    content: str
    timestamp: str


class GameSession(BaseModel):
    game_id: str
    game_style: str
    max_players: int
    players: List[Player] = []
    status: GameStatus = GameStatus.waiting
    story_log: List[StoryEvent] = []
    created_at: str


# Request / Response models

class CreateGameRequest(BaseModel):
    creator_name: str
    character_name: str
    character_class: str
    game_style: str
    max_players: int = Field(ge=1, le=4)


class CreateGameResponse(BaseModel):
    game_id: str
    player_id: str
    game_session: GameSession


class JoinGameRequest(BaseModel):
    player_name: str
    character_name: str
    character_class: str


class JoinGameResponse(BaseModel):
    player_id: str
    game_session: GameSession


class StartGameRequest(BaseModel):
    player_id: str


class LeaveGameRequest(BaseModel):
    player_id: str


class ActionRequest(BaseModel):
    player_id: str
    action: str


class ActionResponse(BaseModel):
    dm_response: str
    story_log: List[StoryEvent]
