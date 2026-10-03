"""Tests for the fail-closed Gate-17 full-scope receipt producer."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from gate17_full_scope_receipt import (
    FullScopeReceiptError,
    REQUIRED_SCOPE_RESULT_FLAGS,
    run_full_scope_receipt,
    validate_scope_results,
)


COMMIT = "a" * 40
VERSION = "rc-full-scope"


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


class Gate17FullScopeReceiptTests(unittest.TestCase):
    def _fixture(self, temp):
        root = Path(temp)
        repo = root / "repo"
        repo.mkdir()
        research = repo / "research"
        research.mkdir()
        catalog = {
            "schema_version": 1,
            "status": "source_backed_complete",
            "expected_entry_count": 2,
            "source_evidence": ["synthetic-source-a", "synthetic-source-b"],
            "entries": [
                {
                    "scope_id": "scope-england-premier",
                    "country": "England",
                    "competition": "Premier",
                    "source_reference": "synthetic-ref-1",
                    "originally_playable": True,
                },
                {
                    "scope_id": "scope-example-league",
                    "country": "Exampleland",
                    "competition": "Example League",
                    "source_reference": "synthetic-ref-2",
                    "originally_playable": True,
                },
            ],
        }
        catalog_path = research / "GATE17_ORIGINAL_SCOPE_CATALOG.json"
        catalog_path.write_text(
            json.dumps(catalog, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        results = {
            "schema_version": 1,
            "scope_catalog_sha256": digest(catalog_path),
            "results": [
                {
                    "scope_id": "scope-england-premier",
                    "passed": True,
                    "human_career_flow": True,
                    "competition_progression": True,
                    "original_management_gameplay_subsystems": True,
                },
                {
                    "scope_id": "scope-example-league",
                    "passed": True,
                    "human_career_flow": True,
                    "competition_progression": True,
                    "original_management_gameplay_subsystems": True,
                },
            ],
        }
        results_path = root / "scope-results.json"
        results_path.write_text(json.dumps(results), encoding="utf-8")
        archive = root / "release.zip"
        archive.write_bytes(b"candidate")
        output = root / "full_original_scope.json"
        return repo, catalog_path, results_path, archive, output

    def test_scope_results_match_exact_catalog_order_and_required_flags(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, catalog, results, _archive, _output = self._fixture(temp)
            checked = validate_scope_results(
                results_path=results,
                repo_root=repo,
            )
            self.assertEqual(checked["scope_catalog_sha256"], digest(catalog))
            self.assertEqual(checked["scope_entry_count"], 2)
            self.assertEqual(
                checked["verified_scope_ids"],
                ("scope-england-premier", "scope-example-league"),
            )
            self.assertEqual(set(REQUIRED_SCOPE_RESULT_FLAGS), {
                "human_career_flow",
                "competition_progression",
                "original_management_gameplay_subsystems",
            })

    def test_scope_results_reject_catalog_hash_order_and_per_scope_failures(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, catalog, results, _archive, _output = self._fixture(temp)

            payload = json.loads(results.read_text(encoding="utf-8"))
            payload["scope_catalog_sha256"] = "0" * 64
            results.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(FullScopeReceiptError, "different scope catalog"):
                validate_scope_results(results_path=results, repo_root=repo)

            payload["scope_catalog_sha256"] = digest(catalog)
            payload["results"].reverse()
            results.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(FullScopeReceiptError, "do not exactly match"):
                validate_scope_results(results_path=results, repo_root=repo)

            payload["results"].reverse()
            payload["results"][0]["competition_progression"] = False
            results.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                FullScopeReceiptError,
                "failed scope IDs: scope-england-premier",
            ):
                validate_scope_results(results_path=results, repo_root=repo)

    def test_unrecovered_repository_catalog_blocks_receipt_before_output(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, catalog, results, archive, output = self._fixture(temp)
            payload = json.loads(catalog.read_text(encoding="utf-8"))
            payload["status"] = "unrecovered"
            payload["expected_entry_count"] = 0
            payload["entries"] = []
            catalog.write_text(json.dumps(payload), encoding="utf-8")

            with (
                patch(
                    "gate17_full_scope_receipt.require_external_windows_11_workstation",
                    return_value={
                        "windows_11": True,
                        "windows_build": 26200,
                        "windows_product_type": 1,
                    },
                ),
                patch(
                    "gate17_full_scope_receipt.resolve_release_artifact_identity",
                    return_value=SimpleNamespace(
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive_sha256="b" * 64,
                        release_archive_size=123,
                    ),
                ),
            ):
                with self.assertRaisesRegex(
                    Exception,
                    "not source_backed_complete",
                ):
                    run_full_scope_receipt(
                        repo_root=repo,
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        scope_results=results,
                        output_path=output,
                    )
            self.assertFalse(output.exists())

    def test_success_writes_archive_catalog_and_result_bound_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, catalog, results, archive, output = self._fixture(temp)
            identity = SimpleNamespace(
                release_version=VERSION,
                repository_commit=COMMIT,
                release_archive_sha256="b" * 64,
                release_archive_size=123,
            )
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
                    return_value=identity,
                ),
            ):
                path = run_full_scope_receipt(
                    repo_root=repo,
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    release_archive=archive,
                    scope_results=results,
                    output_path=output,
                )

            self.assertEqual(path.resolve(), output.resolve())
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(payload["passed"])
            self.assertTrue(payload["full_original_scope"])
            self.assertTrue(payload["all_original_playable_leagues"])
            self.assertTrue(payload["all_original_playable_countries"])
            self.assertEqual(payload["scope_catalog_sha256"], digest(catalog))
            self.assertEqual(payload["scope_results_sha256"], digest(results))
            self.assertEqual(payload["scope_entry_count"], 2)
            self.assertEqual(payload["verified_scope_entry_count"], 2)
            self.assertEqual(
                payload["verified_scope_ids"],
                ["scope-england-premier", "scope-example-league"],
            )
            self.assertEqual(payload["missing_scope_ids"], [])
            self.assertEqual(payload["failed_scope_ids"], [])
            self.assertEqual(payload["release_archive_sha256"], "b" * 64)
            self.assertEqual(payload["repository_commit"], COMMIT)

    def test_results_and_receipt_must_remain_outside_git_and_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, _catalog, results, archive, output = self._fixture(temp)
            inside = repo / "scope-results.json"
            inside.write_text(results.read_text(encoding="utf-8"), encoding="utf-8")
            with self.assertRaisesRegex(FullScopeReceiptError, "outside the Git repository"):
                validate_scope_results(results_path=inside, repo_root=repo)

            output.write_text("{}", encoding="utf-8")
            with (
                patch(
                    "gate17_full_scope_receipt.require_external_windows_11_workstation",
                    return_value={
                        "windows_11": True,
                        "windows_build": 26200,
                        "windows_product_type": 1,
                    },
                ),
                patch(
                    "gate17_full_scope_receipt.resolve_release_artifact_identity",
                    return_value=SimpleNamespace(
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive_sha256="b" * 64,
                        release_archive_size=123,
                    ),
                ),
            ):
                with self.assertRaisesRegex(FullScopeReceiptError, "do not overwrite"):
                    run_full_scope_receipt(
                        repo_root=repo,
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        scope_results=results,
                        output_path=output,
                    )


if __name__ == "__main__":
    unittest.main()
