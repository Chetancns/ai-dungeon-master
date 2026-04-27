from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.models.schemas import (
    CreateGameRequest,
    CreateGameResponse,
    JoinGameRequest,
    JoinGameResponse,
    LeaveGameRequest,
    StartGameRequest,
    StoryEvent,
)
from backend.services import game_service, dm_service

router = APIRouter(prefix="/api/game", tags=["game"])


@router.post("/create", response_model=CreateGameResponse)
def create_game(body: CreateGameRequest):
    session, player_id = game_service.create_game(
        creator_name=body.creator_name,
        character_name=body.character_name,
        character_class=body.character_class,
        game_style=body.game_style,
        max_players=body.max_players,
    )
    return CreateGameResponse(game_id=session.game_id, player_id=player_id, game_session=session)


@router.post("/join/{game_id}", response_model=JoinGameResponse)
def join_game(game_id: str, body: JoinGameRequest):
    try:
        session, player_id = game_service.join_game(
            game_id=game_id,
            player_name=body.player_name,
            character_name=body.character_name,
            character_class=body.character_class,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return JoinGameResponse(player_id=player_id, game_session=session)


@router.get("/{game_id}")
def get_game(game_id: str):
    session = game_service.get_game(game_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return session


@router.post("/{game_id}/start")
def start_game(game_id: str, body: StartGameRequest):
    try:
        session = game_service.start_game(game_id=game_id, player_id=body.player_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Generate opening narration
    try:
        opening = dm_service.generate_opening(session)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DM service error: {exc}")

    event = StoryEvent(
        role="dm",
        player_name=None,
        content=opening,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    session = game_service.append_story_event(game_id, event)
    return session


@router.post("/{game_id}/leave")
def leave_game(game_id: str, body: LeaveGameRequest):
    session = game_service.get_game(game_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game not found")
    session = game_service.leave_game(game_id=game_id, player_id=body.player_id)
    return session
