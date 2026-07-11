# Universal Extraction Engine Architecture

## Overview
This engine is designed to handle high-throughput HTML processing and data extraction safely and asynchronously. It bypasses traditional, brittle HTML DOM parsing by strictly targeting Universal Metadata and embedded JSON-LD footprints.

## Core Components

### 1. The Asynchronous Decoupling Matrix
The system uses an `asyncio.Queue` pipeline to completely isolate network I/O from CPU-bound parsing.
- **Engine A (Producers):** Responsible solely for hitting target URLs and fetching the raw HTML bytes.
- **Engine B (Consumers):** Intercepts payloads and runs the flat-memory parser logic.

### 2. Streaming Tokenizer & The "Zero Memory Leak" Fix
To parse enormous HTML payloads without inflating RAM:
- The system uses `lxml.etree.HTMLPullParser`.
- As nodes are processed, they are instantly cleared and unlinked from their parents:
  ```python
  element.clear()
  while element.getprevious() is not None:
      del element.getparent()[0]
  ```
- This keeps the heap profile entirely flat, preventing `libxml2` memory leaks common in massive scraping jobs.

### 3. Universal "No-Code" Extraction
Instead of parsing site-specific HTML paths (`<div class="price">`), the engine universally maps:
- `<title>` nodes.
- `<meta>` nodes (capturing SEO descriptions and `og:description`).
- `<script type="application/ld+json">` payloads (structured JSON embedded by modern websites).

### 4. Streaming Storage Engine (SQLite WAL)
To persist high-concurrency data without write-lockouts:
- The backend relies on `aiosqlite` configured with `PRAGMA journal_mode=WAL;`.
- A single, dedicated async writer task consumes the extracted payloads and flushes them to disk in batches using `.executemany()`.
