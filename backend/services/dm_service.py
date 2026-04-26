import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from memory.session_memory import get_history
from models.schemas import GameSession

load_dotenv()


def _build_system_prompt(session: GameSession) -> str:
    player_lines = "\n".join(
        f"- {p.player_name} ({p.character_class} named {p.character_name})"
        for p in session.players
    )
    return (
        f"You are an expert Dungeon Master running a {session.game_style} RPG adventure.\n\n"
        f"The players in this session are:\n{player_lines}\n\n"
        "Your role:\n"
        "- Narrate vivid, immersive scenes tailored to the genre\n"
        "- Respond to each player's action and advance the story\n"
        "- Remember ALL past events in this session\n"
        "- Keep responses between 100-200 words unless dramatic moments require more\n"
        "- Address players by their CHARACTER names\n"
        "- Create tension, mystery, and fun — be creative!\n"
        "- When multiple players are present, include all characters in the narrative\n"
        "- Never break character"
    )


def _get_chain(session: GameSession) -> RunnableWithMessageHistory:
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.85,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
    system_prompt = _build_system_prompt(session)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    chain = prompt | llm

    chain_with_history = RunnableWithMessageHistory(
        chain,
        # LangChain calls this lambda with the session_id from config["configurable"]
        # to retrieve (or create) the correct per-game chat history.
        lambda session_id: get_history(session_id),
        input_messages_key="input",
        history_messages_key="history",
    )
    return chain_with_history


def generate_opening(session: GameSession) -> str:
    """Generate the opening narration when the game starts."""
    player_count = len(session.players)
    player_descriptions = ", ".join(
        f"{p.character_name} the {p.character_class}" for p in session.players
    )
    opening_prompt = (
        f"The adventure begins! Set the scene for our {session.game_style} adventure "
        f"with {player_count} adventurer(s): {player_descriptions}. "
        "Introduce the world, the immediate situation, and give the players their first "
        "challenge or hook. Make it exciting!"
    )
    chain = _get_chain(session)
    response = chain.invoke(
        {"input": opening_prompt},
        config={"configurable": {"session_id": session.game_id}},
    )
    return response.content


def process_action(session: GameSession, player_name: str, character_name: str, action: str) -> str:
    """Process a player action and return the DM's response."""
    human_message = f"[{player_name} as {character_name}]: {action}"
    chain = _get_chain(session)
    response = chain.invoke(
        {"input": human_message},
        config={"configurable": {"session_id": session.game_id}},
    )
    return response.content
