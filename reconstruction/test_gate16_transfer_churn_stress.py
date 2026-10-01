"""Gate-16 long-duration autonomous transfer churn stress.

This is deliberately synthetic work-ahead. It exercises the recovered Saturday
AI acquisition machinery for five years without claiming that the unresolved
country transfer-window dates or club +0x1ED buy-counter reset lifecycle match
the original game's long-term market frequency.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from types import SimpleNamespace
import unittest

from game_state import GameState
from match_schedule import MsvcCrtRng
from runtime_state import RuntimePlayer
from test_ai_transfers import financial_rows


CLUB_IDS = tuple(range(1, 21))
PLAYERS_PER_CLUB = 26
TOTAL_PLAYERS = len(CLUB_IDS) * PLAYERS_PER_CLUB
START_DATE = date(2000, 8, 19)  # Saturday
WEEKS = 260


def _player(club_id: int, offset: int) -> RuntimePlayer:
    player_id = club_id * 1000 + offset
    return RuntimePlayer(
        index=player_id,
        first_name=f"P{player_id}",
        surname="Stress",
        club_id=club_id,
        nationality_id=0,
        date_of_birth=date(1975 + (offset % 5), 1, 1),
        shirt_number=offset + 1,
        height_cm=180,
        weight_kg=75,
        positions=(0, 0, 0),
        current_raw=[128] * 17,
        target_raw=(128,) * 17,
        development=None,
        current_position=0,
        current_club_join_date=date(1999, 1, 1),
        contract_expiry_date=date(2010, 1, 1),
    )


def _build_state(seed: int) -> GameState:
    players = tuple(
        _player(club_id, offset)
        for club_id in CLUB_IDS
        for offset in range(PLAYERS_PER_CLUB)
    )
    state = GameState.from_players(players, START_DATE)
    state.clubs = {
        club_id: SimpleNamespace(
            index=club_id,
            name=f"Club {club_id}",
            manager_id=club_id,
            competition_id=0,
            country_id=0,
            team_category_code=0,
            fan_base_index=22,
            related_club_id_0=-1,
            related_club_id_1=-1,
            related_club_id_2=-1,
        )
        for club_id in CLUB_IDS
    }
    state.managers = {
        club_id: SimpleNamespace(index=club_id, club_id=club_id)
        for club_id in CLUB_IDS
    }
    state.competitions = {
        0: SimpleNamespace(id=0, valuation_division_category=0)
    }
    state.countries = {
        0: SimpleNamespace(
            id=0,
            financial_multiplier_percent=100,
            eu_status_flag=1,
        )
    }
    state.positions = {0: SimpleNamespace(lineup_group=0)}
    # seller threshold = field_48 - 4 = 16.
    state.access_fan_bases = tuple(
        SimpleNamespace(field_48=20)
        for _ in range(23)
    )
    state.access_skill_financial_values = financial_rows()
    state.country_transfer_window_open = {0: True}
    state.user_controlled_club_id = None
    state.rng = MsvcCrtRng(int(seed))
    return state


def _assert_roster_integrity(testcase: unittest.TestCase, state: GameState) -> None:
    roster_ids = []
    for club_id in CLUB_IDS:
        roster = tuple(state.club_roster_order.get(club_id, ()))
        testcase.assertGreaterEqual(
            len(roster),
            16,
            f"club {club_id} fell through the recovered seller roster floor",
        )
        # This is intentionally a generous corruption guard, not an assertion
        # about authentic transfer frequency while +0x1ED reset timing is open.
        testcase.assertLessEqual(
            len(roster),
            40,
            f"club {club_id} roster grew without a plausible bound",
        )
        for player_id in roster:
            testcase.assertEqual(
                int(state.players[int(player_id)].club_id),
                club_id,
                f"player {player_id} roster ownership disagrees with runtime club",
            )
        roster_ids.extend(int(value) for value in roster)

    testcase.assertEqual(len(roster_ids), TOTAL_PLAYERS)
    testcase.assertEqual(len(set(roster_ids)), TOTAL_PLAYERS)
    testcase.assertEqual(set(roster_ids), set(state.players))


def _stress_signature(seed: int):
    state = _build_state(seed)
    successful = 0

    for _week in range(WEEKS):
        if state.calendar.current_date.weekday() != 5:
            raise AssertionError("transfer churn fixture drifted away from Saturday")

        results = tuple(state.run_weekly_ai_transfer_maintenance())
        successful += len(results)

        # Direct autonomous acquisition must not leak proposal/deal scheduling
        # state. Completed movement history is expected to grow exactly once per
        # successful acquisition.
        if state.transfers.proposals:
            raise AssertionError("autonomous transfer leaked pending proposals")
        if state.transfers.deals:
            raise AssertionError("autonomous transfer leaked deals in progress")
        if state.transfers.bid_log:
            raise AssertionError("autonomous transfer leaked bid-log entries")
        if state.transfers.scheduled_transfers:
            raise AssertionError("autonomous transfer leaked scheduled transfers")
        if len(state.transfers.movements) != successful:
            raise AssertionError("movement history is not one record per acquisition")

        _assert_roster_integrity(_StressAsserts(), state)
        state.calendar.current_date += timedelta(days=7)

    movements = tuple(
        (
            item.movement_date.isoformat(),
            int(item.player_id),
            int(item.from_club_id),
            int(item.to_club_id),
            int(item.consideration),
        )
        for item in state.transfers.movements
    )
    move_counts = Counter(int(item.player_id) for item in state.transfers.movements)

    return {
        "successful": successful,
        "movements": movements,
        "move_counts": tuple(sorted(move_counts.items())),
        "rosters": tuple(
            (club_id, tuple(int(v) for v in state.club_roster_order[club_id]))
            for club_id in CLUB_IDS
        ),
        "counters": tuple(
            sorted(
                (int(club_id), int(value))
                for club_id, value in state.ai_transfer_buy_counter.items()
            )
        ),
        "rng_state": int(state.rng.state) & 0xFFFFFFFF,
        "final_date": state.calendar.current_date.isoformat(),
    }


class _StressAsserts(unittest.TestCase):
    """Assertion helper used inside the pure signature runner."""

    def runTest(self):
        pass


class Gate16TransferChurnStressTests(unittest.TestCase):
    def test_five_year_ai_transfer_churn_preserves_bounded_runtime_state(self):
        result = _stress_signature(0x12345678)

        self.assertGreater(
            result["successful"],
            0,
            "five-year stress never exercised a completed autonomous transfer",
        )
        self.assertEqual(len(result["movements"]), result["successful"])

        previous_date = None
        for movement_date, _player_id, from_club, to_club, consideration in result[
            "movements"
        ]:
            current = date.fromisoformat(movement_date)
            self.assertEqual(current.weekday(), 5)
            if previous_date is not None:
                self.assertGreaterEqual(current, previous_date)
            previous_date = current
            self.assertNotEqual(from_club, to_club)
            self.assertGreater(consideration, 0)

        # 0x40DBB0 requires >26 weeks at the current club. Across 260 weekly
        # passes, no player can therefore move more than ten times.
        self.assertTrue(
            all(count <= 10 for _player_id, count in result["move_counts"])
        )
        self.assertEqual(
            result["final_date"],
            (START_DATE + timedelta(days=7 * WEEKS)).isoformat(),
        )

    def test_transfer_churn_is_repeatable_for_same_crt_seed(self):
        first = _stress_signature(0x0BADF00D)
        second = _stress_signature(0x0BADF00D)
        self.assertEqual(first, second)

    def test_distinct_seed_also_survives_five_year_transfer_churn(self):
        result = _stress_signature(0xDEADBEEF)
        self.assertGreater(result["successful"], 0)
        self.assertEqual(len(result["movements"]), result["successful"])


if __name__ == "__main__":
    unittest.main()
