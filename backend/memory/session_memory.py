from langchain_core.chat_history import InMemoryChatMessageHistory

# Dict mapping game_id -> InMemoryChatMessageHistory
_session_histories: dict = {}


def get_history(game_id: str) -> InMemoryChatMessageHistory:
    """Return the existing chat history for a game session, or create a new one."""
    if game_id not in _session_histories:
        _session_histories[game_id] = InMemoryChatMessageHistory()
    return _session_histories[game_id]


def delete_history(game_id: str) -> None:
    """Remove the chat history for a game session."""
    _session_histories.pop(game_id, None)
