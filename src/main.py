import asyncio
import logging
import sys
import os
import argparse

# Ensure the root directory is in the python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline.orchestrator import PipelineOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(description="Universal Universal E-Commerce Data Miner")
    parser.add_argument("urls", nargs="*", help="List of URLs to scrape.")
    parser.add_argument("--file", "-f", type=str, help="Path to a text file containing URLs.")
    args = parser.parse_args()

    target_urls = args.urls
    if args.file:
        try:
            with open(args.file, "r") as f:
                target_urls.extend([line.strip() for line in f if line.strip()])
        except Exception as e:
            logger.error(f"Failed to read file {args.file}: {e}")
            sys.exit(1)

    if not target_urls:
        logger.error("No target URLs provided. Pass URLs directly or via a --file.")
        parser.print_help()
        sys.exit(1)

    logger.info("Starting Universal Web Miner...")
    logger.info(f"Dispatching {len(target_urls)} URLs to the pipeline.")
    
    orchestrator = PipelineOrchestrator(db_path="universal_inventory.db", num_consumers=2)
    await orchestrator.run(target_urls)
    logger.info("Miner run finished successfully.")

if __name__ == "__main__":
    # Windows Compatibility for asyncio tearing down Event Loops
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
