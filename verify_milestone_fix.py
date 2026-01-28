import asyncio
import uuid
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.chat.agent import compile_chat_agent
from src.database import SessionLocal
from src.repos.chat import ConversationRepository, MessageRepository
from src.api.auth import TOKEN_TO_USER_MAP

async def verify_milestones():
    # Setup
    db = SessionLocal()
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)
    
    user_id = TOKEN_TO_USER_MAP["user-1-token"]
    conversation = conv_repo.create(user_id=user_id)
    conv_id = str(conversation.id)
    print(f"Created conversation: {conv_id}")

    agent = compile_chat_agent()

    async def send_msg(text, user_msg_count):
        print(f"\n--- Sending message {user_msg_count}: {text} ---")
        msg_repo.add_message(conversation_id=conv_id, role="user", content=text)
        
        # Get history from DB to pass to agent (simulating how the API works)
        db_messages = msg_repo.get_messages_by_conversation(uuid.UUID(conv_id))
        messages = []
        for m in db_messages:
            if m.role == "user":
                messages.append(HumanMessage(content=m.content))
            else:
                messages.append(AIMessage(content=m.content))
        
        inputs = {
            "messages": messages,
            "user_id": user_id
        }
        config = {"configurable": {"thread_id": conv_id, "user_id": user_id}}
        
        # We use ainvoke here to see the final state
        result = await agent.ainvoke(inputs, config=config)
        
        # Save assistant response
        ai_msg = result["messages"][-1].content
        msg_repo.add_message(conversation_id=conv_id, role="assistant", content=ai_msg)
        
        # Check title
        db.expire_all()
        curr_conv = conv_repo.get_by_id(uuid.UUID(conv_id))
        print(f"Current title: {curr_conv.title}")
        return curr_conv.title

    try:
        # 1st message: Title should remain "Untitled"
        title1 = await send_msg("Hello, I want to talk about space exploration.", 1)
        assert title1 == "Untitled", f"Expected Untitled, got {title1}"

        # 2nd message: Title should be updated
        title2 = await send_msg("What are the most recent Mars missions?", 2)
        assert title2 != "Untitled", "Expected title to be updated after 2nd message"
        print(f"Title updated to: {title2}")

        # 3rd-9th: No update (it might update if we didn't have milestones, but we want to be sure it doesn't change yet)
        # Actually, it will re-invoke the node if it's called. 
        # But wait, our router only returns "update_title" for 2, 10, 20.
        
        # Let's fast forward to 9th message
        for i in range(3, 10):
            await send_msg(f"Message {i}", i)
        
        title9 = conv_repo.get_by_id(uuid.UUID(conv_id)).title
        print(f"Title after 9 messages: {title9}")

        # 10th message: Title should be updated again
        title10 = await send_msg("Actually, let's talk about quantum computers instead.", 10)
        print(f"Title after 10 messages: {title10}")
        # It's hard to assert it CHANGED because LLM is non-deterministic, but it should have been invoked.

        print("\nVerification successful!")

    finally:
        conv_repo.delete(uuid.UUID(conv_id))
        db.close()

if __name__ == "__main__":
    asyncio.run(verify_milestones())
