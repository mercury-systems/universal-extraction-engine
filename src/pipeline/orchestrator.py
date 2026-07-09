import asyncio
import logging
from typing import List
from src.scraper.producer import RawIngestionService
from src.parser.streaming_parser import parse_html_stream
from src.storage.db import StorageEngine

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    def __init__(self, db_path: str = "inventory.db", num_consumers: int = 4):
        self.payload_queue = asyncio.Queue(maxsize=100)
        self.results_queue = asyncio.Queue(maxsize=500)
        self.num_consumers = num_consumers
        self.ingestion_service = RawIngestionService()
        self.storage_engine = StorageEngine(db_path=db_path)

    async def producer_worker(self, urls: List[str]):
        """
        Engine A: Consumes raw target URLs, fetches payload, puts into queue.
        """
        for url in urls:
            logger.debug(f"Producer fetching: {url}")
            html_bytes = await self.ingestion_service.fetch_html_bytes(url)
            if html_bytes:
                await self.payload_queue.put((url, html_bytes))
            else:
                logger.warning(f"Producer failed to fetch content for {url}")

    async def consumer_worker(self):
        """
        Engine B: Pulls payloads, parses them, puts validated objects to results queue.
        """
        while True:
            url, html_bytes = await self.payload_queue.get()
            try:
                for item in parse_html_stream(url, html_bytes):
                    await self.results_queue.put(item)
            except Exception as e:
                logger.error(f"Error parsing payload from {url}: {e}")
            finally:
                self.payload_queue.task_done()

    async def writer_worker(self):
        """
        Storage Engine: Dedicated thread to consume results and write to WAL SQLite.
        """
        await self.storage_engine.initialize()
        while True:
            product = await self.results_queue.get()
            try:
                await self.storage_engine.ingest_item(product)
            except Exception as e:
                logger.error(f"Error writing product {product.sku}: {e}")
            finally:
                self.results_queue.task_done()

    async def run(self, target_urls: List[str]):
        """
        Orchestrates the producer-consumer matrix.
        """
        # Start the writer task
        writer_task = asyncio.create_task(self.writer_worker())
        
        # Start consumer tasks
        consumers = [
            asyncio.create_task(self.consumer_worker())
            for _ in range(self.num_consumers)
        ]

        # Run producer logic
        await self.producer_worker(target_urls)

        # Wait for all payloads to be processed
        await self.payload_queue.join()
        
        # Wait for all results to be written
        await self.results_queue.join()

        # Shutdown consumers and writer
        for c in consumers:
            c.cancel()
        writer_task.cancel()
        
        # Final flush & close
        await self.storage_engine.close()
        logger.info("Pipeline execution complete.")
