#!/usr/bin/env python3
"""
Universal Extraction Engine — Interactive CLI
Author: MERCURY-OPS
"""

import os
import sys
import asyncio
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline.orchestrator import PipelineOrchestrator
from src.scraper.producer import RawIngestionService
from src.parser.streaming_parser import parse_html_stream
from src.storage.db import StorageEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     🌐 UNIVERSAL EXTRACTION ENGINE v1.0.0                    ║
║     Author: MERCURY-OPS                                      ║
╚══════════════════════════════════════════════════════════════╝
""")


def print_menu():
    print("""
[1] Scrape single URL
[2] Scrape multiple URLs (from file)
[3] View stored data
[4] Export to JSON
[5] Run full pipeline
[0] Exit
""")


async def scrape_single():
    url = input("Enter URL: ").strip()
    if not url.startswith(("http://", "https://")):
        print("❌ Invalid URL. Must start with http:// or https://")
        return

    service = RawIngestionService()
    html = await service.fetch(url)
    if not html:
        print("❌ Failed to fetch URL")
        return

    items = list(parse_html_stream(url, html))
    print(f"✅ Extracted {len(items)} items")
    for item in items:
        print(f"  → {item.title or 'No title'} | {item.url}")


async def scrape_from_file():
    filepath = input("Enter file path (one URL per line): ").strip()
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    with open(filepath, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"📄 Loaded {len(urls)} URLs")
    service = RawIngestionService()

    for url in urls:
        print(f"\n🔍 Fetching: {url}")
        html = await service.fetch(url)
        if html:
            items = list(parse_html_stream(url, html))
            print(f"  ✅ {len(items)} items extracted")
        else:
            print(f"  ❌ Failed")


async def view_data():
    db_path = input("Database path [default: extraction.db]: ").strip() or "extraction.db"
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return

    engine = StorageEngine(db_path=db_path)
    await engine.initialize()
    import aiosqlite
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT COUNT(*) FROM extracted_items") as cursor:
            count = (await cursor.fetchone())[0]
            print(f"📊 Total extracted items: {count}")
    await engine.close()


async def export_json():
    db_path = input("Database path [default: extraction.db]: ").strip() or "extraction.db"
    output_path = input("Output JSON path [default: export.json]: ").strip() or "export.json"

    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return

    import aiosqlite
    import json

    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM extracted_items") as cursor:
            rows = await cursor.fetchall()
            data = [dict(row) for row in rows]

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

    print(f"✅ Exported {len(data)} items to {output_path}")


async def run_pipeline():
    urls_input = input("Enter URLs (comma-separated) or file path: ").strip()

    if os.path.exists(urls_input):
        with open(urls_input, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        urls = [u.strip() for u in urls_input.split(",") if u.strip()]

    if not urls:
        print("❌ No URLs provided")
        return

    orchestrator = PipelineOrchestrator()
    await orchestrator.run(urls)
    print("✅ Pipeline complete")


async def main():
    print_banner()

    while True:
        print_menu()
        choice = input("Choice: ").strip()

        if choice == "0":
            print("Goodbye.")
            break
        elif choice == "1":
            await scrape_single()
        elif choice == "2":
            await scrape_from_file()
        elif choice == "3":
            await view_data()
        elif choice == "4":
            await export_json()
        elif choice == "5":
            await run_pipeline()
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
