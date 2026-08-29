# Universal Extraction Engine

Extract structured data from HTML: metadata, JSON-LD, tables, links, images, and CSS selectors.

## What It Does

- **Metadata**: Title, description, canonical URL, language
- **JSON-LD**: Structured data (Product, Article, Organization, etc.)
- **Tables**: HTML tables converted to JSON arrays with headers
- **Links & Images**: All unique URLs, resolved relative to base
- **CSS Selectors**: Target specific elements with any selector
- **Batch mode**: Process multiple URLs concurrently
- **Export**: JSON or CSV output

## Installation

```bash
git clone https://github.com/mercury-systems/universal-extraction-engine.git
cd universal-extraction-engine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

For running tests:

```bash
pip install -r requirements-dev.txt
```

> **Note:** Always activate the virtual environment (`source .venv/bin/activate`) before working with this project.

## Quick Start

    # Single URL
    extract single https://quotes.toscrape.com/

    # With CSS selector
    extract single https://quotes.toscrape.com/ --selector ".quote" --output result.json

    # Batch
    extract batch --urls https://a.com https://b.com --concurrency 5 --output results.json

    # From file
    extract batch --url-file urls.txt --output results.json --csv results.csv

## Demo

    make demo

## Docker

    docker compose run --rm extract single https://example.com

## Test

    make test        # Unit tests only
    make test-all    # All tests including integration

## License

MIT
