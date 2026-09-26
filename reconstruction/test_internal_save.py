import json
import tempfile
import unittest
from dataclasses import replace
from datetime import date
from pathlib import Path

from game_state import GameState
from human_gameplay import HumanGameplayController
from internal_save import (
    SAVE_SCHEMA_VERSION,
    dumps_human_gameplay,
    loads_human_gameplay,
    restore_human_gameplay,
    save_human_gameplay,
    load_human_gameplay,
    snapshot_human_gameplay,
)
from match_schedule import MsvcCrtRng
from test_human_gameplay import Database, coefficient_matrix


SCHEDULER_ORDER = (
    (0, (5, 6, 7, 8, 9, 0, 1, 2, 3, 4)),
    (1, (15, 16, 17, 18, 19, 10, 11, 12, 13, 14)),
    (2, (25, 26, 27, 28, 29, 20, 21, 22, 23, 24)),
)


class InternalSaveTests(unittest.TestCase):
    def build_controller(self):
        state = GameState.from_database(
            Database(),
            date(2000, 6, 30),
            seed=1,
            season_year=2000,
        )
        state.install_premier_league_scheduler_order(SCHEDULER_ORDER)
        controller = HumanGameplayController(
            state,
            coefficient_matrix(),
            coefficient_matrix(),
            MsvcCrtRng(0x12345678),
        )
        controller.select_club(1)
        controller.autofill_lineup(0)
        return controller

    def test_json_roundtrip_preserves_mid_matchday_controller_state(self):
        original = self.build_controller()
        fixture = original.advance_to_next_user_fixture()
        self.assertEqual(fixture.id, 0)
        self.assertEqual(original.pending_fixture_id, 0)
        self.assertEqual(
            tuple(sorted(original.state.premier_league.results)),
            (5, 6, 7, 8, 9),
        )

        text = dumps_human_gameplay(original)
        decoded = json.loads(text)
        self.assertEqual(decoded["schema_version"], SAVE_SCHEMA_VERSION)

        restored = loads_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            text,
        )
        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_save_reload_branch_continues_identically_across_multiple_matchdays(self):
        original = self.build_controller()
        original.advance_to_next_user_fixture()
        snapshot = snapshot_human_gameplay(original)
        restored = restore_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            snapshot,
        )

        for expected_fixture_id in (0, 10, 20):
            if original.pending_fixture_id is None:
                original.autofill_lineup(0)
                restored.autofill_lineup(0)
                self.assertEqual(
                    original.advance_to_next_user_fixture().id,
                    expected_fixture_id,
                )
                self.assertEqual(
                    restored.advance_to_next_user_fixture().id,
                    expected_fixture_id,
                )
            else:
                self.assertEqual(original.pending_fixture_id, expected_fixture_id)
                self.assertEqual(restored.pending_fixture_id, expected_fixture_id)

            left = original.play_user_fixture()
            right = restored.play_user_fixture()
            self.assertEqual(left.user_result, right.user_result)
            self.assertEqual(left.matchday_results, right.matchday_results)
            self.assertEqual(left.table, right.table)
            self.assertEqual(
                snapshot_human_gameplay(restored),
                snapshot_human_gameplay(original),
            )

        self.assertEqual(len(original.state.premier_league.results), 30)
        self.assertEqual(len(restored.state.premier_league.results), 30)

    def test_gzip_file_roundtrip_preserves_state(self):
        original = self.build_controller()
        original.advance_to_next_user_fixture()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "gate8.fm2k"
            save_human_gameplay(original, path)
            self.assertEqual(path.read_bytes()[:2], b"\x1f\x8b")
            restored = load_human_gameplay(
                Database(),
                coefficient_matrix(),
                coefficient_matrix(),
                path,
            )

        self.assertEqual(
            snapshot_human_gameplay(restored),
            snapshot_human_gameplay(original),
        )

    def test_source_signature_ignores_live_skill_changes_but_binds_source_identity(self):
        original = self.build_controller()
        original.state.players[1000].current_raw[0] += 1
        snapshot = snapshot_human_gameplay(original)

        restored = restore_human_gameplay(
            Database(),
            coefficient_matrix(),
            coefficient_matrix(),
            snapshot,
        )
        self.assertEqual(
            restored.state.players[1000].current_raw[0],
            original.state.players[1000].current_raw[0],
        )

        class AlteredDatabase(Database):
            players = [
                replace(player, surname="Changed") if player.index == 1000 else player
                for player in Database.players
            ]

        with self.assertRaisesRegex(ValueError, "source database"):
            restore_human_gameplay(
                AlteredDatabase(),
                coefficient_matrix(),
                coefficient_matrix(),
                snapshot,
            )

    def test_wrong_source_database_is_rejected(self):
        original = self.build_controller()
        snapshot = snapshot_human_gameplay(original)

        class WrongDatabase(Database):
            players = Database.players[:-1]

        with self.assertRaisesRegex(ValueError, "source database"):
            restore_human_gameplay(
                WrongDatabase(),
                coefficient_matrix(),
                coefficient_matrix(),
                snapshot,
            )

    def test_unknown_schema_is_rejected(self):
        original = self.build_controller()
        snapshot = snapshot_human_gameplay(original)
        snapshot["schema_version"] = 999

        with self.assertRaisesRegex(ValueError, "unsupported internal save schema"):
            restore_human_gameplay(
                Database(),
                coefficient_matrix(),
                coefficient_matrix(),
                snapshot,
            )


if __name__ == "__main__":
    unittest.main()
