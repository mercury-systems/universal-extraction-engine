#!/usr/bin/env python3
"""
Raw Ingestion Service — Fetches HTML from targets.
"""

import asyncio
import logging
from typing import Optional
from urllib.parse import urlparse

import aiohttp
import httpx

logger = logging.getLogger(__name__)


class RawIngestionService:
    """Fetches raw HTML from URLs using aiohttp or httpx."""

    def __init__(self, timeout: float = 30.0, user_agent: str = None):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={"User-Agent": self.user_agent}
            )
        return self._session

    def _validate_url(self, url: str) -> bool:
        """Validate URL scheme and structure."""
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)

    async def fetch(self, url: str) -> Optional[bytes]:
        """Fetch HTML content from URL."""
        if not self._validate_url(url):
            logger.error(f"Invalid URL: {url}")
            return None

        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    logger.info(f"Fetched {len(content)} bytes from {url}")
                    return content
                else:
                    logger.warning(f"HTTP {response.status} from {url}")
                    return None
        except Exception as e:
            logger.error(f"Fetch failed for {url}: {e}")
            return None

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
