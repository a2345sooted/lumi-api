import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.cors import setup_cors
from src.logging_config import setup_logging
from src.services.checkpointer import init_checkpointer, close_checkpointer

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up lumi...")
    # Initialize checkpointer
    await init_checkpointer()
    yield
    logger.info("Shutting down lumi...")
    await close_checkpointer()

app = FastAPI(lifespan=lifespan)

setup_cors(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
