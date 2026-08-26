Universal Extraction Engine
===========================

|Python| |Docker| |License|

.. |Python| image:: https://img.shields.io/badge/python-3.12%2B-blue
   :target: https://www.python.org/

.. |Docker| image:: https://img.shields.io/badge/docker-supported-blue
   :target: https://www.docker.com/

.. |License| image:: https://img.shields.io/badge/license-MIT-yellow
   :target: LICENSE

**Async web extraction engine for structured data scraping.**

The Universal Extraction Engine fetches, parses, and stores web data using an async pipeline. Built on aiohttp and lxml, it handles single URLs, batch files, and full pipelines with SQLite persistence.

Features
--------

- **⚡ Async Fetching** — aiohttp with connection pooling. ~150ms per request.
- **🧠 Streaming Parser** — lxml with low memory footprint. Extracts titles, meta, JSON-LD, links, images.
- **💾 SQLite Storage** — aiosqlite with batch inserts. ~5,000 items/sec.
- **📦 Batch Processing** — Process 10, 100, or 1,000 URLs from a file.
- **🐳 Docker Ready** — One command to build and run.
- **📤 JSON Export** — Export stored data to JSON for downstream use.

Architecture
------------

::

    Your Code → PipelineOrchestrator
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │Producer│  │ Parser │  │Storage │
    │(aiohttp)│  │(lxml)  │  │(SQLite)│
    └────────┘  └────────┘  └────────┘

Quick Start
-----------

Docker
~~~~~~

.. code-block:: bash

    git clone https://github.com/mercury-systems/universal-extraction-engine.git
    cd universal-extraction-engine
    docker compose up --build

Local
~~~~~

.. code-block:: bash

    # Install system dependencies (Ubuntu/Debian)
    sudo apt-get update
    sudo apt-get install -y libxml2-dev libxslt1-dev zlib1g-dev

    # Install Python dependencies
    pip install -r requirements.txt

    # Run interactive CLI
    python3 src/main.py

Usage
-----

Interactive CLI
~~~~~~~~~~~~~~~

.. code-block:: bash

    python3 src/main.py

::

    [1] Scrape single URL
    [2] Scrape multiple URLs (from file)
    [3] View stored data
    [4] Export to JSON
    [5] Run full pipeline
    [0] Exit

Programmatic API
~~~~~~~~~~~~~~~~

.. code-block:: python

    import asyncio
    from src.pipeline.orchestrator import PipelineOrchestrator

    async def main():
        orchestrator = PipelineOrchestrator()
        await orchestrator.run([
            "https://example.com",
            "https://example.org",
        ])

    asyncio.run(main())

Testing
-------

.. code-block:: bash

    make test

    # Or manually:
    python3 tests/test_extraction.py

Configuration
-------------

No configuration files needed. The engine uses sensible defaults:

- Database: ``extraction.db`` (SQLite)
- Timeout: 30 seconds per request
- Batch size: 100 items per SQLite flush
- User-Agent: Chrome 120 on Windows 10

Performance
-----------

See `BENCHMARK.md <BENCHMARK.md>`_ for detailed performance data.

License
-------

MIT — see `LICENSE <LICENSE>`_.
