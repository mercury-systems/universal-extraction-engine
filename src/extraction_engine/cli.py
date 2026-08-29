"""Command-line interface."""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from .batch import BatchExtractor
from .exporter import export_json, export_csv


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    fmt = "%(message)s"
    logging.basicConfig(level=level, format=fmt)


def print_banner():
    print("=" * 72)
    print("  MERCURY-OPS  |  Universal Extraction Engine  v2.0.0")
    print("=" * 72)
    print()


def print_result(result: dict, index: int = 0):
    url = result.get("url", "unknown")
    if "error" in result:
        print(f"  [{index + 1}] ❌ {url}")
        print(f"      Error: {result['error']}")
    else:
        print(f"  [{index + 1}] ✅ {url}")
        print(f"      Title: {result.get('title', 'N/A')}")
        print(f"      Tables: {result.get('table_count', 0)} | JSON-LD: {result.get('jsonld_count', 0)}")
        print(f"      Links: {result.get('link_count', 0)} | Images: {result.get('image_count', 0)}")
    print()


def print_summary(results: list):
    total = len(results)
    success = sum(1 for r in results if "error" not in r)
    failed = total - success
    total_tables = sum(r.get("table_count", 0) for r in results if "error" not in r)
    total_jsonld = sum(r.get("jsonld_count", 0) for r in results if "error" not in r)

    print("-" * 72)
    print("  EXTRACTION REPORT")
    print("-" * 72)
    print(f"  ✅ {success}/{total} pages extracted successfully")
    if failed:
        print(f"  ❌ {failed} failures")
    print(f"  📊 {total_tables} tables found")
    print(f"  🏷️  {total_jsonld} JSON-LD objects found")
    print("-" * 72)
    print()


async def run_single(args):
    extractor = BatchExtractor(concurrency=1)
    try:
        print(f"  → Target: {args.url}")
        if args.selector:
            print(f"  → CSS selector: {args.selector}")
        print()

        results = await extractor.extract([args.url], selector=args.selector)
        for result in results:
            print_result(result)

        if args.output:
            export_json(results[0], args.output)
            print(f"  💾 Saved to {args.output}")

    finally:
        await extractor.close()


async def run_batch(args):
    urls = []
    if args.url_file:
        with open(args.url_file) as f:
            urls = [line.strip() for line in f if line.strip()]
    elif args.urls:
        urls = args.urls
    else:
        print("❌ No URLs provided. Use --url or --url-file.")
        sys.exit(1)

    extractor = BatchExtractor(concurrency=args.concurrency)
    try:
        print(f"  → Batch: {len(urls)} URLs | Concurrency: {args.concurrency}")
        if args.selector:
            print(f"  → CSS selector: {args.selector}")
        print()

        results = await extractor.extract(urls, selector=args.selector)
        for i, result in enumerate(results):
            print_result(result, index=i)

        print_summary(results)

        if args.output:
            export_json(results, args.output)
            print(f"  💾 Saved to {args.output}")

        if args.csv:
            flat = []
            for r in results:
                if "error" not in r:
                    row = {
                        "url": r["url"],
                        "title": r.get("title", ""),
                        "description": r.get("description", ""),
                        "tables": r.get("table_count", 0),
                        "jsonld": r.get("jsonld_count", 0),
                        "links": r.get("link_count", 0),
                    }
                    flat.append(row)
            if flat:
                export_csv(flat, args.csv)
                print(f"  💾 CSV saved to {args.csv}")

    finally:
        await extractor.close()


def main():
    parser = argparse.ArgumentParser(
        description="Universal Extraction Engine — Extract structured data from HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s single https://quotes.toscrape.com/
  %(prog)s single https://example.com --selector ".product-title" --output result.json
  %(prog)s batch --urls https://a.com https://b.com --concurrency 5
  %(prog)s batch --url-file urls.txt --output results.json --csv results.csv
        """
    )
    parser.add_argument("--verbose", "-v", action="store_true")

    subparsers = parser.add_subparsers(dest="command", required=True)

    single = subparsers.add_parser("single", help="Extract from a single URL")
    single.add_argument("url", help="Target URL")
    single.add_argument("--selector", help="CSS selector for targeted extraction")
    single.add_argument("--output", "-o", help="Save result to JSON file")

    batch = subparsers.add_parser("batch", help="Extract from multiple URLs")
    batch.add_argument("--urls", nargs="+", help="Space-separated URLs")
    batch.add_argument("--url-file", help="File with one URL per line")
    batch.add_argument("--selector", help="CSS selector for targeted extraction")
    batch.add_argument("--concurrency", type=int, default=5)
    batch.add_argument("--output", "-o", help="Save results to JSON file")
    batch.add_argument("--csv", help="Also export to CSV file")

    args = parser.parse_args()
    setup_logging(args.verbose)
    print_banner()

    if args.command == "single":
        asyncio.run(run_single(args))
    elif args.command == "batch":
        asyncio.run(run_batch(args))


if __name__ == "__main__":
    main()
