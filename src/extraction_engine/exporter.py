"""Export extracted data to JSON and CSV."""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def export_json(data: Dict[str, Any], path: str) -> str:
    """Export data to JSON file. Returns the file path."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    logger.info(f"Exported JSON to {output}")
    return str(output)


def export_csv(data: List[Dict[str, Any]], path: str, fields: List[str] = None) -> str:
    """Export list of dicts to CSV. Returns the file path."""
    if not data:
        logger.warning("No data to export to CSV")
        return ""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    if fields is None:
        fields = list(data[0].keys())

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)

    logger.info(f"Exported CSV to {output}")
    return str(output)
