from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.models.schemas import ActionRequest, ActionResponse, StoryEvent
from backend.services import game_service, dm_service

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

    # Enforce turn order in multi-player games
    if (
        len(session.players) > 1
        and session.current_turn_player_id
        and session.current_turn_player_id != body.player_id
    ):
        raise HTTPException(status_code=403, detail="It's not your turn")

    # Determine who acts next (before advancing the turn)
    next_character_name = None
    if len(session.players) > 1:
        ids = [p.player_id for p in session.players]
        try:
            idx = ids.index(session.current_turn_player_id)
            next_p = session.players[(idx + 1) % len(session.players)]
            next_character_name = next_p.character_name
        except ValueError:
            pass

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
            next_character_name=next_character_name,
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

    # Advance to the next player's turn
    session = game_service.advance_turn(game_id)

    return ActionResponse(
        dm_response=dm_response,
        story_log=session.story_log,
        current_turn_player_id=session.current_turn_player_id,
    )
