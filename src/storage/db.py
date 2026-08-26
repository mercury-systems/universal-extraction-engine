#!/usr/bin/env python3
"""
Storage Engine — SQLite backend with async support.
"""

import logging
from typing import List, Optional

import aiosqlite

from src.parser.streaming_parser import UniversalWebItem

logger = logging.getLogger(__name__)


class StorageEngine:
    """Async SQLite storage for extracted items."""

    def __init__(self, db_path: str = "extraction.db", batch_size: int = 100):
        self.db_path = db_path
        self.batch_size = batch_size
        self._db: Optional[aiosqlite.Connection] = None
        self._buffer: List[UniversalWebItem] = []

    async def initialize(self):
        """Initialize database and tables."""
        self._db = await aiosqlite.connect(self.db_path)
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS extracted_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                meta_description TEXT,
                json_ld_data TEXT,
                links TEXT,
                images TEXT,
                sku TEXT,
                scraped_at TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await self._db.commit()
        logger.info(f"Storage initialized: {self.db_path}")

    async def ingest_item(self, item: UniversalWebItem):
        """Add item to buffer, flush if batch size reached."""
        self._buffer.append(item)
        if len(self._buffer) >= self.batch_size:
            await self._flush()

    async def _flush(self):
        """Write buffered items to database."""
        if not self._buffer or not self._db:
            return

        import json

        rows = [
            (
                item.url,
                item.title,
                item.meta_description,
                item.json_ld_data,
                json.dumps(item.links),
                json.dumps(item.images),
                item.sku,
                item.scraped_at,
            )
            for item in self._buffer
        ]

        await self._db.executemany("""
            INSERT INTO extracted_items
            (url, title, meta_description, json_ld_data, links, images, sku, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        await self._db.commit()

        logger.info(f"Flushed {len(self._buffer)} items to database")
        self._buffer.clear()

    async def close(self):
        """Flush remaining items and close database."""
        await self._flush()
        if self._db:
            await self._db.close()
            logger.info("Storage closed")

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
