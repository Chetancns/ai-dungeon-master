from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from models.schemas import ActionRequest, ActionResponse, StoryEvent
from services import game_service, dm_service

router = APIRouter(prefix="/api/action", tags=["action"])


@router.post("/{game_id}", response_model=ActionResponse)
def submit_action(game_id: str, body: ActionRequest):
    session = game_service.get_game(game_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game not found")

    player = game_service.get_player(session, body.player_id)
    if player is None:
        raise HTTPException(status_code=403, detail="Player not found in this game")

    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Game is not in progress")

    # Append player action to story log
    player_event = StoryEvent(
        role="player",
        player_name=player.player_name,
        content=body.action,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    game_service.append_story_event(game_id, player_event)

    # Get DM response
    try:
        dm_response = dm_service.process_action(
            session=session,
            player_name=player.player_name,
            character_name=player.character_name,
            action=body.action,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DM service error: {exc}")

    # Append DM response to story log
    dm_event = StoryEvent(
        role="dm",
        player_name=None,
        content=dm_response,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    session = game_service.append_story_event(game_id, dm_event)

    return ActionResponse(dm_response=dm_response, story_log=session.story_log)
