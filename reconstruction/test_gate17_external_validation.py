import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from gate17_external_validation import (
    ExternalReleaseValidationError,
    preflight_external_release_validation,
    run_external_release_validation,
)
from gate17_release_readiness import ReleaseReadinessError


COMMIT = "a" * 40
VERSION = "rc-final"


def ready_implementation_preflight():
    return SimpleNamespace(
        ready_for_full_runtime_validation=True,
        blocker_codes=(),
    )


def blocked_implementation_preflight():
    return SimpleNamespace(
        ready_for_full_runtime_validation=False,
        blocker_codes=(
            "runtime_owner_capability_incomplete",
            "save_scope_capability_incomplete",
            "multi_human_capability_incomplete",
        ),
    )


class Gate17ExternalValidationTests(unittest.TestCase):
    def _paths(self, temp):
        root = Path(temp)
        repo = root / "repo"
        repo.mkdir()
        game = root / "FM2001"
        game.mkdir()
        archive = root / "release.zip"
        archive.write_bytes(b"candidate")
        scope = root / "full_original_scope.json"
        scope.write_text("{}", encoding="utf-8")
        work = root / "external-validation"
        return repo, game, archive, scope, work

    def test_preflight_checks_prerequisites_before_creating_work_root(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, game, archive, scope, work = self._paths(temp)
            with (
                patch(
                    "gate17_external_validation.require_external_windows_11_workstation",
                    return_value={
                        "windows_11": True,
                        "windows_build": 26200,
                        "windows_product_type": 1,
                    },
                ),
                patch(
                    "gate17_external_validation.validate_clean_repository",
                    return_value={"working_tree_clean": True},
                ),
                patch(
                    "gate17_external_validation.validate_roadmap_prerequisites",
                    side_effect=ReleaseReadinessError("Gate 13 (1 unchecked)"),
                ),
                patch(
                    "gate17_external_validation.validate_limitations_document"
                ) as limitations,
            ):
                with self.assertRaisesRegex(
                    ReleaseReadinessError,
                    "Gate 13",
                ):
                    preflight_external_release_validation(
                        repo_root=repo,
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        canonical_game_dir=game,
                        full_original_scope_receipt=scope,
                        work_root=work,
                    )

            limitations.assert_not_called()
            self.assertFalse(work.exists())

    def test_preflight_requires_existing_external_full_scope_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, game, archive, scope, work = self._paths(temp)
            scope.unlink()
            with (
                patch(
                    "gate17_external_validation.require_external_windows_11_workstation",
                    return_value={
                        "windows_11": True,
                        "windows_build": 26200,
                        "windows_product_type": 1,
                    },
                ),
                patch(
                    "gate17_external_validation.validate_clean_repository",
                    return_value={"working_tree_clean": True},
                ),
                patch(
                    "gate17_external_validation.validate_roadmap_prerequisites",
                    return_value={"all_prerequisites_complete": True},
                ),
                patch(
                    "gate17_external_validation.validate_limitations_document",
                    return_value={"path": "research/RELEASE_LIMITATIONS.md"},
                ),
                patch(
                    "gate17_external_validation.resolve_release_artifact_identity",
                    return_value=SimpleNamespace(
                        release_version=VERSION,
                        repository_commit=COMMIT,
                    ),
                ),
            ):
                with self.assertRaisesRegex(
                    ExternalReleaseValidationError,
                    "full original scope receipt does not exist",
                ):
                    preflight_external_release_validation(
                        repo_root=repo,
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        canonical_game_dir=game,
                        full_original_scope_receipt=scope,
                        work_root=work,
                    )
            self.assertFalse(work.exists())

    def test_preflight_rejects_incomplete_canonical_full_scope_before_work_root(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, game, archive, scope, work = self._paths(temp)
            with (
                patch(
                    "gate17_external_validation.require_external_windows_11_workstation",
                    return_value={
                        "windows_11": True,
                        "windows_build": 26200,
                        "windows_product_type": 1,
                    },
                ),
                patch(
                    "gate17_external_validation.validate_clean_repository",
                    return_value={"working_tree_clean": True},
                ),
                patch(
                    "gate17_external_validation.validate_roadmap_prerequisites",
                    return_value={"all_prerequisites_complete": True},
                ),
                patch(
                    "gate17_external_validation.validate_limitations_document",
                    return_value={"path": "research/RELEASE_LIMITATIONS.md"},
                ),
                patch(
                    "gate17_external_validation.resolve_release_artifact_identity",
                    return_value=SimpleNamespace(
                        release_version=VERSION,
                        repository_commit=COMMIT,
                    ),
                ),
                patch(
                    "gate17_external_validation.run_canonical_full_scope_preflight",
                    return_value=blocked_implementation_preflight(),
                ) as implementation,
                patch(
                    "gate17_external_validation.run_clean_windows_install_receipt"
                ) as clean,
            ):
                with self.assertRaisesRegex(
                    ExternalReleaseValidationError,
                    "canonical full-scope implementation preflight is not ready",
                ):
                    preflight_external_release_validation(
                        repo_root=repo,
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        canonical_game_dir=game,
                        full_original_scope_receipt=scope,
                        work_root=work,
                    )

            implementation.assert_called_once_with(
                game.resolve(),
                player_seed=1,
                max_days=420,
            )
            clean.assert_not_called()
            self.assertFalse(work.exists())

    def test_preflight_rejects_pre_release_limitations_before_receipts(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, game, archive, scope, work = self._paths(temp)
            with (
                patch(
                    "gate17_external_validation.require_external_windows_11_workstation",
                    return_value={"windows_11": True},
                ),
                patch(
                    "gate17_external_validation.validate_clean_repository",
                    return_value={"working_tree_clean": True},
                ),
                patch(
                    "gate17_external_validation.validate_roadmap_prerequisites",
                    return_value={"all_prerequisites_complete": True},
                ),
                patch(
                    "gate17_external_validation.validate_limitations_document",
                    side_effect=ReleaseReadinessError("pre-release"),
                ),
                patch(
                    "gate17_external_validation.run_clean_windows_install_receipt"
                ) as clean,
            ):
                with self.assertRaisesRegex(ReleaseReadinessError, "pre-release"):
                    run_external_release_validation(
                        repo_root=repo,
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        canonical_game_dir=game,
                        full_original_scope_receipt=scope,
                        work_root=work,
                    )

            clean.assert_not_called()
            self.assertFalse(work.exists())

    def test_success_runs_one_archive_identity_through_complete_transaction(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, game, archive, scope, work = self._paths(temp)
            receipts = work / "receipts"
            clean_path = receipts / "clean_windows_install.json"
            management_path = receipts / "new_game_management_loop.json"
            season_path = receipts / "season_progression.json"
            save_path = receipts / "save_reload.json"
            evidence_path = work / "release-evidence.json"

            def clean_runner(**kwargs):
                Path(kwargs["output_dir"]).mkdir(parents=True, exist_ok=True)
                clean_path.write_text("{}", encoding="utf-8")
                return clean_path

            def gameplay_runner(**kwargs):
                Path(kwargs["output_dir"]).mkdir(parents=True, exist_ok=True)
                for path in (management_path, season_path, save_path):
                    path.write_text("{}", encoding="utf-8")
                return {
                    "new_game_management_loop": management_path,
                    "season_progression": season_path,
                    "save_reload": save_path,
                }

            def evidence_runner(**kwargs):
                Path(kwargs["output_path"]).write_text("{}", encoding="utf-8")
                return Path(kwargs["output_path"])

            with (
                patch(
                    "gate17_external_validation.require_external_windows_11_workstation",
                    return_value={
                        "windows_11": True,
                        "windows_build": 26200,
                        "windows_product_type": 1,
                    },
                ),
                patch(
                    "gate17_external_validation.validate_clean_repository",
                    return_value={"working_tree_clean": True},
                ),
                patch(
                    "gate17_external_validation.validate_roadmap_prerequisites",
                    return_value={"all_prerequisites_complete": True},
                ),
                patch(
                    "gate17_external_validation.validate_limitations_document",
                    return_value={"path": "research/RELEASE_LIMITATIONS.md"},
                ),
                patch(
                    "gate17_external_validation.resolve_release_artifact_identity",
                    return_value=SimpleNamespace(
                        release_version=VERSION,
                        repository_commit=COMMIT,
                    ),
                ),
                patch(
                    "gate17_external_validation.run_canonical_full_scope_preflight",
                    return_value=ready_implementation_preflight(),
                ) as implementation,
                patch(
                    "gate17_external_validation.run_clean_windows_install_receipt",
                    side_effect=clean_runner,
                ) as clean,
                patch(
                    "gate17_external_validation.run_windows_gameplay_receipts",
                    side_effect=gameplay_runner,
                ) as gameplay,
                patch(
                    "gate17_external_validation.assemble_release_evidence",
                    side_effect=evidence_runner,
                ) as evidence,
                patch(
                    "gate17_external_validation.run_final_release_audit",
                    return_value={
                        "schema_version": 1,
                        "passed": True,
                        "repository_commit": COMMIT,
                    },
                ) as final_audit,
            ):
                result = run_external_release_validation(
                    repo_root=repo,
                    release_version=VERSION,
                    repository_commit=COMMIT,
                    release_archive=archive,
                    canonical_game_dir=game,
                    full_original_scope_receipt=scope,
                    work_root=work,
                    player_seed=7,
                    max_days=430,
                )

            self.assertTrue(work.is_dir())
            implementation.assert_called_once_with(
                game.resolve(),
                player_seed=7,
                max_days=430,
            )
            final_payload = json.loads(
                result["final_release_receipt"].read_text(encoding="utf-8")
            )
            self.assertTrue(final_payload["passed"])
            self.assertEqual(final_payload["repository_commit"], COMMIT)
            self.assertEqual(
                result["release_evidence"].resolve(),
                evidence_path.resolve(),
            )
            self.assertEqual(clean.call_args.kwargs["release_archive"], archive.resolve())
            self.assertEqual(gameplay.call_args.kwargs["release_archive"], archive.resolve())
            self.assertEqual(gameplay.call_args.kwargs["player_seed"], 7)
            self.assertEqual(gameplay.call_args.kwargs["max_days"], 430)
            self.assertEqual(evidence.call_args.kwargs["release_archive"], archive.resolve())
            self.assertEqual(
                evidence.call_args.kwargs["receipt_paths"]["full_original_scope"],
                scope.resolve(),
            )
            self.assertEqual(result["full_original_scope"], scope.resolve())
            self.assertEqual(final_audit.call_args.kwargs["release_archive"], archive.resolve())

    def test_late_failure_removes_all_partial_external_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, game, archive, scope, work = self._paths(temp)

            def clean_runner(**kwargs):
                output = Path(kwargs["output_dir"])
                output.mkdir(parents=True, exist_ok=True)
                path = output / "clean_windows_install.json"
                path.write_text("partial", encoding="utf-8")
                return path

            with (
                patch(
                    "gate17_external_validation.require_external_windows_11_workstation",
                    return_value={"windows_11": True},
                ),
                patch(
                    "gate17_external_validation.validate_clean_repository",
                    return_value={"working_tree_clean": True},
                ),
                patch(
                    "gate17_external_validation.validate_roadmap_prerequisites",
                    return_value={"all_prerequisites_complete": True},
                ),
                patch(
                    "gate17_external_validation.validate_limitations_document",
                    return_value={"path": "research/RELEASE_LIMITATIONS.md"},
                ),
                patch(
                    "gate17_external_validation.resolve_release_artifact_identity",
                    return_value=SimpleNamespace(
                        release_version=VERSION,
                        repository_commit=COMMIT,
                    ),
                ),
                patch(
                    "gate17_external_validation.run_canonical_full_scope_preflight",
                    return_value=ready_implementation_preflight(),
                ) as implementation,
                patch(
                    "gate17_external_validation.run_clean_windows_install_receipt",
                    side_effect=clean_runner,
                ),
                patch(
                    "gate17_external_validation.run_windows_gameplay_receipts",
                    side_effect=RuntimeError("season progression failed"),
                ),
            ):
                with self.assertRaisesRegex(RuntimeError, "season progression"):
                    run_external_release_validation(
                        repo_root=repo,
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        canonical_game_dir=game,
                        full_original_scope_receipt=scope,
                        work_root=work,
                    )

            implementation.assert_called_once_with(
                game.resolve(),
                player_seed=1,
                max_days=420,
            )
            self.assertFalse(work.exists())

    def test_work_root_and_canonical_game_data_must_remain_outside_repo(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / "repo"
            repo.mkdir()
            archive = root / "release.zip"
            archive.write_bytes(b"x")
            inside_game = repo / "game"
            inside_game.mkdir()

            with (
                patch(
                    "gate17_external_validation.require_external_windows_11_workstation",
                    return_value={"windows_11": True},
                ),
                patch(
                    "gate17_external_validation.validate_clean_repository",
                    return_value={"working_tree_clean": True},
                ),
                patch(
                    "gate17_external_validation.validate_roadmap_prerequisites",
                    return_value={"all_prerequisites_complete": True},
                ),
                patch(
                    "gate17_external_validation.validate_limitations_document",
                    return_value={"path": "research/RELEASE_LIMITATIONS.md"},
                ),
                patch(
                    "gate17_external_validation.resolve_release_artifact_identity",
                    return_value=SimpleNamespace(
                        release_version=VERSION,
                        repository_commit=COMMIT,
                    ),
                ),
            ):
                with self.assertRaisesRegex(
                    ExternalReleaseValidationError,
                    "outside the Git repository",
                ):
                    preflight_external_release_validation(
                        repo_root=repo,
                        release_version=VERSION,
                        repository_commit=COMMIT,
                        release_archive=archive,
                        canonical_game_dir=inside_game,
                        full_original_scope_receipt=root / "scope.json",
                        work_root=root / "work",
                    )


if __name__ == "__main__":
    unittest.main()
