import asyncio
import logging
import uuid
from src.common.agents.registry import get_note_optimizer_agent
from src.common.database import SessionLocal
from src.common.repos.notes import UserNoteRepository
from src.common.repos.chat import UserMessageRepository

logger = logging.getLogger(__name__)

async def run_chat_stream(chat_agent, inputs, config):
    """
    Streams the chat agent and then kicks off the note optimizer asynchronously 
    ONLY if notes were saved or profile was updated.
    Also audits the chat run.
    """
    user_id = inputs.get("user_id")
    thread_id_str = config.get("configurable", {}).get("thread_id")
    thread_id = uuid.UUID(thread_id_str) if thread_id_str else None
    
    db = SessionLocal()
    message_repo = UserMessageRepository(db)
    chat_run = None
    
    if user_id and thread_id:
        chat_run = message_repo.start_chat_run(uuid.UUID(user_id), thread_id)
        # Pass chat_run_id to the state/config if needed by nodes, 
        # but for now we'll handle errors in the nodes themselves or here.
        config["configurable"]["chat_run_id"] = str(chat_run.id)

    notes_saved = False
    try:
        async for chunk_data in chat_agent.astream(inputs, config=config, stream_mode="messages"):
            chunk, metadata = chunk_data
            
            # Only yield chunks from the chat node to avoid leaking other node outputs (like title updates)
            if metadata.get("langgraph_node") == "chat":
                yield chunk_data
            
            # Check if this chunk contains a tool call to save_user_note or update_user_profile
            # Tool calls are usually in the 'chat' node chunks anyway
            if hasattr(chunk, "tool_calls") and chunk.tool_calls:
                for tool_call in chunk.tool_calls:
                    if tool_call["name"] in ["save_user_note", "update_user_profile"]:
                        notes_saved = True
        
        # If we reached here, the chat was successful
        if chat_run:
            message_repo.end_chat_run(chat_run.id, status="COMPLETED")
            
    except Exception as e:
        logger.error(f"Error during chat run: {e}")
        if chat_run:
            message_repo.end_chat_run(chat_run.id, status="FAILED")
        raise e
    finally:
        db.close()
    
    # Kick off note optimizer asynchronously after streaming is done, if notes were saved
    if user_id and notes_saved:
        db = SessionLocal()
        try:
            repo = UserNoteRepository(db)
            if repo.start_optimization_run(user_id, thread_id=thread_id):
                optimizer = get_note_optimizer_agent()
                asyncio.create_task(optimizer.ainvoke({
                    "user_id": user_id,
                    "thread_id": str(thread_id) if thread_id else None
                }))
            else:
                logger.info(f"Note optimization already in progress for user {user_id}. Skipping.")
        finally:
            db.close()
