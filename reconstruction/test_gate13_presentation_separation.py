from __future__ import annotations

import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).parent


def top_level_import_modules(filename: str) -> tuple[str, ...]:
    source = (ROOT / filename).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=filename)
    modules = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module is not None and node.module != "__future__":
                modules.append(node.module)
        elif isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
    return tuple(modules)


class Gate13PresentationSeparationAuditTests(unittest.TestCase):
    def test_front_end_state_is_presentation_navigation_only(self):
        self.assertEqual(
            top_level_import_modules("front_end_state.py"),
            ("dataclasses", "enum"),
        )

    def test_front_end_session_does_not_import_simulation_at_module_load(self):
        modules = top_level_import_modules("front_end_session.py")
        self.assertNotIn("human_gameplay", modules)
        self.assertNotIn("game_state", modules)
        self.assertNotIn("match_calculator", modules)
        self.assertIn("front_end_state", modules)

        # The canonical backend adapter is deliberately lazy inside the
        # factory method so importing front-end presentation cannot initialize
        # or own simulation state.
        source = (ROOT / "front_end_session.py").read_text(encoding="utf-8")
        tree = ast.parse(source, filename="front_end_session.py")
        parent_of = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parent_of[child] = parent

        nearest_function_names = []
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.ImportFrom)
                and node.module == "human_gameplay"
            ):
                continue
            parent = parent_of.get(node)
            while parent is not None and not isinstance(
                parent, (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                parent = parent_of.get(parent)
            nearest_function_names.append(
                None if parent is None else parent.name
            )
        self.assertEqual(nearest_function_names, ["make_gameplay"])

    def test_original_first_screen_presenter_has_no_simulation_imports(self):
        modules = set(top_level_import_modules("original_first_screen_presenter.py"))
        forbidden = {
            "human_gameplay",
            "game_state",
            "competition_state",
            "match_calculator",
            "transfer_state",
            "finance_state",
            "runtime_state",
        }
        self.assertEqual(modules & forbidden, set())
        self.assertIn("front_end_session", modules)
        self.assertIn("front_end_state", modules)

    def test_pmatchinfo_presenter_has_no_simulation_imports(self):
        modules = set(top_level_import_modules("original_pmatchinfo_presenter.py"))
        forbidden = {
            "human_gameplay",
            "game_state",
            "competition_state",
            "match_calculator",
            "match_events",
            "match_presentation_feed",
            "transfer_state",
            "finance_state",
            "runtime_state",
        }
        self.assertEqual(modules & forbidden, set())
        self.assertIn("original_pmatchinfo_resources", modules)
        self.assertIn("ea444_decoder", modules)

    def test_management_projection_is_backend_type_agnostic_and_read_only(self):
        # The management bridge intentionally accepts a controller by duck
        # typing and imports no simulation package. This prevents presentation
        # code from becoming another implementation of game rules.
        self.assertEqual(
            top_level_import_modules("gate13_management_source_data.py"),
            ("dataclasses", "datetime"),
        )
        source = (ROOT / "gate13_management_source_data.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source, filename="gate13_management_source_data.py")

        mutating_names = {
            "advance_one_day",
            "advance_to_next_user_fixture",
            "play_user_fixture",
            "set_lineup",
            "set_tactics",
            "set_team_orders",
            "submit_cash_bid",
            "offer_player_contract",
            "process_due_transfers",
            "select_financial_objective",
        }
        invoked = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in mutating_names
        }
        self.assertEqual(invoked, set())


if __name__ == "__main__":
    unittest.main()
