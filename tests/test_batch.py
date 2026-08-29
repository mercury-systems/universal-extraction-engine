"""Tests for batch extractor."""

import pytest
from extraction_engine.batch import BatchExtractor


@pytest.mark.asyncio
@pytest.mark.integration
async def test_batch_extract():
    extractor = BatchExtractor(concurrency=2)
    try:
        results = await extractor.extract([
            "https://httpbin.org/html",
            "https://httpbin.org/get",
        ])
        assert len(results) == 2
        assert any("error" not in r for r in results)
    finally:
        await extractor.close()
