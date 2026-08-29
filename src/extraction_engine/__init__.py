"""Universal Extraction Engine v2.0.0"""

from .fetcher import Fetcher
from .parser import (
    extract_metadata,
    extract_jsonld,
    extract_tables,
    extract_with_selector,
    extract_all,
)
from .exporter import export_json, export_csv
from .batch import BatchExtractor

__version__ = "2.0.0"
