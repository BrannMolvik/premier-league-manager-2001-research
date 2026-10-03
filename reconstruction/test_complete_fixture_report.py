"""Synthetic complete-contract tests; NOT a genuine native production proof."""
import unittest
from dataclasses import replace
from datetime import date
from types import SimpleNamespace

from complete_fixture_report import *
from game_state import GameState
from gate13_management_source_data import ManagementSourceDataBridge
from internal_save import snapshot_game_state, restore_game_state
from match_postmatch import FinalizedParticipantStatistics
from native_compact_match import native_boundary
from test_human_gameplay import Database
from test_match_simulation import side, matrix, MidpointRng
import test_match_simulation as simulation_tests
from match_simulation import simulate_normal_match


def contract(fixture):
    sides = tuple(tuple(ReportParticipantMetadata(side * 100 + i, i, 0, 1)
                        for i in range(11)) for side in range(2))
    metadata = ReportMetadata(
        tuple(NativeCapturedScalar(d, s, bytes(n)) for d, s, n in NATIVE_CAPTURE_SCALAR_COPIES),
        b'Explicit synthetic contract', fixture.home_club_id,
        (fixture.home_club_id, fixture.away_club_id), (0, 0), sides, None)
    statistics = tuple(FinalizedSideParticipantStatistics(
        tuple(p.player_id for p in side),
        tuple(FinalizedParticipantStatistics(i, 6, bytes(8)) for i in range(11)))
        for side in sides)
    result = SimpleNamespace(
        native_completion_scalars=LiveReportCompletionScalars((100, 7, 1), (0, 0)),
        captured_possession=NativeCapturedPossession(bytes((50, 50, 50)) * 2, bytes((50, 50, 50))),
        native_compact_events=(native_boundary(45, 6), native_boundary(90, 7, outcome=0)))
    return metadata, statistics, result


class CompleteReportTests(unittest.TestCase):
    def setUp(self):
        self.database = Database()
        self.state = GameState.from_database(self.database, date(2000, 7, 1), seed=1, season_year=2000)
        self.fixture = next(iter(self.state.premier_league.fixtures.values()))
        self.metadata, self.statistics, self.result = contract(self.fixture)

    def publish(self):
        key = self.fixture.id
        self.state.prepared_match_report_metadata[key] = self.metadata
        self.state.prepared_match_participant_statistics[key] = self.statistics
        self.state.prepared_match_report_player_ids[key] = 0
        return self.state._publish_completed_fixture_report(key, self.result)

    def test_missing_each_input_never_publishes(self):
        self.assertFalse(self.state._publish_completed_fixture_report(self.fixture.id, self.result))
        for name in ('native_completion_scalars', 'captured_possession', 'native_compact_events'):
            with self.subTest(name=name):
                result = SimpleNamespace(**vars(self.result))
                setattr(result, name, None)
                self.assertIsNone(assemble_complete_fixture_report(
                    self.fixture.id, result, self.metadata, self.statistics, 0))
        self.assertEqual(self.state.captured_match_reports, ())
        self.assertEqual(self.state.fixture_match_info_links, {})

    def test_complete_contract_owner_save_reload_context(self):
        self.assertTrue(self.publish())
        restored = restore_game_state(self.database, snapshot_game_state(self.state))
        self.assertEqual(restored.captured_match_reports, self.state.captured_match_reports)
        self.assertEqual(restored.fixture_match_info_links, {self.fixture.id: 0})
        self.assertEqual(tuple(int.from_bytes(s.value, 'little')
                               for s in restored.captured_match_reports[0].helper_copies),
                         (100, 7, 1))
        context = ManagementSourceDataBridge(SimpleNamespace(state=restored)).fixture_match_info_context(self.fixture.id)
        self.assertIsNotNone(context)
        self.assertEqual(context.fixture_id, self.fixture.id)

    def test_owner_identity_and_partial_scalar_reject(self):
        with self.assertRaises(ValueError):
            replace(self.metadata, scalar_copies=())
        self.state.prepared_match_report_metadata[self.fixture.id] = replace(
            self.metadata, team_ids=tuple(reversed(self.metadata.team_ids)))
        self.state.prepared_match_participant_statistics[self.fixture.id] = self.statistics
        self.state.prepared_match_report_player_ids[self.fixture.id] = 0
        with self.assertRaises(ValueError):
            self.state._publish_completed_fixture_report(self.fixture.id, self.result)
        self.assertEqual(self.state.captured_match_reports, ())
        self.assertEqual(self.state.fixture_match_info_links, {})

    def test_duplicate_and_corrupt_link_reject(self):
        self.publish()
        saved = snapshot_game_state(self.state)
        saved['fixture_match_info_links'][0][1] = 1
        with self.assertRaises(ValueError):
            restore_game_state(self.database, saved)
        self.state.prepared_match_report_metadata[self.fixture.id] = self.metadata
        with self.assertRaises(ValueError):
            self.state._publish_completed_fixture_report(self.fixture.id, self.result)

    def test_incomplete_save_rejects_not_defaulted(self):
        self.publish()
        saved = snapshot_game_state(self.state)
        del saved['captured_match_reports'][0]['calendar']
        with self.assertRaises(ValueError):
            restore_game_state(self.database, saved)

    def test_packed_script_corruption_rejects(self):
        self.publish()
        saved = snapshot_game_state(self.state)
        saved['captured_match_reports'][0]['script'] = '0200'
        with self.assertRaises(ValueError):
            restore_game_state(self.database, saved)

    def test_initial_history_is_retained_before_final_condition(self):
        lineup = simulation_tests.FullNormalMatchTests().lineup
        home = side(0, lineup(0), 10, user_controlled=True)
        away = side(1, lineup(1), 10, user_controlled=False)
        home.players[0].condition = 101
        away.players[0].condition = 100
        output = simulate_normal_match(home, away, matrix(), matrix(), MidpointRng(),
                                       discipline_enabled=False, native_ai_condition_adjustment=101)
        self.assertEqual(tuple(row for row in output.initial_report_condition_bits if row[1] == 0),
                         ((0, 0, 1), (1, 0, 1)))
        self.assertEqual(tuple(row for row in output.report_booking_bits if row[1] == 0),
                         ((0, 0, 0), (1, 0, 0)))
        # Byte wrap, not clamping at zero; human side does not subtract D48.
        home = side(0, lineup(0), 10)
        away = side(1, lineup(1), 10, user_controlled=False)
        output = simulate_normal_match(home, away, matrix(), matrix(), MidpointRng(), discipline_enabled=False)
        self.assertEqual(tuple(row for row in output.initial_report_condition_bits if row[1] == 0),
                         ((0, 0, 0), (1, 0, None)))

    def test_caption_requires_exact_loaded_language_and_context(self):
        language = (b'%C %D{%D %M %Yf}', (b'Jan', b'Feb', b'Mar', b'Apr', b'May', b'Jun',
                                        b'Jul', b'Aug', b'Sep', b'Oct', b'Nov', b'Dec'))
        self.assertEqual(format_report_caption(language, 'Explicit source context', date(2000, 7, 1)),
                         b'Explicit source context 1 Jul 2000')
        self.assertIsNone(format_report_caption(None, 'No guessed language', date(2000, 7, 1)))
        self.assertIsNone(format_report_caption(language, None, date(2000, 7, 1)))
        self.assertIsNone(format_report_caption(language, 'x' * 64, date(2000, 7, 1)))


if __name__ == '__main__':
    unittest.main()
