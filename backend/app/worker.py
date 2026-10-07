import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("recipe-worker")


async def main() -> None:
    logger.info("Recipe worker started. Waiting for jobs.")
    while True:
        await asyncio.sleep(30)
        logger.info("Worker heartbeat")


if __name__ == "__main__":
    asyncio.run(main())
