from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import app as app_module


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



    def test_normal_launch_uses_source_backed_host_and_prototype_is_explicit_opt_in(self):
        source = APP_PATH.read_text(encoding="utf-8")
        self.assertIn("from original_game_host import run_original_game_ui", source)
        self.assertIn("'--prototype-ui'", source)
        self.assertIn("if args.prototype_ui:", source)
        self.assertIn("App(game_dir).mainloop()", source)
        self.assertIn("'--skip-startup-media'", source)
        self.assertIn("'--startup-media-receipt'", source)
        self.assertIn("'--startup-media-player'", source)
        self.assertIn("'--startup-media-player-arg'", source)
        self.assertIn("SynchronousCommandStartupMediaBackend", source)
        self.assertIn("WindowsMciStartupMediaBackend", source)
        self.assertIn("prepare_runtime_startup_media", source)
        self.assertIn("startup_media_receipt=startup_receipt", source)
        self.assertIn("startup_media_backend=startup_backend", source)
        self.assertIn("startup_media_derivatives=startup_derivatives", source)
        self.assertLess(
            source.index("if args.prototype_ui:"),
            source.index("run_original_game_ui("),
        )


    def test_normal_windows_launch_prepares_verified_cache_and_builtin_backend(self):
        args = SimpleNamespace(
            prototype_ui=False,
            startup_media_receipt=None,
            startup_media_player=None,
            startup_media_player_arg=[],
        )
        derivatives = (object(), object())
        backend = object()
        with patch.object(
            app_module,
            "prepare_runtime_startup_media",
            return_value=derivatives,
        ) as prepare, patch.object(
            app_module,
            "WindowsMciStartupMediaBackend",
            return_value=backend,
        ) as make_backend:
            receipt, selected_backend, selected_derivatives = (
                app_module.configure_startup_media(
                    args,
                    Path("/game"),
                    app_root=Path("/package"),
                    platform_system="Windows",
                )
            )

        self.assertIsNone(receipt)
        self.assertIs(selected_backend, backend)
        self.assertIs(selected_derivatives, derivatives)
        prepare.assert_called_once_with(
            Path("/game"),
            Path("/package").resolve(),
        )
        make_backend.assert_called_once_with(platform_system="Windows")

    def test_explicit_skip_startup_media_bypasses_default_windows_backend(self):
        args = SimpleNamespace(
            prototype_ui=False,
            skip_startup_media=True,
            startup_media_receipt=None,
            startup_media_player=None,
            startup_media_player_arg=[],
        )
        with (
            patch.object(app_module, "prepare_runtime_startup_media") as prepare,
            patch.object(app_module, "WindowsMciStartupMediaBackend") as backend,
        ):
            self.assertEqual(
                app_module.configure_startup_media(
                    args,
                    Path("/game"),
                    platform_system="Windows",
                ),
                (None, None, None),
            )
        prepare.assert_not_called()
        backend.assert_not_called()

    def test_skip_startup_media_rejects_explicit_player_override(self):
        args = SimpleNamespace(
            prototype_ui=False,
            skip_startup_media=True,
            startup_media_receipt=Path("/private/receipt.json"),
            startup_media_player="player.exe",
            startup_media_player_arg=[],
        )
        with self.assertRaisesRegex(ValueError, "cannot be combined"):
            app_module.configure_startup_media(
                args,
                Path("/game"),
                platform_system="Windows",
            )

    def test_non_windows_default_does_not_invent_startup_backend(self):
        args = SimpleNamespace(
            prototype_ui=False,
            startup_media_receipt=None,
            startup_media_player=None,
            startup_media_player_arg=[],
        )
        with patch.object(
            app_module,
            "prepare_runtime_startup_media",
        ) as prepare:
            self.assertEqual(
                app_module.configure_startup_media(
                    args,
                    Path("/game"),
                    platform_system="Linux",
                ),
                (None, None, None),
            )
        prepare.assert_not_called()

    def test_explicit_startup_player_remains_override(self):
        receipt = Path("/private/receipt.json")
        args = SimpleNamespace(
            prototype_ui=False,
            startup_media_receipt=receipt,
            startup_media_player="player.exe",
            startup_media_player_arg=["--fullscreen"],
        )
        backend = object()
        with patch.object(
            app_module,
            "SynchronousCommandStartupMediaBackend",
            return_value=backend,
        ) as make_backend, patch.object(
            app_module,
            "prepare_runtime_startup_media",
        ) as prepare:
            selected = app_module.configure_startup_media(
                args,
                Path("/game"),
                platform_system="Windows",
            )

        self.assertEqual(selected, (receipt, backend, None))
        make_backend.assert_called_once_with(
            "player.exe",
            ("--fullscreen",),
        )
        prepare.assert_not_called()

    def test_prototype_or_partial_override_fails_closed(self):
        prototype = SimpleNamespace(
            prototype_ui=True,
            startup_media_receipt=Path("/private/receipt.json"),
            startup_media_player="player.exe",
            startup_media_player_arg=[],
        )
        with self.assertRaisesRegex(ValueError, "source-backed FM2001 host"):
            app_module.configure_startup_media(
                prototype,
                Path("/game"),
                platform_system="Windows",
            )

        partial = SimpleNamespace(
            prototype_ui=False,
            startup_media_receipt=Path("/private/receipt.json"),
            startup_media_player=None,
            startup_media_player_arg=[],
        )
        with self.assertRaisesRegex(ValueError, "requires both"):
            app_module.configure_startup_media(
                partial,
                Path("/game"),
                platform_system="Windows",
            )



if __name__ == "__main__":
    unittest.main()
