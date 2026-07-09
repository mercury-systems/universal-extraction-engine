# Universal Extraction Engine Usage Guide

## Prerequisites
Ensure you have Python 3.8+ installed. The environment relies on modern asynchronous libraries.

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Engine

The CLI entrypoint is located at `src/main.py`. The engine dynamically scales based on the input URLs provided.

### Single Target Extraction
To run the miner against a single URL:
```bash
python src/main.py https://example.com
```

### Multi-Target Extraction
To run the miner concurrently against multiple URLs:
```bash
python src/main.py https://example.com https://contra.com https://github.com
```

### Bulk Batch Processing
For massive scraping tasks, feed a `.txt` file containing your target URLs (one per line):
```bash
python src/main.py --file urls.txt
```

## Cross-Platform Compatibility
The system is built to run natively on both Linux and Windows. The entrypoint automatically detects Windows (`win32`) environments and sets the `WindowsSelectorEventLoopPolicy` to prevent `asyncio` from throwing "Event loop is closed" errors during teardown.
