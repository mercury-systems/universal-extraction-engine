#!/usr/bin/env python3
"""
Streaming HTML Parser — Extracts structured data from raw HTML.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Iterator, List, Optional
from urllib.parse import urljoin

from lxml import html as lh

logger = logging.getLogger(__name__)


@dataclass
class UniversalWebItem:
    """Standardized extraction item."""
    url: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    json_ld_data: Optional[str] = None
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    sku: Optional[str] = None
    scraped_at: Optional[str] = None

    def __post_init__(self):
        if self.sku is None:
            self.sku = self.url


def parse_html_stream(url: str, html_bytes: bytes) -> Iterator[UniversalWebItem]:
    """Parse HTML and yield extracted items."""
    try:
        tree = lh.fromstring(html_bytes)
    except Exception as e:
        logger.error(f"Failed to parse HTML from {url}: {e}")
        return

    title = None
    title_elem = tree.find(".//title")
    if title_elem is not None:
        title = title_elem.text_content().strip()

    meta_desc = None
    for meta in tree.iter("meta"):
        if meta.get("name") == "description":
            meta_desc = meta.get("content")
            break

    json_ld = None
    for script in tree.iter("script"):
        if script.get("type") == "application/ld+json":
            try:
                data = json.loads(script.text_content())
                json_ld = json.dumps(data)
            except (json.JSONDecodeError, AttributeError):
                pass
            break

    links = []
    for a in tree.iter("a"):
        href = a.get("href")
        if href:
            links.append(urljoin(url, href))

    images = []
    for img in tree.iter("img"):
        src = img.get("src")
        if src:
            images.append(urljoin(url, src))

    from datetime import datetime, timezone
    scraped_at = datetime.now(timezone.utc).isoformat()

    yield UniversalWebItem(
        url=url,
        title=title,
        meta_description=meta_desc,
        json_ld_data=json_ld,
        links=links[:50],
        images=images[:50],
        scraped_at=scraped_at,
    )
