import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RawIngestionService:
    """
    Ingestion service tailored for raw HTML extraction.
    Mimics Project 1's IngestionService primitives but returns raw bytes
    to feed the lxml.etree.HTMLPullParser.
    """
    def __init__(self, transport: Optional[httpx.AsyncBaseTransport] = None):
        limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
        self.transport = transport
        self.limits = limits
        self.timeout = httpx.Timeout(10.0)

    async def fetch_html_bytes(self, url: str) -> Optional[bytes]:
        """
        Asynchronously fetches raw HTML bytes from the given URL.
        """
        async with httpx.AsyncClient(
            limits=self.limits,
            timeout=self.timeout,
            transport=self.transport,
            follow_redirects=True
        ) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTPStatusError for {url}: {e.response.status_code}")
                return None
            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)}")
                return None
