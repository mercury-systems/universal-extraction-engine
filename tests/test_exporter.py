"""Tests for exporter."""

import json
import csv
import tempfile
import os
from extraction_engine.exporter import export_json, export_csv


class TestExporter:
    def test_export_json(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = export_json({"key": "value"}, f.name)
            assert os.path.exists(path)
            with open(path) as fp:
                data = json.load(fp)
            assert data["key"] == "value"
            os.unlink(path)

    def test_export_csv(self):
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = export_csv(data, f.name)
            assert os.path.exists(path)
            with open(path, newline="") as fp:
                reader = csv.DictReader(fp)
                rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["name"] == "Alice"
            os.unlink(path)

    def test_export_csv_empty(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = export_csv([], f.name)
            assert path == ""
            os.unlink(f.name)
