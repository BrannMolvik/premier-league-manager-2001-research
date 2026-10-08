"""Contract tests for the real-Windows startup-media acceptance audit."""
from pathlib import Path
from types import SimpleNamespace
import json
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import gate14_windows_startup_media_audit as audit
from original_startup_media import ORIGINAL_STARTUP_MEDIA_SEQUENCE
from startup_media_derivatives import VerifiedStartupMediaDerivative
from startup_media_playback import play_verified_startup_sequence
from startup_media_windows_backend import WindowsWpfStartupMediaBackend
from gate14_windows_startup_media_audit import (
    Gate14WindowsStartupMediaAuditError,
    VISIBLE_AUDIBLE_CONFIRMATION_TOKEN,
    _require_external_windows_11,
    _require_private_receipt,
    main as audit_main,
    run_windows_startup_media_audit,
)


def derivatives(root: Path):
    result = []
    for index, spec in enumerate(ORIGINAL_STARTUP_MEDIA_SEQUENCE):
        path = root / (Path(spec.source_path).stem + ".mp4")
        path.write_bytes(f"verified-{index}".encode("ascii"))
        result.append(
            VerifiedStartupMediaDerivative(
                sequence=index,
                spec=spec,
                path=path,
                converted_sha256=("%064x" % (index + 1)),
                converted_size_bytes=path.stat().st_size,
                container="mp4",
                video_codec="h264",
                pixel_format="yuv420p",
                audio_codec="aac",
            )
        )
    return tuple(result)


class FakeRoot:
    def __init__(self):
        self.destroyed = False

    def after(self, _delay, callback):
        callback()

    def destroy(self):
        self.destroyed = True


def backend(process_calls):
    def runner(command, **kwargs):
        process_calls.append((command, kwargs))
        env = kwargs["env"]
        sequence = len(process_calls) - 1
        parent_hwnd = int(env["FM2001_STARTUP_PARENT_HWND"])
        x = int(env["FM2001_STARTUP_MEDIA_X"])
        y = int(env["FM2001_STARTUP_MEDIA_Y"])
        width = int(env["FM2001_STARTUP_MEDIA_WIDTH"])
        height = int(env["FM2001_STARTUP_MEDIA_HEIGHT"])
        payload = {
            "parent_hwnd": parent_hwnd,
            "child_hwnd": 54321 + sequence,
            "requested_child_rect": {
                "x": x, "y": y, "width": width, "height": height,
            },
            "parent_window_rect": {
                "left": 90, "top": 70, "right": 910, "bottom": 710,
                "width": 820, "height": 640,
            },
            "parent_client_rect": {
                "left": 0, "top": 0, "right": 800, "bottom": 600,
                "width": 800, "height": 600,
            },
            "parent_client_origin_screen": {"x": 100, "y": 100},
            "child_window_rect": {
                "left": 100 + x, "top": 100 + y,
                "right": 100 + x + width, "bottom": 100 + y + height,
                "width": width, "height": height,
            },
            "child_client_rect": {
                "left": 0, "top": 0, "right": width, "bottom": height,
                "width": width, "height": height,
            },
            "child_client_origin_screen": {"x": 100 + x, "y": 100 + y},
            "child_offset_from_parent_client": {"x": x, "y": y},
            "parent_dpi": 96,
            "child_dpi": 96,
            "parent_dpi_awareness_context": -4,
            "child_dpi_awareness_context": -4,
            "probe_thread_dpi_awareness_context": -4,
            "parent_dpi_awareness": 2,
            "child_dpi_awareness": 2,
            "probe_thread_dpi_awareness": 2,
        }
        stdout = "FM2001_TRANSPORT_RECEIPT:" + json.dumps(
            payload, separators=(",", ":")
        )
        return SimpleNamespace(returncode=0, stderr="", stdout=stdout)

    return WindowsWpfStartupMediaBackend(
        platform_system="Windows",
        runner=runner,
    )


