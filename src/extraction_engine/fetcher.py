"""Async HTML fetcher."""

import asyncio
import logging
from typing import Optional
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


class Fetcher:
    def __init__(self, timeout: float = 30.0, max_connections: int = 20):
        self.timeout = timeout
        self.limits = httpx.Limits(max_connections=max_connections)
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(timeout=self.timeout),
                limits=self.limits,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                },
            )
        return self._client

    def _validate_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)

    async def fetch(self, url: str) -> Optional[bytes]:
        if not self._validate_url(url):
            logger.error(f"Invalid URL: {url}")
            return None
        try:
            client = await self._get_client()
            response = await client.get(url)
            if response.status_code == 200:
                logger.info(f"Fetched {len(response.content)} bytes from {url}")
                return response.content
            logger.warning(f"HTTP {response.status_code} from {url}")
            return None
        except Exception as e:
            logger.error(f"Fetch failed for {url}: {e}")
            return None

    async def fetch_batch(self, urls: list, concurrency: int = 5) -> list:
        semaphore = asyncio.Semaphore(concurrency)

        async def _fetch_one(url):
            async with semaphore:
                return url, await self.fetch(url)

        tasks = [_fetch_one(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
