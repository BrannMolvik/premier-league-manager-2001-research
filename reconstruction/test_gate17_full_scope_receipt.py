"""Tests for the current-contract Gate-17 full-scope receipt producer."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from gate17_full_scope_receipt import (
    FullScopeReceiptError,
    REQUIRED_PER_SCOPE_FLAGS,
    run_full_scope_receipt,
    validate_full_scope_results,
)
from gate17_windows_gameplay_receipts import ReleaseArtifactIdentity


COMMIT = "a" * 40
VERSION = "rc-full-scope"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()



def release_identity():
    return ReleaseArtifactIdentity(
        release_version=VERSION,
        repository_commit=COMMIT,
        release_archive_sha256="b" * 64,
        release_archive_size=123,
    )

def binding():
    return {
        "scope_catalog_sha256": "c" * 64,
        "scope_country_count": 2,
        "scope_entry_count": 2,
        "scope_selectable_club_row_count": 4,
        "scope_ids": ("1:10", "2:20"),
    }


def scope_results():
    return {
        "schema_version": 2,
        "release_version": VERSION,
        "repository_commit": COMMIT,
        "release_archive_sha256": "b" * 64,
        "release_archive_size": 123,
        "windows_11": True,
        "windows_build": 26200,
        "windows_product_type": 1,
        "scope_catalog_sha256": "c" * 64,
        "multi_human_management": True,
        "simultaneous_human_users_verified": 6,
        "results": [
            {
                "scope_id": "1:10",
                "passed": True,
                "human_career_flow": True,
                "competition_progression": True,
                "original_management_gameplay_subsystems": True,
                "save_reload": True,
            },
            {
                "scope_id": "2:20",
                "passed": True,
                "human_career_flow": True,
                "competition_progression": True,
                "original_management_gameplay_subsystems": True,
                "save_reload": True,
            },
        ],
    }


class Gate17FullScopeReceiptTests(unittest.TestCase):
    def _fixture(self, temp):
        root = Path(temp)
        repo = root / "repo"
        repo.mkdir()
        game = root / "game"
        game.mkdir()
        results = root / "scope-results.json"
        results.write_text(json.dumps(scope_results()), encoding="utf-8")
        archive = root / "release.zip"
        archive.write_bytes(b"candidate")
        output = root / "full_original_scope.json"
        return repo, game, results, archive, output

    def _catalog_patches(self):
        return (
            patch(
                "gate17_full_scope_receipt.load_canonical_original_playable_scope",
                return_value=SimpleNamespace(catalog_sha256="c" * 64),
            ),
            patch(
                "gate17_full_scope_receipt.build_full_scope_receipt_binding",
                return_value=binding(),
            ),
        )

    def test_required_scope_flags_include_save_reload(self):
        self.assertEqual(
            REQUIRED_PER_SCOPE_FLAGS,
            (
                "human_career_flow",
                "competition_progression",
                "original_management_gameplay_subsystems",
                "save_reload",
            ),
        )

    def test_results_bind_exact_catalog_order_and_multi_human_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, game, results, _archive, _output = self._fixture(temp)
            p1, p2 = self._catalog_patches()
            with p1, p2:
                checked = validate_full_scope_results(
                    results_path=results,
                    repo_root=repo,
                    canonical_game_dir=game,
                    identity=release_identity(),
                )
            self.assertEqual(checked["scope_catalog_sha256"], "c" * 64)
            self.assertEqual(checked["verified_scope_ids"], ("1:10", "2:20"))
            self.assertEqual(
                checked["save_reload_verified_scope_ids"],
                ("1:10", "2:20"),
            )
            self.assertEqual(checked["simultaneous_human_users_verified"], 6)
            self.assertEqual(checked["sha256"], digest(results))

    def test_results_reject_wrong_order_missing_flags_and_wrong_user_count(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, game, results, _archive, _output = self._fixture(temp)
            p1, p2 = self._catalog_patches()
            payload = scope_results()
            payload["results"].reverse()
            results.write_text(json.dumps(payload), encoding="utf-8")
            with p1, p2:
                with self.assertRaisesRegex(FullScopeReceiptError, "do not exactly match"):
                    validate_full_scope_results(
                        results_path=results,
                        repo_root=repo,
                        canonical_game_dir=game,
                    )

        with tempfile.TemporaryDirectory() as temp:
            repo, game, results, _archive, _output = self._fixture(temp)
            payload = scope_results()
            payload["results"][0]["save_reload"] = False
            results.write_text(json.dumps(payload), encoding="utf-8")
            p1, p2 = self._catalog_patches()
            with p1, p2:
                with self.assertRaisesRegex(FullScopeReceiptError, "failed scope IDs"):
                    validate_full_scope_results(
                        results_path=results,
                        repo_root=repo,
                        canonical_game_dir=game,
                    )

        with tempfile.TemporaryDirectory() as temp:
            repo, game, results, _archive, _output = self._fixture(temp)
            payload = scope_results()
            payload["simultaneous_human_users_verified"] = 5
            results.write_text(json.dumps(payload), encoding="utf-8")
            p1, p2 = self._catalog_patches()
            with p1, p2:
                with self.assertRaisesRegex(FullScopeReceiptError, "must equal 6"):
                    validate_full_scope_results(
                        results_path=results,
                        repo_root=repo,
                        canonical_game_dir=game,
                    )

    def test_results_reject_release_identity_and_windows_provenance_drift(self):
        drift_cases = (
            ("release_version", "older"),
            ("repository_commit", "0" * 40),
            ("release_archive_sha256", "0" * 64),
            ("release_archive_size", 999),
            ("windows_11", False),
            ("windows_build", 21999),
            ("windows_product_type", 3),
        )
        for key, value in drift_cases:
            with self.subTest(key=key):
                with tempfile.TemporaryDirectory() as temp:
                    repo, game, results, _archive, _output = self._fixture(temp)
                    payload = scope_results()
                    payload[key] = value
                    results.write_text(json.dumps(payload), encoding="utf-8")
                    p1, p2 = self._catalog_patches()
                    with p1, p2:
                        with self.assertRaises(FullScopeReceiptError):
                            validate_full_scope_results(
                                results_path=results,
                                repo_root=repo,
                                canonical_game_dir=game,
                                identity=release_identity(),
                            )

    def test_incomplete_implementation_preflight_blocks_before_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, game, results, archive, output = self._fixture(temp)
            with (
                patch(
                    "gate17_full_scope_receipt.require_external_windows_11_workstation",
                    return_value={"windows_11": True, "windows_build": 26200, "windows_product_type": 1},
                ),
                patch(
                    "gate17_full_scope_receipt.resolve_release_artifact_identity",
                    return_value=release_identity(),
                ),
                patch(
                    "gate17_full_scope_receipt.run_canonical_full_scope_preflight",
                    return_value=SimpleNamespace(
                        ready_for_full_runtime_validation=False,
                        blocker_codes=("runtime_owner_capability_incomplete",),
                    ),
                ),
            ):
                with self.assertRaisesRegex(
                    FullScopeReceiptError,
                    "implementation preflight is not ready",
                ):
                    run_full_scope_receipt(
                        repo_root=repo,
                        canonical_game_dir=game,
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        scope_results=results,
                        output_path=output,
                    )
            self.assertFalse(output.exists())

    def test_receipt_rejects_scope_results_from_different_windows_build(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, game, results, archive, output = self._fixture(temp)
            p1, p2 = self._catalog_patches()
            with (
                patch(
                    "gate17_full_scope_receipt.require_external_windows_11_workstation",
                    return_value={
                        "platform": "Windows-11",
                        "windows_11": True,
                        "windows_build": 26201,
                        "windows_product_type": 1,
                    },
                ),
                patch(
                    "gate17_full_scope_receipt.resolve_release_artifact_identity",
                    return_value=release_identity(),
                ),
                patch(
                    "gate17_full_scope_receipt.run_canonical_full_scope_preflight",
                    return_value=SimpleNamespace(
                        ready_for_full_runtime_validation=True,
                        blocker_codes=(),
                    ),
                ),
                p1,
                p2,
            ):
                with self.assertRaisesRegex(
                    FullScopeReceiptError,
                    "Windows build differs",
                ):
                    run_full_scope_receipt(
                        repo_root=repo,
                        canonical_game_dir=game,
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        scope_results=results,
                        output_path=output,
                    )
            self.assertFalse(output.exists())

    def test_success_emits_every_current_release_binding_field(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, game, results, archive, output = self._fixture(temp)
            p1, p2 = self._catalog_patches()
            with (
                patch(
                    "gate17_full_scope_receipt.require_external_windows_11_workstation",
                    return_value={
                        "platform": "Windows-11",
                        "windows_11": True,
                        "windows_build": 26200,
                        "windows_product_type": 1,
                    },
                ),
                patch(
                    "gate17_full_scope_receipt.resolve_release_artifact_identity",
                    return_value=release_identity(),
                ),
                patch(
                    "gate17_full_scope_receipt.run_canonical_full_scope_preflight",
                    return_value=SimpleNamespace(
                        ready_for_full_runtime_validation=True,
                        blocker_codes=(),
                    ),
                ),
                p1,
                p2,
            ):
                path = run_full_scope_receipt(
                    repo_root=repo,
                    canonical_game_dir=game,
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    release_archive=archive,
                    scope_results=results,
                    output_path=output,
                )

            self.assertEqual(path.resolve(), output.resolve())
            payload = json.loads(output.read_text(encoding="utf-8"))
            for flag in (
                "passed",
                "full_original_scope",
                "all_original_playable_leagues",
                "all_original_playable_countries",
                "human_career_flow",
                "competition_progression",
                "original_management_gameplay_subsystems",
                "all_original_scope_save_reload",
                "multi_human_management",
            ):
                self.assertTrue(payload[flag])
            self.assertEqual(payload["simultaneous_human_users_verified"], 6)
            self.assertEqual(payload["scope_catalog_sha256"], "c" * 64)
            self.assertEqual(payload["scope_country_count"], 2)
            self.assertEqual(payload["scope_entry_count"], 2)
            self.assertEqual(payload["scope_selectable_club_row_count"], 4)
            self.assertEqual(payload["verified_scope_ids"], ["1:10", "2:20"])
            self.assertEqual(payload["save_reload_verified_scope_ids"], ["1:10", "2:20"])
            self.assertEqual(payload["missing_scope_ids"], [])
            self.assertEqual(payload["failed_scope_ids"], [])
            self.assertEqual(payload["save_reload_missing_scope_ids"], [])
            self.assertEqual(payload["save_reload_failed_scope_ids"], [])
            self.assertEqual(payload["scope_results_sha256"], digest(results))

    def test_results_and_output_must_remain_outside_repository(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, game, results, _archive, _output = self._fixture(temp)
            inside = repo / "scope-results.json"
            inside.write_text(results.read_text(encoding="utf-8"), encoding="utf-8")
            with self.assertRaisesRegex(
                FullScopeReceiptError,
                "outside the Git repository",
            ):
                validate_full_scope_results(
                    results_path=inside,
                    repo_root=repo,
                    canonical_game_dir=game,
                    identity=release_identity(),
                )


if __name__ == "__main__":
    unittest.main()