def production_host_stub(expected_items, host_calls):
    def run(game_dir, **kwargs):
        player = kwargs["startup_media_backend"]
        items = tuple(kwargs["startup_media_derivatives"])
        host_calls.append((game_dir, kwargs))
        if items != tuple(expected_items):
            raise AssertionError("audit did not pass the prepared derivatives to production host")
        binding = {
            "parent_hwnd": 12345,
            "x": 80,
            "y": 60,
            "width": 640,
            "height": 480,
        }
        player.bind_parent_window(
            binding["parent_hwnd"],
            x=binding["x"],
            y=binding["y"],
            width=binding["width"],
            height=binding["height"],
        )
        summary = play_verified_startup_sequence(items, player)
        if not summary.source_order_preserved or not all(
            step.completed for step in summary.steps
        ):
            raise AssertionError("fake production host did not complete startup sequence")
        root = FakeRoot()
        host = SimpleNamespace(
            root=root,
            startup_media_child_binding=lambda: dict(binding),
        )
        kwargs["host_ready_callback"](host, None)
        if not root.destroyed:
            raise AssertionError("acceptance callback did not close production host")

    return run


class Gate14WindowsStartupMediaAuditTests(unittest.TestCase):
    def test_pass_uses_production_host_wpf_child_path_and_requires_human_confirmation(self):
        with tempfile.TemporaryDirectory() as temp:
            items = derivatives(Path(temp))
            prepare = Mock(return_value=items)
            prompts = []
            process_calls = []
            host_calls = []

            with patch.object(
                audit,
                "run_original_game_ui",
                production_host_stub(items, host_calls),
            ):
                receipt = run_windows_startup_media_audit(
                    "C:/FM2001",
                    "C:/FM2001-port",
                    backend=backend(process_calls),
                    confirmer=lambda prompt: (
                        prompts.append(prompt) or VISIBLE_AUDIBLE_CONFIRMATION_TOKEN
                    ),
                    platform_system="Windows",
                    platform_release="11",
                    platform_version="10.0.26100",
                    github_actions="",
                    windows_product_type=1,
                    preparer=prepare,
                )

        prepare.assert_called_once_with("C:/FM2001", "C:/FM2001-port")
        self.assertEqual(len(host_calls), 1)
        self.assertEqual(len(process_calls), 2)
        self.assertEqual(len(prompts), 1)
        self.assertIn("easp.tgq, then premintro.tgq", prompts[0])
        self.assertIn("game-owned window", prompts[0])
        self.assertEqual(VISIBLE_AUDIBLE_CONFIRMATION_TOKEN, "YES-GAME-WINDOW")
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["schema_version"], 3)
        self.assertEqual(
            receipt["audit_kind"],
            "gate14_windows_startup_media_acceptance",
        )
        self.assertTrue(receipt["windows_11"])
        self.assertEqual(receipt["windows_build"], 26100)
        self.assertEqual(receipt["windows_product_type"], 1)
        self.assertEqual(
            receipt["playback_backend"],
            "WindowsWpfStartupMediaBackend",
        )
        self.assertEqual(receipt["production_host_runner"], "run_original_game_ui")
        self.assertTrue(receipt["normal_application_host_path_invoked"])
        self.assertFalse(receipt["normal_app_cli_invoked"])
        self.assertTrue(receipt["game_owned_child_window_verified"])
        self.assertTrue(receipt["backend_parent_binding_verified"])
        self.assertEqual(
            receipt["host_child_binding"],
            {
                "parent_hwnd": 12345,
                "x": 80,
                "y": 60,
                "width": 640,
                "height": 480,
            },
        )
        self.assertTrue(receipt["actual_hwnd_dpi_transport_captured"])
        self.assertEqual(len(receipt["transport_receipts"]), 2)
        self.assertEqual(
            [row["child_hwnd"] for row in receipt["transport_receipts"]],
            [54321, 54322],
        )
        self.assertTrue(
            all(
                row["child_offset_from_parent_client"] == {"x": 80, "y": 60}
                for row in receipt["transport_receipts"]
            )
        )
        self.assertTrue(
            all(row["parent_dpi"] == row["child_dpi"] == 96 for row in receipt["transport_receipts"])
        )
        self.assertEqual(
            receipt["source_presentation"]["coded_size"],
            [320, 480],
        )
        self.assertEqual(
            receipt["source_presentation"]["movie_size"],
            [640, 480],
        )
        self.assertEqual(
            receipt["source_presentation"]["ordinary_movie_offset"],
            [80, 60],
        )
        self.assertEqual(receipt["source_presentation"]["horizontal_repeat"], 2)
        self.assertIn("flags=neighbor", receipt["source_presentation"]["ffmpeg_filter"])
        self.assertEqual(len(receipt["startup_sequence"]), 2)
        self.assertEqual(
            tuple(row["source_path"] for row in receipt["startup_sequence"]),
            tuple(spec.source_path for spec in ORIGINAL_STARTUP_MEDIA_SEQUENCE),
        )
        self.assertTrue(
            all(row["playback_completed"] for row in receipt["startup_sequence"])
        )
        self.assertTrue(receipt["source_order_preserved"])
        self.assertTrue(receipt["human_visibility_confirmation"])
        self.assertTrue(receipt["human_audibility_confirmation"])
        self.assertTrue(receipt["human_game_owned_window_confirmation"])
        self.assertTrue(receipt["startup_media_real_windows_verified"])
        self.assertTrue(receipt["visual_acceptance_claimed"])
        self.assertTrue(receipt["default_runtime_components_replayed"])
        self.assertTrue(receipt["source_display_geometry_integrated"])
        self.assertTrue(receipt["exact_horizontal_repeat_integrated"])
        self.assertFalse(receipt["normal_application_launch_invoked"])
        self.assertFalse(receipt["skip_input_recovered"])
        self.assertFalse(receipt["transition_timing_recovered"])
        self.assertFalse(receipt["exact_display_treatment_recovered"])
        self.assertFalse(receipt["gate14_complete"])

        for _command, kwargs in process_calls:
            env = kwargs["env"]
            self.assertEqual(env["FM2001_STARTUP_PARENT_HWND"], "12345")
            self.assertEqual(env["FM2001_STARTUP_MEDIA_X"], "80")
            self.assertEqual(env["FM2001_STARTUP_MEDIA_Y"], "60")
            self.assertEqual(env["FM2001_STARTUP_MEDIA_WIDTH"], "640")
            self.assertEqual(env["FM2001_STARTUP_MEDIA_HEIGHT"], "480")
            self.assertEqual(env["FM2001_STARTUP_CAPTURE_TRANSPORT"], "1")

    def test_external_windows_guard_rejects_non_windows_hosted_server_and_old_build(self):
        cases = (
            (
                "Windows 11",
                dict(
                    platform_system="Linux",
                    platform_release="Linux",
                    platform_version="6.8",
                    github_actions="",
                    windows_product_type=1,
                ),
            ),
            (
                "GitHub Actions",
                dict(
                    platform_system="Windows",
                    platform_release="11",
                    platform_version="10.0.26100",
                    github_actions="true",
                    windows_product_type=1,
                ),
            ),
            (
                "client workstation",
                dict(
                    platform_system="Windows",
                    platform_release="11",
                    platform_version="10.0.26100",
                    github_actions="",
                    windows_product_type=3,
                ),
            ),
            (
                "build 22000",
                dict(
                    platform_system="Windows",
                    platform_release="10",
                    platform_version="10.0.19045",
                    github_actions="",
                    windows_product_type=1,
                ),
            ),
        )
        for expected, kwargs in cases:
            with self.subTest(expected=expected):
                with self.assertRaisesRegex(
                    Gate14WindowsStartupMediaAuditError,
                    expected,
                ):
                    _require_external_windows_11(**kwargs)

    def test_transport_probe_only_captures_hwnd_dpi_without_visual_acceptance(self):
        with tempfile.TemporaryDirectory() as temp:
            items = derivatives(Path(temp))
            process_calls = []
            host_calls = []
            with patch.object(
                audit,
                "run_original_game_ui",
                production_host_stub(items, host_calls),
            ):
                receipt = run_windows_startup_media_audit(
                    "C:/FM2001",
                    "C:/FM2001-port",
                    backend=backend(process_calls),
                    confirmer=lambda _prompt: self.fail(
                        "transport-only probe must not ask for visual acceptance"
                    ),
                    platform_system="Windows",
                    platform_release="11",
                    platform_version="10.0.26100",
                    github_actions="",
                    windows_product_type=1,
                    preparer=lambda _game, _root: items,
                    transport_probe_only=True,
                )

        self.assertEqual(receipt["schema_version"], 3)
        self.assertEqual(receipt["audit_kind"], "gate13_windows_startup_transport_probe")
        self.assertTrue(receipt["passed"])
        self.assertTrue(receipt["actual_hwnd_dpi_transport_captured"])
        self.assertFalse(receipt["visual_acceptance_claimed"])
        self.assertFalse(receipt["human_visibility_confirmation"])
        self.assertFalse(receipt["startup_media_real_windows_verified"])
        self.assertEqual(len(receipt["transport_receipts"]), 2)
        self.assertFalse(receipt["exact_display_treatment_recovered"])
        self.assertFalse(receipt["gate14_complete"])

    def test_arbitrary_backend_and_failed_human_confirmation_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            items = derivatives(Path(temp))
            common = dict(
                game_dir="C:/FM2001",
                application_root="C:/port",
                platform_system="Windows",
                platform_release="11",
                platform_version="10.0.26100",
                github_actions="",
                windows_product_type=1,
                preparer=lambda _game, _root: items,
            )
            with self.assertRaisesRegex(
                Gate14WindowsStartupMediaAuditError,
                "exact WindowsWpfStartupMediaBackend",
            ):
                run_windows_startup_media_audit(
                    backend=object(),
                    confirmer=lambda _: VISIBLE_AUDIBLE_CONFIRMATION_TOKEN,
                    **common,
                )

            for response in ("YES", "YES-BOTH", "yes-game-window", "", "YES-GAME-WINDOW "):
                with self.subTest(response=response):
                    process_calls = []
                    host_calls = []
                    with (
                        patch.object(
                            audit,
                            "run_original_game_ui",
                            production_host_stub(items, host_calls),
                        ),
                        self.assertRaisesRegex(
                            Gate14WindowsStartupMediaAuditError,
                            "not explicitly confirmed",
                        ),
                    ):
                        run_windows_startup_media_audit(
                            backend=backend(process_calls),
                            confirmer=lambda _prompt, value=response: value,
                            **common,
                        )
                    self.assertEqual(len(host_calls), 1)
                    self.assertEqual(len(process_calls), 2)

    def test_production_host_must_bind_exact_wpf_backend_to_same_child_geometry(self):
        with tempfile.TemporaryDirectory() as temp:
            items = derivatives(Path(temp))
            process_calls = []

            def bad_host(_game_dir, **kwargs):
                player = kwargs["startup_media_backend"]
                player.bind_parent_window(1, x=80, y=60, width=640, height=480)
                play_verified_startup_sequence(items, player)
                host = SimpleNamespace(
                    root=FakeRoot(),
                    startup_media_child_binding=lambda: {
                        "parent_hwnd": 2,
                        "x": 80,
                        "y": 60,
                        "width": 640,
                        "height": 480,
                    },
                )
                kwargs["host_ready_callback"](host, None)

            with (
                patch.object(audit, "run_original_game_ui", bad_host),
                self.assertRaisesRegex(
                    Gate14WindowsStartupMediaAuditError,
                    "not bound to the production game HWND",
                ),
            ):
                run_windows_startup_media_audit(
                    "C:/FM2001",
                    "C:/port",
                    backend=backend(process_calls),
                    confirmer=lambda _: VISIBLE_AUDIBLE_CONFIRMATION_TOKEN,
                    platform_system="Windows",
                    platform_release="11",
                    platform_version="10.0.26100",
                    github_actions="",
                    windows_product_type=1,
                    preparer=lambda _game, _root: items,
                )

    def test_private_receipt_must_be_outside_git_and_never_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            with self.assertRaisesRegex(
                Gate14WindowsStartupMediaAuditError,
                "outside Git",
            ):
                _require_private_receipt(
                    root / "startup.json",
                    repository_root=root,
                )

            outside = Path(temp) / "private" / "startup.json"
            checked = _require_private_receipt(
                outside,
                repository_root=root,
            )
            self.assertEqual(checked, outside.resolve())
            checked.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(
                Gate14WindowsStartupMediaAuditError,
                "do not overwrite",
            ):
                _require_private_receipt(
                    outside,
                    repository_root=root,
                )

    def test_cli_writes_only_returned_private_receipt(self):
        receipt = {
            "schema_version": 3,
            "audit_kind": "gate14_windows_startup_media_acceptance",
            "passed": True,
            "startup_media_real_windows_verified": True,
            "normal_application_host_path_invoked": True,
            "skip_input_recovered": False,
            "gate14_complete": False,
        }
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "private" / "startup.json"
            argv = [
                "gate14_windows_startup_media_audit.py",
                "--game-dir",
                "C:/FM2001",
                "--application-root",
                "C:/port",
                "--output-receipt",
                str(output),
            ]
            with (
                patch.object(sys, "argv", argv),
                patch(
                    "gate14_windows_startup_media_audit.run_windows_startup_media_audit",
                    return_value=receipt,
                ) as run,
            ):
                self.assertEqual(audit_main(), 0)

            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8")),
                receipt,
            )
            run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
