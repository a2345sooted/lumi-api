import asyncio
import logging
from src.agents.registry import get_note_optimizer_agent
from src.database import SessionLocal
from src.repos.notes import UserNoteRepository

logger = logging.getLogger(__name__)

async def run_chat_stream(chat_agent, inputs, config):
    """
    Streams the chat agent and then kicks off the note optimizer asynchronously 
    ONLY if notes were saved or profile was updated.
    """
    notes_saved = False
    async for chunk_data in chat_agent.astream(inputs, config=config, stream_mode="messages"):
        yield chunk_data
        
        chunk, metadata = chunk_data
        # Check if this chunk contains a tool call to save_user_note or update_user_profile
        if hasattr(chunk, "tool_calls") and chunk.tool_calls:
            for tool_call in chunk.tool_calls:
                if tool_call["name"] in ["save_user_note", "update_user_profile"]:
                    notes_saved = True
    
    # Kick off note optimizer asynchronously after streaming is done, if notes were saved
    user_id = inputs.get("user_id")
    if user_id and notes_saved:
        db = SessionLocal()
        try:
            repo = UserNoteRepository(db)
            if repo.start_optimization_run(user_id):
                optimizer = get_note_optimizer_agent()
                asyncio.create_task(optimizer.ainvoke({"user_id": user_id}))
            else:
                logger.info(f"Note optimization already in progress for user {user_id}. Skipping.")
        finally:
            db.close()
