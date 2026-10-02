from __future__ import annotations

import ast
from pathlib import Path
import unittest


APP_PATH = Path(__file__).with_name("app.py")


class AppPresentationBoundaryTests(unittest.TestCase):
    def test_temporary_play_ui_has_no_direct_gameplay_state_or_human_reads(self):
        """Keep the development UI behind the Gate13 presentation read seam.

        Controller command methods remain valid mutation/action boundaries.
        Presentation reads from controller.state/controller.human or
        self.gameplay.state/self.gameplay.human bypass the source-data bridge
        and are therefore rejected here.
        """
        source = APP_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(APP_PATH))
        direct_reads = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Attribute):
                continue
            if node.attr not in {"state", "human"}:
                continue
            base = ast.unparse(node.value)
            if base in {"controller", "self.gameplay"}:
                direct_reads.append(
                    f"{base}.{node.attr} at line {getattr(node, 'lineno', '?')}"
                )
        self.assertEqual(direct_reads, [])

    def test_temporary_ui_imports_and_uses_management_source_data_bridge(self):
        source = APP_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(APP_PATH))
        imported = False
        calls = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "gate13_management_source_data":
                imported = any(
                    alias.name == "ManagementSourceDataBridge"
                    for alias in node.names
                )
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "ManagementSourceDataBridge"
            ):
                calls += 1
        self.assertTrue(imported)
        self.assertGreaterEqual(calls, 3)


    def test_development_league_table_uses_source_presenter_and_original_columns(self):
        source = APP_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(APP_PATH))
        imported = False
        presenter_calls = 0
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module == "original_league_tables_presenter"
            ):
                imported = any(
                    alias.name == "build_league_tables_snapshot"
                    for alias in node.names
                )
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "build_league_tables_snapshot"
            ):
                presenter_calls += 1
        self.assertTrue(imported)
        self.assertGreaterEqual(presenter_calls, 1)
        self.assertIn("columns=('pos', 'club', 'p', 'w', 'd', 'l', 'f', 'a', 'pts')", source)
        self.assertNotIn("columns=('pos', 'club', 'p', 'w', 'd', 'l', 'gd', 'pts')", source)



if __name__ == "__main__":
    unittest.main()
