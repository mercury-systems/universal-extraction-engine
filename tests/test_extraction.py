#!/usr/bin/env python3
"""Basic tests for Universal Extraction Engine."""

import sys
import asyncio
import tempfile
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scraper.producer import RawIngestionService
from parser.streaming_parser import parse_html_stream, UniversalWebItem
from storage.db import StorageEngine


def test_url_validation():
    """Test that the producer validates URLs correctly."""
    service = RawIngestionService()

    assert service._validate_url("https://example.com") == True
    assert service._validate_url("http://localhost:8080") == True
    assert service._validate_url("ftp://example.com") == False
    assert service._validate_url("file:///etc/passwd") == False
    assert service._validate_url("not-a-url") == False

    print("✅ URL validation tests passed")


def test_parser_structure():
    """Test that the parser produces valid items."""
    html = b"""<html><head><title>Test Page</title>
    <meta name="description" content="Test description">
    <script type="application/ld+json">{"@type": "Product", "name": "Test"}</script>
    </head><body></body></html>"""

    items = list(parse_html_stream("https://example.com", html))
    assert len(items) == 1

    item = items[0]
    assert item.url == "https://example.com"
    assert item.title == "Test Page"
    assert item.meta_description == "Test description"
    assert "Product" in item.json_ld_data

    print("✅ Parser structure tests passed")


def test_item_sku():
    """Test that SKU defaults to URL."""
    item = UniversalWebItem(
        url="https://example.com/product/123",
        scraped_at="2024-01-01T00:00:00+00:00"
    )
    assert item.sku == "https://example.com/product/123"

    print("✅ Item SKU tests passed")


async def test_storage_engine():
    """Test storage engine initialization and upserts."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    try:
        engine = StorageEngine(db_path=db_path, batch_size=2)
        await engine.initialize()

        item = UniversalWebItem(
            url="https://example.com",
            title="Test",
            meta_description="Desc",
            json_ld_data="{}",
            scraped_at="2024-01-01T00:00:00+00:00"
        )

        await engine.ingest_item(item)
        assert len(engine._buffer) == 1

        await engine.ingest_item(item)
        assert len(engine._buffer) == 0

        await engine.close()
        print("✅ Storage engine tests passed")
    finally:
        os.unlink(db_path)


def main():
    test_url_validation()
    test_parser_structure()
    test_item_sku()
    asyncio.run(test_storage_engine())
    print("\n🎉 All tests passed!")


if __name__ == "__main__":
    main()
