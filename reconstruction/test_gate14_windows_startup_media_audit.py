"""Contract tests for the real-Windows startup-media acceptance audit."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from original_startup_media import ORIGINAL_STARTUP_MEDIA_SEQUENCE
from startup_media_derivatives import VerifiedStartupMediaDerivative
from startup_media_windows_backend import WindowsMciStartupMediaBackend
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


def backend():
    return WindowsMciStartupMediaBackend(
        platform_system="Windows",
        sender=lambda _command: 0,
    )


class Gate14WindowsStartupMediaAuditTests(unittest.TestCase):
    def test_pass_replays_exact_runtime_sequence_and_requires_human_yes_both(self):
        with tempfile.TemporaryDirectory() as temp:
            items = derivatives(Path(temp))
            prepare = Mock(return_value=items)
            prompts = []

            receipt = run_windows_startup_media_audit(
                "C:/FM2001",
                "C:/FM2001-port",
                backend=backend(),
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
        self.assertEqual(len(prompts), 1)
        self.assertIn("easp.tgq, then premintro.tgq", prompts[0])
        self.assertTrue(receipt["passed"])
        self.assertEqual(
            receipt["audit_kind"],
            "gate14_windows_startup_media_acceptance",
        )
        self.assertTrue(receipt["windows_11"])
        self.assertEqual(receipt["windows_build"], 26100)
        self.assertEqual(receipt["windows_product_type"], 1)
        self.assertEqual(
            receipt["playback_backend"],
            "WindowsMciStartupMediaBackend",
        )
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
        self.assertTrue(receipt["startup_media_real_windows_verified"])
        self.assertTrue(receipt["default_runtime_components_replayed"])
        self.assertFalse(receipt["normal_application_launch_invoked"])
        self.assertFalse(receipt["skip_input_recovered"])
        self.assertFalse(receipt["transition_timing_recovered"])
        self.assertFalse(receipt["exact_display_treatment_recovered"])
        self.assertFalse(receipt["gate14_complete"])

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
                "exact WindowsMciStartupMediaBackend",
            ):
                run_windows_startup_media_audit(
                    backend=object(),
                    confirmer=lambda _: VISIBLE_AUDIBLE_CONFIRMATION_TOKEN,
                    **common,
                )

            for response in ("YES", "yes-both", "", "YES-BOTH "):
                with self.subTest(response=response):
                    with self.assertRaisesRegex(
                        Gate14WindowsStartupMediaAuditError,
                        "not explicitly confirmed",
                    ):
                        run_windows_startup_media_audit(
                            backend=backend(),
                            confirmer=lambda _prompt, value=response: value,
                            **common,
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
            "schema_version": 1,
            "audit_kind": "gate14_windows_startup_media_acceptance",
            "passed": True,
            "startup_media_real_windows_verified": True,
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
