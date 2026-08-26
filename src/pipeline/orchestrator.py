#!/usr/bin/env python3
"""
Pipeline Orchestrator — Coordinates producer, parser, and storage.
"""

import asyncio
import logging
from typing import List

from src.scraper.producer import RawIngestionService
from src.parser.streaming_parser import parse_html_stream
from src.storage.db import StorageEngine

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates the full extraction pipeline."""

    def __init__(self, db_path: str = "extraction.db"):
        self.db_path = db_path
        self.producer = RawIngestionService()

    async def run(self, urls: List[str]):
        """Run full pipeline on list of URLs."""
        async with StorageEngine(self.db_path) as storage:
            for url in urls:
                logger.info(f"Processing: {url}")

                html = await self.producer.fetch(url)
                if not html:
                    logger.warning(f"Skipping {url} — fetch failed")
                    continue

                items = list(parse_html_stream(url, html))

                for item in items:
                    await storage.ingest_item(item)

                logger.info(f"Stored {len(items)} items from {url}")

        await self.producer.close()
        logger.info("Pipeline complete")
