import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.cors import setup_cors
from src.logging_config import setup_logging
from src.services.checkpointer import init_checkpointer, close_checkpointer, get_checkpointer
from src.api.websockets.router import router as ws_router
from src.api.chat.router import router as chat_router
from src.agents.chat.agent import compile_chat_agent
from src.agents.registry import register_chat_agent

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up lumi...")
    # Initialize checkpointer
    checkpointer = await init_checkpointer()
    
    # Compile chat agent with checkpointer
    chat_agent = compile_chat_agent(checkpointer=checkpointer)
    register_chat_agent(chat_agent)
    logger.info("Chat agent compiled and registered with persistent checkpointer")
    
    yield
    logger.info("Shutting down lumi...")
    await close_checkpointer()

app = FastAPI(lifespan=lifespan)

setup_cors(app)

app.include_router(ws_router)
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])


@app.get("/")
async def root():
    return {"message": "Hello World"}
