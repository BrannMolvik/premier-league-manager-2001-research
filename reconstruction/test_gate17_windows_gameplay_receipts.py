import json
import tempfile
import unittest
from datetime import date
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from gate17_windows_gameplay_receipts import (
    ReleaseArtifactIdentity,
    WindowsGameplayReceiptError,
    _receipt_payload,
    audit_new_game_management_loop,
    audit_save_reload,
    audit_season_progression,
    require_output_directory_outside_repo,
    resolve_release_artifact_identity,
    run_windows_gameplay_receipts,
    write_new_receipt,
)


COMMIT = "a" * 40


class FakeManagementController:
    def __init__(self):
        self.state = SimpleNamespace(
            premier_league=SimpleNamespace(
                club_ids=(7, 8),
                results={},
            ),
            calendar=SimpleNamespace(current_date=date(2000, 8, 19)),
        )
        self.pending_fixture_id = None
        self.selected_club_id = None
        self.attack_matrix = object()
        self.defence_matrix = object()

    def select_club(self, club_id):
        self.selected_club_id = int(club_id)

    def autofill_lineup(self, formation_id):
        starters = tuple(
            SimpleNamespace(player_index=index)
            for index in range(11)
        )
        substitutes = tuple(range(11, 16))
        return SimpleNamespace(
            lineup=SimpleNamespace(
                starters=starters,
                substitutes=substitutes,
            )
        )

    def advance_to_next_user_fixture(self):
        self.pending_fixture_id = 42
        return SimpleNamespace(id=42)

    def play_user_fixture(self):
        self.state.premier_league.results[42] = object()
        self.pending_fixture_id = None
        return SimpleNamespace(
            fixture_id=42,
            matchday_results=tuple((index, object()) for index in range(10)),
        )


