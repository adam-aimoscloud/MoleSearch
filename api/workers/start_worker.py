#!/usr/bin/env python3
"""
Worker startup script for MoleSearch async tasks
"""

import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workers.async_worker import start_worker
from utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    """Main function to start the worker"""
    try:
        logger.info("Starting MoleSearch async worker...")
        await start_worker()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 