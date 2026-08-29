#!/usr/bin/env python3
"""Live demo against real targets."""

import asyncio
import json

from .batch import BatchExtractor
from .exporter import export_json


async def main():
    print("=" * 72)
    print("  MERCURY-OPS  |  Universal Extraction Engine  |  Live Demo")
    print("=" * 72)
    print()

    extractor = BatchExtractor(concurrency=3)

    try:
        targets = [
            ("https://quotes.toscrape.com/", "Scraper-friendly — quotes site"),
            ("https://httpbin.org/html", "Simple HTML — baseline test"),
            ("https://docs.python.org/3/", "Python docs — structured content"),
        ]

        urls = [url for url, _ in targets]
        results = await extractor.extract(urls)

        for i, (url, desc) in enumerate(targets):
            result = results[i]
            print(f"  [{i + 1}/3] {desc}")
            print(f"        URL: {url}")
            print("-" * 50)

            if "error" in result:
                print(f"        ❌ {result['error']}")
            else:
                print(f"        ✅ Title: {result.get('title', 'N/A')}")
                print(f"        📊 Tables: {result.get('table_count', 0)}")
                print(f"        🏷️  JSON-LD: {result.get('jsonld_count', 0)}")
                print(f"        🔗 Links: {result.get('link_count', 0)}")
                print(f"        🖼️  Images: {result.get('image_count', 0)}")
                if result.get("jsonld"):
                    types = [item.get("@type", "Unknown") for item in result["jsonld"]]
                    print(f"        📋 JSON-LD types: {', '.join(types)}")
            print()

        # Summary
        success = sum(1 for r in results if "error" not in r)
        total_tables = sum(r.get("table_count", 0) for r in results if "error" not in r)
        total_jsonld = sum(r.get("jsonld_count", 0) for r in results if "error" not in r)

        print("=" * 72)
        print("  EXTRACTION REPORT")
        print("=" * 72)
        print(f"  ✅ {success}/{len(results)} pages extracted")
        print(f"  📊 {total_tables} tables found")
        print(f"  🏷️  {total_jsonld} JSON-LD objects found")
        print()
        print("  Try CSS selectors: extract single <url> --selector '.quote'")
        print("=" * 72)

    finally:
        await extractor.close()


if __name__ == "__main__":
    asyncio.run(main())
