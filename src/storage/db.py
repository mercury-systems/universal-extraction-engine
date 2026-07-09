import asyncio
import aiosqlite
import logging
from typing import List
from src.parser.streaming_parser import UniversalWebItem

logger = logging.getLogger(__name__)

class StorageEngine:
    """
    Handles SQLite WAL-mode storage for Universal Web Items.
    Expects to be run as a dedicated writer task to avoid concurrent write locks.
    """
    def __init__(self, db_path: str = "universal_inventory.db", batch_size: int = 100):
        self.db_path = db_path
        self.batch_size = batch_size
        self._buffer: List[UniversalWebItem] = []
        self._conn: aiosqlite.Connection = None

    async def initialize(self):
        self._conn = await aiosqlite.connect(self.db_path)
        # Enable WAL mode for high concurrency
        await self._conn.execute("PRAGMA journal_mode=WAL;")
        await self._conn.execute("PRAGMA synchronous=NORMAL;")
        
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS web_data (
                url TEXT PRIMARY KEY,
                title TEXT,
                meta_description TEXT,
                json_ld_data TEXT,
                scraped_at TEXT NOT NULL
            )
        ''')
        await self._conn.commit()
        logger.info(f"Storage engine initialized with WAL mode at {self.db_path}")

    async def close(self):
        if self._buffer:
            await self.flush()
        if self._conn:
            await self._conn.close()

    async def ingest_item(self, item: UniversalWebItem):
        """
        Adds an item to the buffer and flushes if the batch size is reached.
        Must be called from the dedicated writer task.
        """
        self._buffer.append(item)
        if len(self._buffer) >= self.batch_size:
            await self.flush()

    async def flush(self):
        """
        Flushes the current buffer to SQLite.
        """
        if not self._buffer:
            return

        items = [(
            p.url, p.title, p.meta_description, p.json_ld_data, p.scraped_at
        ) for p in self._buffer]

        try:
            await self._conn.executemany('''
                INSERT INTO web_data (url, title, meta_description, json_ld_data, scraped_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title=excluded.title,
                    meta_description=excluded.meta_description,
                    json_ld_data=excluded.json_ld_data,
                    scraped_at=excluded.scraped_at
            ''', items)
            await self._conn.commit()
            logger.debug(f"Flushed {len(items)} items to database.")
        except Exception as e:
            logger.error(f"Failed to flush batch to database: {e}")
        finally:
            self._buffer.clear()
