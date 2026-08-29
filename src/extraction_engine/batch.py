"""Batch extraction with concurrency."""

import asyncio
import logging
from typing import List, Dict, Any

from .fetcher import Fetcher
from .parser import extract_all

logger = logging.getLogger(__name__)


class BatchExtractor:
    def __init__(self, concurrency: int = 5, timeout: float = 30.0):
        self.concurrency = concurrency
        self.fetcher = Fetcher(timeout=timeout, max_connections=concurrency * 2)

    async def extract(self, urls: List[str], selector: str = None) -> List[Dict[str, Any]]:
        """Extract data from multiple URLs concurrently. Preserves URL order."""
        results_list = await self.fetcher.fetch_batch(urls, concurrency=self.concurrency)
        results = []

        for url, html in results_list:
            if html is None:
                results.append({"url": url, "error": "Fetch failed"})
                continue
            try:
                data = extract_all(html, url, selector=selector)
                results.append(data)
            except Exception as e:
                logger.error(f"Extraction failed for {url}: {e}")
                results.append({"url": url, "error": str(e)})

        return results

    async def close(self):
        await self.fetcher.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
