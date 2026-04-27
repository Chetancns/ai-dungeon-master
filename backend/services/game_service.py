import uuid
from datetime import datetime, timezone
from typing import Optional

from backend.models.schemas import GameSession, GameStatus, Player, StoryEvent

# In-memory store: game_id -> GameSession
_games: dict[str, GameSession] = {}


def _generate_game_id() -> str:
    """Generate a unique 6-character alphanumeric game ID."""
    import random
    import string
    while True:
        game_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if game_id not in _games:
            return game_id


def create_game(
    creator_name: str,
    character_name: str,
    character_class: str,
    game_style: str,
    max_players: int,
) -> tuple[GameSession, str]:
    """Create a new game session. Returns (session, player_id)."""
    game_id = _generate_game_id()
    player_id = str(uuid.uuid4())
    player = Player(
        player_id=player_id,
        player_name=creator_name,
        character_name=character_name,
        character_class=character_class,
    )
    session = GameSession(
        game_id=game_id,
        game_style=game_style,
        max_players=max_players,
        players=[player],
        status=GameStatus.waiting,
        story_log=[],
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    _games[game_id] = session
    return session, player_id


def get_game(game_id: str) -> Optional[GameSession]:
    """Return a game session by ID, or None if not found."""
    return _games.get(game_id)


def join_game(
    game_id: str,
    player_name: str,
    character_name: str,
    character_class: str,
) -> tuple[GameSession, str]:
    """
    Add a player to an existing game session.
    Returns (session, player_id).
    Raises ValueError if the game is full or already started.
    """
    session = _games.get(game_id)
    if session is None:
        raise ValueError("Game not found")
    if session.status != GameStatus.waiting:
        raise ValueError("Game has already started")
    if len(session.players) >= session.max_players:
        raise ValueError("Game is full")

    player_id = str(uuid.uuid4())
    player = Player(
        player_id=player_id,
        player_name=player_name,
        character_name=character_name,
        character_class=character_class,
    )
    session.players.append(player)
    return session, player_id


def start_game(game_id: str, player_id: str) -> GameSession:
    """
    Mark the game as in_progress.
    Only the creator (first player) can start.
    """
    session = _games.get(game_id)
    if session is None:
        raise ValueError("Game not found")
    if not session.players:
        raise ValueError("No players in game")
    if session.players[0].player_id != player_id:
        raise ValueError("Only the creator can start the game")
    if session.status != GameStatus.waiting:
        raise ValueError("Game is not in waiting state")
    session.status = GameStatus.in_progress
    if session.players:
        session.current_turn_player_id = session.players[0].player_id
    return session


def append_story_event(game_id: str, event: StoryEvent) -> GameSession:
    """Append a story event to the game's story log."""
    session = _games.get(game_id)
    if session is None:
        raise ValueError("Game not found")
    session.story_log.append(event)
    return session


def advance_turn(game_id: str) -> GameSession:
    """Rotate current_turn_player_id to the next player in the list."""
    session = _games.get(game_id)
    if session is None:
        raise ValueError("Game not found")
    if not session.players:
        return session
    ids = [p.player_id for p in session.players]
    try:
        idx = ids.index(session.current_turn_player_id)
    except ValueError:
        idx = -1
    session.current_turn_player_id = ids[(idx + 1) % len(ids)]
    return session


def leave_game(game_id: str, player_id: str) -> GameSession:
    """Remove a player from a game session."""
    session = _games.get(game_id)
    if session is None:
        raise ValueError("Game not found")
    session.players = [p for p in session.players if p.player_id != player_id]
    return session


def get_player(session: GameSession, player_id: str) -> Optional[Player]:
    """Find a player in a session by player_id."""
    for p in session.players:
        if p.player_id == player_id:
            return p
    return None
