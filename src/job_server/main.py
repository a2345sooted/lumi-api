import asyncio
import logging
from src.common.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting up job server...")
    while True:
        logger.info("Job server is running and waiting for jobs...")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
