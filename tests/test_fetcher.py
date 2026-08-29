"""Tests for fetcher."""

import pytest
from extraction_engine.fetcher import Fetcher


class TestFetcher:
    def test_validate_url(self):
        f = Fetcher()
        assert f._validate_url("https://example.com") is True
        assert f._validate_url("http://localhost:8080") is True
        assert f._validate_url("ftp://example.com") is False
        assert f._validate_url("not-a-url") is False
        assert f._validate_url("") is False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_fetch_real():
    f = Fetcher()
    try:
        html = await f.fetch("https://httpbin.org/html")
        assert html is not None
        assert b"<html" in html.lower()
    finally:
        await f.close()


@pytest.mark.asyncio
async def test_fetch_invalid():
    f = Fetcher()
    try:
        result = await f.fetch("not-a-url")
        assert result is None
    finally:
        await f.close()
