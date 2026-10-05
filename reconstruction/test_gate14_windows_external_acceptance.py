"""Tests for the transactional Gate-14 external Windows acceptance coordinator."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import tempfile
import unittest

from gate14_windows_external_acceptance import (
    BOUND_AUDIO_RECEIPT_FILENAME,
    BUNDLE_MANIFEST_FILENAME,
    STARTUP_RECEIPT_FILENAME,
    Gate14WindowsAcceptanceCoordinatorError,
    build_external_acceptance_bundle,
    run_windows_external_acceptance,
    write_external_acceptance_bundle,
)


def _windows_fields() -> dict:
    return {
        "platform_system": "Windows",
        "platform_release": "11",
        "platform_version": "10.0.26100",
        "windows_build": 26100,
        "windows_product_type": 1,
        "windows_11": True,
        "outside_github_actions": True,
    }


def _startup_receipt() -> dict:
    return {
        "schema_version": 1,
        "audit_kind": "gate14_windows_startup_media_acceptance",
        "passed": True,
        **_windows_fields(),
        "source_order_preserved": True,
        "human_visibility_confirmation": True,
        "human_audibility_confirmation": True,
        "startup_media_real_windows_verified": True,
        "default_runtime_components_replayed": True,
        "gate14_complete": False,
    }


def _bound_audio_receipt() -> dict:
    return {
        "schema_version": 1,
        "audit_kind": "gate14_windows_bound_first_screen_audio_acceptance",
        "passed": True,
        **_windows_fields(),
        "normal_application_host_path_invoked": True,
        "human_audibility_confirmation": True,
        "bound_application_press_audio_verified": True,
        "audible_windows_verified": True,
        "first_screen_press_binding_source_recovered": True,
        "broad_audio_event_binding_recovered": False,
        "sample_meaning_recovered": False,
        "hover_audio_integrated": False,
        "login_menu_audio_integrated": False,
        "gate14_complete": False,
    }


class Gate14WindowsExternalAcceptanceTests(unittest.TestCase):
    def test_bundle_joins_only_the_two_bounded_windows_proofs(self):
        bundle = build_external_acceptance_bundle(
            _startup_receipt(),
            _bound_audio_receipt(),
        )

        self.assertTrue(bundle["passed"])
        self.assertTrue(bundle["startup_media_real_windows_verified"])
        self.assertTrue(bundle["first_screen_press_audio_real_windows_verified"])
        self.assertFalse(bundle["broad_audio_event_binding_recovered"])
        self.assertFalse(bundle["login_menu_audio_integrated"])
        self.assertFalse(bundle["source_fastview_navigation_trigger_recovered"])
        self.assertFalse(bundle["recognizable_original_match_workflow_verified"])
        self.assertFalse(bundle["gate14_complete"])

    def test_child_receipt_cannot_self_promote_broad_audio_or_gate_completion(self):
        for key, value in (
            ("broad_audio_event_binding_recovered", True),
            ("sample_meaning_recovered", True),
            ("hover_audio_integrated", True),
            ("login_menu_audio_integrated", True),
            ("gate14_complete", True),
        ):
            with self.subTest(key=key):
                audio = _bound_audio_receipt()
                audio[key] = value
                with self.assertRaises(Gate14WindowsAcceptanceCoordinatorError):
                    build_external_acceptance_bundle(_startup_receipt(), audio)

    def test_startup_receipt_must_keep_gate_open_and_prove_human_acceptance(self):
        for key, value in (
            ("human_visibility_confirmation", False),
            ("human_audibility_confirmation", False),
            ("startup_media_real_windows_verified", False),
            ("gate14_complete", True),
        ):
            with self.subTest(key=key):
                startup = _startup_receipt()
                startup[key] = value
                with self.assertRaises(Gate14WindowsAcceptanceCoordinatorError):
                    build_external_acceptance_bundle(startup, _bound_audio_receipt())

    def test_child_receipts_must_describe_same_windows_client(self):
        audio = _bound_audio_receipt()
        audio["windows_build"] = 22631
        with self.assertRaisesRegex(
            Gate14WindowsAcceptanceCoordinatorError,
            "disagree on Windows client field windows_build",
        ):
            build_external_acceptance_bundle(_startup_receipt(), audio)

    def test_runner_executes_both_existing_transactions_before_returning(self):
        calls = []

        def startup_runner(game_dir, application_root):
            calls.append(("startup", Path(game_dir), Path(application_root)))
            return _startup_receipt()

        def audio_runner(game_dir, *, source_root=None):
            calls.append(("audio", Path(game_dir), Path(source_root)))
            return _bound_audio_receipt()

        startup, audio, bundle = run_windows_external_acceptance(
            "C:/Games/FM2001",
            "C:/FM2001-App",
            source_root="C:/Source",
            startup_runner=startup_runner,
            bound_audio_runner=audio_runner,
        )

        self.assertEqual(
            calls,
            [
                ("startup", Path("C:/Games/FM2001"), Path("C:/FM2001-App")),
                ("audio", Path("C:/Games/FM2001"), Path("C:/Source")),
            ],
        )
        self.assertEqual(startup["audit_kind"], _startup_receipt()["audit_kind"])
        self.assertEqual(audio["audit_kind"], _bound_audio_receipt()["audit_kind"])
        self.assertTrue(bundle["passed"])

    def test_second_audit_failure_produces_no_bundle_result(self):
        calls = []

        def startup_runner(game_dir, application_root):
            calls.append("startup")
            return _startup_receipt()

        def audio_runner(game_dir, *, source_root=None):
            calls.append("audio")
            raise RuntimeError("human did not confirm")

        with self.assertRaisesRegex(RuntimeError, "human did not confirm"):
            run_windows_external_acceptance(
                "C:/Games/FM2001",
                "C:/FM2001-App",
                startup_runner=startup_runner,
                bound_audio_runner=audio_runner,
            )
        self.assertEqual(calls, ["startup", "audio"])

    def test_private_writer_creates_distinct_hash_bound_receipts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repository_root = root / "repo"
            repository_root.mkdir()
            output = root / "private-evidence"

            manifest = write_external_acceptance_bundle(
                output,
                _startup_receipt(),
                _bound_audio_receipt(),
                repository_root=repository_root,
            )

            self.assertTrue((output / STARTUP_RECEIPT_FILENAME).is_file())
            self.assertTrue((output / BOUND_AUDIO_RECEIPT_FILENAME).is_file())
            self.assertTrue((output / BUNDLE_MANIFEST_FILENAME).is_file())
            saved_manifest = json.loads(
                (output / BUNDLE_MANIFEST_FILENAME).read_text(encoding="utf-8")
            )
            self.assertEqual(saved_manifest, manifest)
            self.assertEqual(len(manifest["child_receipts"]), 2)
            self.assertNotEqual(
                manifest["child_receipts"][0]["sha256"],
                manifest["child_receipts"][1]["sha256"],
            )
            self.assertFalse(manifest["gate14_complete"])

    def test_writer_rejects_git_tree_and_existing_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repository_root = root / "repo"
            repository_root.mkdir()

            with self.assertRaisesRegex(
                Gate14WindowsAcceptanceCoordinatorError,
                "outside Git",
            ):
                write_external_acceptance_bundle(
                    repository_root / "evidence",
                    _startup_receipt(),
                    _bound_audio_receipt(),
                    repository_root=repository_root,
                )

            existing = root / "already-there"
            existing.mkdir()
            with self.assertRaisesRegex(
                Gate14WindowsAcceptanceCoordinatorError,
                "do not overwrite",
            ):
                write_external_acceptance_bundle(
                    existing,
                    _startup_receipt(),
                    _bound_audio_receipt(),
                    repository_root=repository_root,
                )


if __name__ == "__main__":
    unittest.main()
