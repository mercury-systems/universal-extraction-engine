# Universal Extraction Engine — Product Guide

## Section 1 — Overview

The **Universal Extraction Engine** is an async web extraction tool designed for known, scraper-friendly targets. It fetches HTML, extracts structured data (titles, meta descriptions, JSON-LD, links, images), and stores results in SQLite.

| | Universal Extraction Engine | Distributed Stealth Scraper |
|---|---|---|
| **Primary Use** | Known / scraper-friendly targets | Unknown / WAF-protected targets |
| **Engine** | Single: aiohttp + lxml | Dual: curl_cffi + Playwright |
| **WAF Bypass** | No — direct extraction | Yes — auto-escalation |
| **Speed** | ~150–300ms per request | ~200ms (light) / ~3–8s (heavy) |
| **Best For** | Structured data, batch jobs | Cloudflare, DataDome, PerimeterX |
| **When to Use** | Target known and friendly | Target unknown or protected |

**When to use this repo alone:** You have a list of known, scraper-friendly targets and need fast, structured extraction.

**When to pair with Distributed Stealth Scraper:** Your pipeline includes both friendly and protected targets. Use this engine for speed on friendly sites, and the Stealth Scraper for bypass on protected ones.

## Section 2 — Product Breakdown

### Architecture

```
┌─────────────────┐     ┌─────────────────────┐
│   Your Code     │────▶│ PipelineOrchestrator│
└─────────────────┘     └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
        ┌──────────┐       ┌──────────┐       ┌──────────┐
        │ Producer │──────▶│  Parser  │──────▶│ Storage  │
        │(aiohttp) │       │ (lxml)   │       │(SQLite)  │
        └──────────┘       └──────────┘       └──────────┘
```

### File Structure

```
universal-extraction-engine/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Interactive CLI
│   ├── scraper/
│   │   ├── __init__.py
│   │   └── producer.py            # aiohttp fetcher
│   ├── parser/
│   │   ├── __init__.py
│   │   └── streaming_parser.py    # lxml extractor
│   ├── storage/
│   │   ├── __init__.py
│   │   └── db.py                  # aiosqlite backend
│   └── pipeline/
│       ├── __init__.py
│       └── orchestrator.py        # Coordinator
├── tests/
│   └── test_extraction.py         # Unit + integration tests
├── requirements.txt               # Python deps
├── setup.py                       # Package setup
├── Dockerfile                     # Docker build
├── docker-compose.yml             # Docker compose
├── Makefile                       # Convenience commands
├── README.rst                     # Main documentation
├── CHANGELOG.md                   # Version history
├── BENCHMARK.md                   # Performance data
├── LICENSE                        # MIT license
├── .gitignore                     # Git exclusions
├── .gitattributes                 # Line endings
└── .github/workflows/ci.yml       # GitHub Actions CI
```

### Key Classes

| Class | Purpose |
|---|---|
| `PipelineOrchestrator` | Main entry point. Coordinates all stages. |
| `RawIngestionService` | aiohttp fetcher with connection pooling. |
| `parse_html_stream` | lxml parser. Yields `UniversalWebItem`. |
| `StorageEngine` | aiosqlite with batch inserts. |
| `UniversalWebItem` | Standardized dataclass for extracted data. |

## Section 3 — Setup Instructions

### Docker (Recommended)

```bash
git clone https://github.com/mercury-systems/universal-extraction-engine.git
cd universal-extraction-engine
make build
make run
```

### Local

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libxml2-dev libxslt1-dev zlib1g-dev

pip install -r requirements.txt
python3 src/main.py
```

## Section 4 — Integration Workflow

### Scenario A: Known Friendly Target

```python
from src.pipeline.orchestrator import PipelineOrchestrator

orchestrator = PipelineOrchestrator()
await orchestrator.run(["https://quotes.toscrape.com/"])
```

### Scenario B: Batch Processing

```python
# urls.txt — one URL per line
orchestrator = PipelineOrchestrator()
with open("urls.txt") as f:
    urls = [line.strip() for line in f]
await orchestrator.run(urls)
```

### Scenario C: Mixed Pipeline (with Distributed Stealth Scraper)

```python
# For known, friendly targets — fast extraction
from src.pipeline.orchestrator import PipelineOrchestrator

# For unknown or protected targets — stealth bypass
from stealth_engine import StealthScraper

# Route based on target profile
if target in known_friendly_list:
    result = await extraction_engine.scrape(target)
else:
    result = await stealth_scraper.fetch(target)
```

## Section 5 — Performance Comparison

| Metric | Extraction Engine | Stealth Light | Stealth Heavy |
|---|---|---|---|
| Startup | ~100ms | ~50ms | ~2–3s |
| Per Request | ~150–300ms | ~200–800ms | ~3–8s |
| Memory | ~15MB | ~20MB | ~150MB |
| WAF Bypass | No | No | Yes |
| JS Execution | No | No | Yes |
| Batch 100 URLs | ~25s | ~30s | ~6min |

## Section 6 — Common Issues & Fixes

| Issue | Cause | Fix |
|---|---|---|
| `lxml` build fails | Missing system deps | `sudo apt install libxml2-dev libxslt1-dev` |
| `docker-compose` not found | Using v1 syntax | Use `docker compose` (space, v2) |
| `ModuleNotFoundError: src` | Running outside repo root | `cd` to repo root, use `python3 src/main.py` |
| SQLite locked | Concurrent access | Use one StorageEngine instance per process |
| Empty extraction | JavaScript-rendered site | Use Stealth Scraper (Playwright) instead |

## Section 7 — Proxy Configuration

The producer does not include built-in proxy rotation. To add proxies:

```python
from src.scraper.producer import RawIngestionService

service = RawIngestionService(
    timeout=30.0,
    user_agent="Your Custom UA",
)
# Modify the aiohttp session after initialization
session = await service._get_session()
# Add proxy support via aiohttp connector
```

For full proxy rotation, use the Distributed Stealth Scraper which includes `ProxyPool` with automatic failure tracking.

## Section 8 — Testing

```bash
# Run all tests
make test

# Or manually:
python3 tests/test_extraction.py
```

Tests cover:
- URL validation (scheme, netloc)
- Parser structure (title, meta, JSON-LD)
- Item SKU defaults
- Storage engine (init, batch flush, close)

## Section 9 — License

MIT License — see [LICENSE](LICENSE).

Copyright (c) 2026 MERCURY-OPS

## Section 10 — Contact

- GitHub: https://github.com/mercury-systems
- Issues: https://github.com/mercury-systems/universal-extraction-engine/issues
