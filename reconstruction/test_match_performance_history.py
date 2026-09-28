import unittest
from datetime import date

from match_schedule import MsvcCrtRng
from runtime_state import RuntimePlayer
from test_runtime_state import FakePlayer


class MatchPerformanceHistoryTests(unittest.TestCase):
    def build_player(self) -> RuntimePlayer:
        return RuntimePlayer.from_database_player(
            FakePlayer(),
            date(2000, 7, 1),
            MsvcCrtRng(1),
        )

    def test_fresh_history_matches_original_zero_state(self):
        player = self.build_player()

        self.assertEqual(player.match_performance_history, [0] * 6)
        self.assertEqual(player.match_performance_history_count, 0)
        self.assertEqual(player.match_performance_history_write_index, 0)
        self.assertEqual(player.match_performance_average(), 0.0)

    def test_positive_values_fill_then_wrap_exact_six_entry_ring(self):
        player = self.build_player()

        for value in (6, 7, 8, 9, 10, 5):
            self.assertEqual(player.append_match_performance(value), value)

        self.assertEqual(player.match_performance_history, [6, 7, 8, 9, 10, 5])
        self.assertEqual(player.match_performance_history_count, 6)
        self.assertEqual(player.match_performance_history_write_index, 0)
        self.assertEqual(player.match_performance_average(), 7.5)

        player.append_match_performance(4)
        self.assertEqual(player.match_performance_history, [4, 7, 8, 9, 10, 5])
        self.assertEqual(player.match_performance_history_count, 6)
        self.assertEqual(player.match_performance_history_write_index, 1)
        self.assertAlmostEqual(player.match_performance_average(), 43 / 6)

    def test_nonpositive_values_do_not_mutate_history(self):
        player = self.build_player()

        self.assertEqual(player.append_match_performance(0), 0)
        self.assertEqual(player.append_match_performance(-3), -3)
        self.assertEqual(player.match_performance_history, [0] * 6)
        self.assertEqual(player.match_performance_history_count, 0)
        self.assertEqual(player.match_performance_history_write_index, 0)


if __name__ == "__main__":
    unittest.main()
