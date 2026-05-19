#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import tempfile
from pathlib import Path
import sys


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from core import BM25
from design_system import persist_design_system


class SecurityHardeningTests(unittest.TestCase):
    def test_bm25_tokenize_truncates_long_input(self):
        bm25 = BM25()
        text = ("alpha " * 100) + "sentinel"
        tokens = bm25.tokenize(text)
        self.assertNotIn("sentinel", tokens)

    def test_persist_design_system_sanitizes_project_and_page_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = persist_design_system(
                {"project_name": "My Project/2026"},
                page="Checkout\\Main",
                output_dir=tmpdir,
                page_query="Checkout flow",
            )
            created_files = {Path(path) for path in result["created_files"]}
            expected_master = Path(tmpdir) / "design-system" / "my-project-2026" / "MASTER.md"
            expected_page = Path(tmpdir) / "design-system" / "my-project-2026" / "pages" / "checkout-main.md"
            self.assertIn(expected_master, created_files)
            self.assertIn(expected_page, created_files)

    def test_persist_design_system_raises_on_traversal_attempt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(PermissionError):
                persist_design_system(
                    {"project_name": "%2e%2e/evil"},
                    output_dir=tmpdir,
                )

    def test_persist_design_system_blocks_windows_reserved_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = persist_design_system(
                {"project_name": "CON.txt"},
                output_dir=tmpdir,
            )
            created_files = {Path(path) for path in result["created_files"]}
            expected_master = Path(tmpdir) / "design-system" / "default" / "MASTER.md"
            self.assertIn(expected_master, created_files)


if __name__ == "__main__":
    unittest.main()
