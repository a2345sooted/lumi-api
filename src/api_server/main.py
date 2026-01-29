import logging
import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", "1982"))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.common.cors import setup_cors
from src.common.logging_config import setup_logging

from src.common.services.checkpointer import init_checkpointer, close_checkpointer, get_checkpointer
from src.api_server.api.websockets.router import router as ws_router
from src.api_server.api.chat.router import router as chat_router
from src.api_server.api.water.router import router as water_router
from src.api_server.api.users.router import router as users_router
from src.api_server.agents.chat.agent import compile_chat_agent
from src.common.agents.note_optimizer.agent import compile_note_optimizer_agent
from src.common.agents.registry import register_chat_agent, register_note_optimizer_agent

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting up lumi on port {PORT}...")
    # Initialize checkpointer
    checkpointer = await init_checkpointer()
    
    # Compile chat agent with checkpointer
    chat_agent = compile_chat_agent(checkpointer=checkpointer)
    register_chat_agent(chat_agent)
    logger.info("Chat agent compiled and registered with persistent checkpointer")

    # Compile and register note optimizer agent
    note_optimizer_agent = compile_note_optimizer_agent()
    register_note_optimizer_agent(note_optimizer_agent)
    logger.info("Note optimizer agent compiled and registered")
    
    yield
    logger.info("Shutting down lumi...")
    await close_checkpointer()

app = FastAPI(lifespan=lifespan)

setup_cors(app)

app.include_router(ws_router)
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(water_router, prefix="/api/water", tags=["water"])
app.include_router(users_router, prefix="/api/users", tags=["users"])


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    reload = os.getenv("RELOAD", "true").lower() == "true"
    uvicorn.run("src.api_server.main:app", host="0.0.0.0", port=PORT, reload=reload)
