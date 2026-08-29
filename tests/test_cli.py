"""Tests for CLI."""

import sys
from unittest.mock import patch
from extraction_engine.cli import main


class TestCLI:
    def test_single_command(self):
        with patch.object(sys, "argv", ["extract", "single", "https://example.com"]):
            with patch("extraction_engine.cli.asyncio.run") as mock_run:
                try:
                    main()
                except SystemExit:
                    pass
                assert mock_run.called

    def test_batch_command(self):
        with patch.object(sys, "argv", ["extract", "batch", "--urls", "https://a.com", "https://b.com"]):
            with patch("extraction_engine.cli.asyncio.run") as mock_run:
                try:
                    main()
                except SystemExit:
                    pass
                assert mock_run.called