class Gate17WindowsGameplayReceiptTests(unittest.TestCase):
    def test_release_artifact_identity_hashes_exact_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "release.zip"
            archive.write_bytes(b"release-candidate")

            identity = resolve_release_artifact_identity(
                release_version="v0.17.0",
                repository_commit=COMMIT,
                release_archive=archive,
            )

            self.assertEqual(identity.release_version, "v0.17.0")
            self.assertEqual(identity.repository_commit, COMMIT)
            self.assertEqual(
                identity.release_archive_sha256,
                sha256(b"release-candidate").hexdigest(),
            )
            self.assertEqual(identity.release_archive_size, len(b"release-candidate"))

    def test_release_artifact_identity_rejects_bad_commit_and_missing_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "release.zip"
            archive.write_bytes(b"x")
            with self.assertRaisesRegex(
                WindowsGameplayReceiptError,
                "40-character Git SHA",
            ):
                resolve_release_artifact_identity(
                    release_version="v1",
                    repository_commit="not-a-commit",
                    release_archive=archive,
                )
            with self.assertRaisesRegex(
                WindowsGameplayReceiptError,
                "does not exist",
            ):
                resolve_release_artifact_identity(
                    release_version="v1",
                    repository_commit=COMMIT,
                    release_archive=Path(temp) / "missing.zip",
                )

    def test_new_game_management_loop_requires_real_persisted_match(self):
        controller = FakeManagementController()

        result = audit_new_game_management_loop(controller)

        self.assertTrue(result["new_game"])
        self.assertTrue(result["management_loop"])
        self.assertEqual(result["selected_club_id"], 7)
        self.assertEqual(result["starter_count"], 11)
        self.assertEqual(result["substitute_count"], 5)
        self.assertEqual(result["played_fixture_id"], 42)
        self.assertEqual(result["matchday_result_count"], 10)
        self.assertIn(42, controller.state.premier_league.results)

    def test_save_reload_compares_exact_internal_snapshot(self):
        controller = FakeManagementController()
        expected = {
            "schema_version": 34,
            "controller": {"human": {"club_id": 7}},
        }
        restored = SimpleNamespace(
            state=SimpleNamespace(
                calendar=SimpleNamespace(current_date=date(2000, 8, 19)),
                premier_league=SimpleNamespace(results={42: object()}),
            )
        )

        def fake_save(_controller, path):
            Path(path).write_bytes(b"saved")
            return Path(path)

        with (
            patch(
                "gate17_windows_gameplay_receipts.FM2001Database",
                return_value=object(),
            ),
            patch(
                "gate17_windows_gameplay_receipts.save_human_gameplay",
                side_effect=fake_save,
            ),
            patch(
                "gate17_windows_gameplay_receipts.load_human_gameplay",
                return_value=restored,
            ),
            patch(
                "gate17_windows_gameplay_receipts.snapshot_human_gameplay",
                side_effect=(expected, expected),
            ),
        ):
            result = audit_save_reload("C:/FM2001", controller)

        self.assertTrue(result["save_reload"])
        self.assertEqual(result["schema_version"], 34)
        self.assertEqual(result["restored_result_count"], 1)

    def test_save_reload_rejects_snapshot_drift(self):
        controller = FakeManagementController()
        restored = SimpleNamespace(
            state=SimpleNamespace(
                calendar=SimpleNamespace(current_date=date(2000, 8, 19)),
                premier_league=SimpleNamespace(results={}),
            )
        )

        def fake_save(_controller, path):
            Path(path).write_bytes(b"saved")
            return Path(path)

        with (
            patch(
                "gate17_windows_gameplay_receipts.FM2001Database",
                return_value=object(),
            ),
            patch(
                "gate17_windows_gameplay_receipts.save_human_gameplay",
                side_effect=fake_save,
            ),
            patch(
                "gate17_windows_gameplay_receipts.load_human_gameplay",
                return_value=restored,
            ),
            patch(
                "gate17_windows_gameplay_receipts.snapshot_human_gameplay",
                side_effect=(
                    {"schema_version": 34, "value": 1},
                    {"schema_version": 34, "value": 2},
                ),
            ),
        ):
            with self.assertRaisesRegex(
                WindowsGameplayReceiptError,
                "exact gameplay snapshot",
            ):
                audit_save_reload("C:/FM2001", controller)

    def test_season_progression_reuses_canonical_annual_rollover(self):
        canonical = {
            "player_seed": 3,
            "days_advanced": 350,
            "qualification_captured_on": "2001-06-20",
            "rollover_season_year": 2001,
            "year_two_premier_fixture_count": 380,
            "year_two_primary_order_days": 120,
            "rollover_total_draw_count": 9876,
        }
        with patch(
            "gate17_windows_gameplay_receipts.run_canonical_annual_rollover_audit",
            return_value=canonical,
        ) as runner:
            result = audit_season_progression(
                "C:/FM2001",
                player_seed=3,
                max_days=420,
            )

        runner.assert_called_once_with(
            "C:/FM2001",
            player_seed=3,
            max_days=420,
        )
        self.assertTrue(result["season_progression"])
        self.assertEqual(result["year_two_premier_fixture_count"], 380)

    def test_receipt_directory_must_be_outside_repo_and_never_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            with self.assertRaisesRegex(
                WindowsGameplayReceiptError,
                "outside Git",
            ):
                require_output_directory_outside_repo(
                    repo / "receipts",
                    repo_root=repo,
                )

            outside = require_output_directory_outside_repo(
                Path(temp) / "private-receipts",
                repo_root=repo,
            )
            payload = {"passed": True}
            path = write_new_receipt(outside / "smoke.json", payload)
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                payload,
            )
            with self.assertRaisesRegex(
                WindowsGameplayReceiptError,
                "do not overwrite",
            ):
                write_new_receipt(path, payload)

    def test_receipt_set_writes_nothing_when_late_season_audit_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()
            output = Path(temp) / "receipts"
            archive = Path(temp) / "release.zip"
            archive.write_bytes(b"candidate")

            with (
                patch(
                    "gate17_windows_gameplay_receipts.require_external_windows_11_workstation",
                    return_value={"platform": "Windows-11", "windows_build": 26200},
                ),
                patch(
                    "gate17_windows_gameplay_receipts.HumanGameplayController.from_canonical_game_dir",
                    return_value=object(),
                ),
                patch(
                    "gate17_windows_gameplay_receipts.audit_new_game_management_loop",
                    return_value={"new_game": True, "management_loop": True},
                ),
                patch(
                    "gate17_windows_gameplay_receipts.audit_save_reload",
                    return_value={"save_reload": True},
                ),
                patch(
                    "gate17_windows_gameplay_receipts.audit_season_progression",
                    side_effect=WindowsGameplayReceiptError("season failed"),
                ),
            ):
                with self.assertRaisesRegex(
                    WindowsGameplayReceiptError,
                    "season failed",
                ):
                    run_windows_gameplay_receipts(
                        game_dir="C:/FM2001",
                        release_version="v0.17.0",
                        repository_commit=COMMIT,
                        release_archive=archive,
                        output_dir=output,
                        repo_root=repo,
                    )

            self.assertEqual(tuple(output.glob("*.json")), ())

    def test_receipt_payload_carries_exact_release_identity(self):
        identity = ReleaseArtifactIdentity(
            release_version="v0.17.0",
            repository_commit=COMMIT,
            release_archive_sha256="b" * 64,
            release_archive_size=123,
        )
        payload = _receipt_payload(
            audit_kind="gate17_save_reload",
            identity=identity,
            windows={"platform": "Windows-11", "windows_build": 26200},
            result={"save_reload": True},
        )
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["repository_commit"], COMMIT)
        self.assertEqual(payload["release_version"], "v0.17.0")
        self.assertEqual(payload["release_archive_sha256"], "b" * 64)
        self.assertEqual(payload["release_archive_size"], 123)
        self.assertTrue(payload["save_reload"])


if __name__ == "__main__":
    unittest.main()
