"""HTML parsing and structured data extraction."""

import json
import logging
from typing import Iterator, List, Optional, Dict, Any
from urllib.parse import urljoin
from datetime import datetime, timezone

from lxml import html as lh

logger = logging.getLogger(__name__)


def _parse_tree(html_bytes: bytes) -> Optional[lh.HtmlElement]:
    text = html_bytes.decode("utf-8", errors="replace").strip()
    if not text or "<" not in text:
        return None
    try:
        return lh.fromstring(html_bytes)
    except Exception as e:
        logger.error(f"Failed to parse HTML: {e}")
        return None


def extract_metadata(tree: lh.HtmlElement, base_url: str) -> Dict[str, Any]:
    """Extract page metadata: title, description, canonical, lang."""
    result = {"url": base_url}

    title_elem = tree.find(".//title")
    result["title"] = title_elem.text_content().strip() if title_elem is not None else None

    meta_desc = None
    for meta in tree.iter("meta"):
        name = meta.get("name", "").lower()
        prop = meta.get("property", "").lower()
        if name == "description" or prop == "og:description":
            meta_desc = meta.get("content")
            if meta_desc:
                break
    result["description"] = meta_desc

    canonical = tree.find(".//link[@rel='canonical']")
    result["canonical"] = canonical.get("href") if canonical is not None else None

    result["lang"] = tree.get("lang") if tree.tag == "html" else None

    result["scraped_at"] = datetime.now(timezone.utc).isoformat()
    return result


def extract_jsonld(tree: lh.HtmlElement) -> List[Dict[str, Any]]:
    """Extract all JSON-LD structured data (Product, Article, Organization, etc)."""
    results = []
    for script in tree.iter("script"):
        if script.get("type") == "application/ld+json":
            try:
                text = script.text_content().strip()
                if text:
                    data = json.loads(text)
                    if isinstance(data, list):
                        results.extend(data)
                    else:
                        results.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
    return results


def extract_tables(tree: lh.HtmlElement, base_url: str) -> List[Dict[str, Any]]:
    """Extract HTML tables as structured JSON arrays."""
    tables = []
    for i, table in enumerate(tree.iter("table")):
        headers = []
        rows = []

        for th in table.iter("th"):
            text = th.text_content().strip()
            if text:
                headers.append(text)

        for tr in table.iter("tr"):
            cells = []
            for td in tr.iter("td"):
                text = td.text_content().strip()
                cells.append(text)
            if cells:
                if headers and len(cells) == len(headers):
                    rows.append(dict(zip(headers, cells)))
                else:
                    rows.append(cells)

        if rows:
            tables.append({"table_index": i, "headers": headers, "rows": rows})
    return tables


def extract_with_selector(tree: lh.HtmlElement, base_url: str, selector: str) -> List[Dict[str, str]]:
    """Extract elements matching a CSS selector."""
    results = []
    for elem in tree.cssselect(selector):
        item = {
            "text": elem.text_content().strip(),
            "html": lh.tostring(elem, encoding="unicode", method="html"),
        }
        for attr in ("href", "src", "alt", "title", "class", "id"):
            val = elem.get(attr)
            if val:
                if attr in ("href", "src"):
                    item[attr] = urljoin(base_url, val)
                else:
                    item[attr] = val
        results.append(item)
    return results


def extract_links(tree: lh.HtmlElement, base_url: str) -> List[str]:
    """Extract all unique links."""
    links = set()
    for a in tree.iter("a"):
        href = a.get("href")
        if href:
            links.add(urljoin(base_url, href))
    return sorted(links)


def extract_images(tree: lh.HtmlElement, base_url: str) -> List[str]:
    """Extract all image sources."""
    images = set()
    for img in tree.iter("img"):
        src = img.get("src")
        if src:
            images.add(urljoin(base_url, src))
    return sorted(images)


def extract_all(html_bytes: bytes, base_url: str, selector: Optional[str] = None) -> Dict[str, Any]:
    """Run all extraction methods and return combined result."""
    tree = _parse_tree(html_bytes)
    if tree is None:
        return {"url": base_url, "error": "Failed to parse HTML"}

    result = extract_metadata(tree, base_url)
    result["jsonld"] = extract_jsonld(tree)
    result["tables"] = extract_tables(tree, base_url)
    result["links"] = extract_links(tree, base_url)[:100]
    result["images"] = extract_images(tree, base_url)[:100]
    result["link_count"] = len(result["links"])
    result["image_count"] = len(result["images"])
    result["table_count"] = len(result["tables"])
    result["jsonld_count"] = len(result["jsonld"])

    if selector:
        result["selector_results"] = extract_with_selector(tree, base_url, selector)
        result["selector_match_count"] = len(result["selector_results"])

    return result
