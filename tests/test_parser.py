"""Tests for HTML parser."""

import pytest
from extraction_engine.parser import (
    extract_metadata,
    extract_jsonld,
    extract_tables,
    extract_with_selector,
    extract_all,
    _parse_tree,
)


class TestParseTree:
    def test_valid_html(self):
        html = b"<html><head><title>Test</title></head><body></body></html>"
        tree = _parse_tree(html)
        assert tree is not None

    def test_invalid_html(self):
        html = b"not html at all"
        tree = _parse_tree(html)
        assert tree is None


class TestExtractMetadata:
    def test_title(self):
        html = b"<html><head><title>Hello World</title></head><body></body></html>"
        tree = _parse_tree(html)
        meta = extract_metadata(tree, "https://example.com")
        assert meta["title"] == "Hello World"
        assert meta["url"] == "https://example.com"

    def test_description(self):
        html = b'<html><head><meta name="description" content="A test page"></head><body></body></html>'
        tree = _parse_tree(html)
        meta = extract_metadata(tree, "https://example.com")
        assert meta["description"] == "A test page"

    def test_og_description(self):
        html = b'<html><head><meta property="og:description" content="OG desc"></head><body></body></html>'
        tree = _parse_tree(html)
        meta = extract_metadata(tree, "https://example.com")
        assert meta["description"] == "OG desc"

    def test_canonical(self):
        html = b'<html><head><link rel="canonical" href="https://example.com/page"></head><body></body></html>'
        tree = _parse_tree(html)
        meta = extract_metadata(tree, "https://example.com")
        assert meta["canonical"] == "https://example.com/page"

    def test_lang(self):
        html = b'<html lang="en"><head></head><body></body></html>'
        tree = _parse_tree(html)
        meta = extract_metadata(tree, "https://example.com")
        assert meta["lang"] == "en"


class TestExtractJsonLD:
    def test_single_jsonld(self):
        html = b'<html><head><script type="application/ld+json">{"@type": "Product", "name": "Widget"}</script></head><body></body></html>'
        tree = _parse_tree(html)
        data = extract_jsonld(tree)
        assert len(data) == 1
        assert data[0]["@type"] == "Product"

    def test_multiple_jsonld(self):
        html = b'<html><head><script type="application/ld+json">[{"@type": "A"}, {"@type": "B"}]</script></head><body></body></html>'
        tree = _parse_tree(html)
        data = extract_jsonld(tree)
        assert len(data) == 2

    def test_invalid_jsonld(self):
        html = b'<html><head><script type="application/ld+json">not json</script></head><body></body></html>'
        tree = _parse_tree(html)
        data = extract_jsonld(tree)
        assert data == []


class TestExtractTables:
    def test_simple_table(self):
        html = b'<html><body><table><tr><th>Name</th><th>Value</th></tr><tr><td>A</td><td>1</td></tr></table></body></html>'
        tree = _parse_tree(html)
        tables = extract_tables(tree, "https://example.com")
        assert len(tables) == 1
        assert tables[0]["headers"] == ["Name", "Value"]
        assert tables[0]["rows"] == [{"Name": "A", "Value": "1"}]

    def test_no_tables(self):
        html = b"<html><body><p>No tables here</p></body></html>"
        tree = _parse_tree(html)
        tables = extract_tables(tree, "https://example.com")
        assert tables == []


class TestExtractWithSelector:
    def test_css_selector(self):
        html = b'<html><body><div class="item">First</div><div class="item">Second</div></body></html>'
        tree = _parse_tree(html)
        results = extract_with_selector(tree, "https://example.com", ".item")
        assert len(results) == 2
        assert results[0]["text"] == "First"
        assert results[1]["text"] == "Second"

    def test_no_match(self):
        html = b"<html><body><p>Hello</p></body></html>"
        tree = _parse_tree(html)
        results = extract_with_selector(tree, "https://example.com", ".nonexistent")
        assert results == []


class TestExtractAll:
    def test_full_extraction(self):
        html = b"""<html lang="en">
            <head>
                <title>Full Test</title>
                <meta name="description" content="A full test">
                <script type="application/ld+json">{"@type": "Article", "headline": "Test"}</script>
            </head>
            <body>
                <a href="/page1">Link 1</a>
                <a href="/page2">Link 2</a>
                <img src="/img1.jpg" alt="Image 1">
                <table><tr><th>Col</th></tr><tr><td>Val</td></tr></table>
            </body>
        </html>"""
        result = extract_all(html, "https://example.com")
        assert result["title"] == "Full Test"
        assert result["description"] == "A full test"
        assert result["lang"] == "en"
        assert result["jsonld_count"] == 1
        assert result["table_count"] == 1
        assert result["link_count"] == 2
        assert result["image_count"] == 1
        assert "scraped_at" in result

    def test_bad_html(self):
        result = extract_all(b"not html", "https://example.com")
        assert "error" in result
