# Benchmarks

All tests run on Ubuntu 22.04, Python 3.12, 4 vCPU, 8GB RAM.

## Single URL Extraction

| Target | Time | Bytes | Items |
|--------|------|-------|-------|
| example.com | ~150ms | ~1,200 | 1 |
| wikipedia.org | ~300ms | ~45,000 | 1 |
| news.ycombinator.com | ~250ms | ~42,000 | 1 |

## Batch Processing

| URLs | Total Time | Avg per URL |
|------|-----------|-------------|
| 10 | ~3s | ~300ms |
| 100 | ~25s | ~250ms |
| 1,000 | ~4min | ~240ms |

## Resource Usage

| Metric | Value |
|--------|-------|
| Memory (single fetch) | ~15MB |
| Memory (batch 100) | ~45MB |
| SQLite write speed | ~5,000 items/sec |
| lxml parse speed | ~2ms per KB |
