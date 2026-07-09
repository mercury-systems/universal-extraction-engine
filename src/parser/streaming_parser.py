import json
from typing import Iterator, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from lxml import etree

class UniversalWebItem(BaseModel):
    url: str
    title: str = ""
    meta_description: str = ""
    json_ld_data: str = ""
    scraped_at: str

def parse_html_stream(url: str, html_bytes: bytes) -> Iterator[UniversalWebItem]:
    """
    Parses HTML content using lxml's HTMLPullParser, maintaining a flat memory footprint.
    Extracts universal metadata and JSON-LD structured payloads.
    Yields a single UniversalWebItem per document.
    """
    parser = etree.HTMLPullParser(["end"])
    parser.feed(html_bytes)
    
    item = UniversalWebItem(
        url=url,
        scraped_at=datetime.now(timezone.utc).isoformat()
    )
    
    # We collect json_ld blocks since a page might have multiple.
    json_ld_blocks = []

    for action, element in parser.read_events():
        # Capture Title
        if element.tag == "title":
            if element.text:
                item.title = element.text.strip()
                
        # Capture Meta Description
        elif element.tag == "meta":
            name_attr = (element.get("name") or "").lower()
            property_attr = (element.get("property") or "").lower()
            if name_attr == "description" or property_attr == "og:description":
                content = element.get("content")
                if content:
                    item.meta_description = content.strip()
                    
        # Capture JSON-LD Structured Data
        elif element.tag == "script":
            if element.get("type") == "application/ld+json" and element.text:
                json_ld_blocks.append(element.text.strip())

        # CRITICAL MEMORY LEAK FIX:
        # Keep the live DOM slice footprint flat.
        element.clear()
        while element.getprevious() is not None:
            del element.getparent()[0]

    # Combine JSON-LD blocks if any exist
    if json_ld_blocks:
        try:
            # Re-serialize them as a single JSON array string to store neatly
            parsed_blocks = [json.loads(b) for b in json_ld_blocks]
            item.json_ld_data = json.dumps(parsed_blocks)
        except Exception:
            item.json_ld_data = "invalid_json_ld"

    yield item
