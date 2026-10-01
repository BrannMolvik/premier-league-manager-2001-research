"""Gate-16 cloud-safe multi-seed autonomous full-season stress."""
from datetime import date
from hashlib import sha256
import json
import unittest

from game_state import GameState
from match_schedule import MsvcCrtRng
from test_gate11_management_season import FullSeasonDatabase, coefficient_matrix


STRESS_SEEDS = (
    0x00000001,
    0x00000002,
    0x12345678,
    0x80000000,
    0xDEADBEEF,
    0xFFFFFFFF,
)


def _scheduler_order(state):
    return tuple(
        (
            round_index,
            tuple(
                int(fixture.id)
                for fixture in state.premier_league.fixtures_for_round(round_index)
            ),
        )
        for round_index in range(38)
    )


def _season_digest(state):
    payload = {
        "results": [
            [
                int(fixture_id),
                int(result.home_goals),
                int(result.away_goals),
            ]
            for fixture_id, result in sorted(state.premier_league.results.items())
        ],
        "table": [
            [
                int(row.club_id),
                int(row.played),
                int(row.wins),
                int(row.draws),
                int(row.losses),
                int(row.goals_for),
                int(row.goals_against),
                int(row.points),
            ]
            for row in state.premier_league_table()
        ],
        "players": [
            [
                int(player.index),
                int(player.club_id),
                int(player.condition),
                int(player.form_state),
                bool(player.injured),
                int(player.suspension_matches_remaining),
            ]
            for player in sorted(state.players.values(), key=lambda item: int(item.index))
        ],
    }
    return sha256(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("ascii")
    ).hexdigest()


def run_autonomous_season(seed):
    state = GameState.from_database(
        FullSeasonDatabase(),
        date(2000, 8, 18),
        seed=int(seed),
        season_year=2000,
    )
    state.install_premier_league_scheduler_order(_scheduler_order(state))
    attack = coefficient_matrix()
    defence = coefficient_matrix()
    rng = MsvcCrtRng(int(seed))
    days = 0

    while len(state.premier_league.results) < 380:
        days += 1
        if days > 366:
            raise AssertionError(
                f"seed 0x{int(seed):08X}: season did not finish within one year"
            )
        state.advance_one_day_with_premier_league_ai_fixtures(
            attack,
            defence,
            rng,
        )

    rows = state.premier_league_table()
    if len(rows) != 20:
        raise AssertionError(f"seed 0x{int(seed):08X}: expected 20 table rows")
    if any(int(row.played) != 38 for row in rows):
        raise AssertionError(f"seed 0x{int(seed):08X}: not every club played 38")
    if sum(int(row.played) for row in rows) != 760:
        raise AssertionError(f"seed 0x{int(seed):08X}: table played total diverged")
    if sum(int(row.goals_for) for row in rows) != sum(
        int(row.goals_against) for row in rows
    ):
        raise AssertionError(f"seed 0x{int(seed):08X}: goals do not reconcile")
    if sum(int(row.wins) for row in rows) != sum(int(row.losses) for row in rows):
        raise AssertionError(f"seed 0x{int(seed):08X}: wins/losses do not reconcile")

    for player in state.players.values():
        if not 0 <= int(player.condition) <= 100:
            raise AssertionError(
                f"seed 0x{int(seed):08X}: invalid condition for {player.index}"
            )
        if not 0 <= int(player.form_state) <= 4:
            raise AssertionError(
                f"seed 0x{int(seed):08X}: invalid form for {player.index}"
            )
        if int(player.suspension_matches_remaining) < 0:
            raise AssertionError(
                f"seed 0x{int(seed):08X}: negative suspension for {player.index}"
            )
        if player.injured and player.injury_return_date is None:
            raise AssertionError(
                f"seed 0x{int(seed):08X}: injured player lacks return date"
            )

    for club_id in state.premier_league.club_ids:
        roster = state.ordered_club_roster(int(club_id))
        if any(int(player.club_id) != int(club_id) for player in roster):
            raise AssertionError(
                f"seed 0x{int(seed):08X}: roster ownership diverged for club {club_id}"
            )
        active = {
            int(player.index) for player in roster if player.match_active
        }
        substitutes = {
            int(player.index)
            for player in roster
            if player.match_substitute_available
        }
        if active & substitutes:
            raise AssertionError(
                f"seed 0x{int(seed):08X}: active/substitute overlap for club {club_id}"
            )
        if len(active) != 11 or len(substitutes) != 5:
            raise AssertionError(
                f"seed 0x{int(seed):08X}: invalid final selection sizes for club {club_id}"
            )

    return {
        "seed": int(seed) & 0xFFFFFFFF,
        "days": days,
        "result_count": len(state.premier_league.results),
        "digest": _season_digest(state),
        "rng_state_after": int(rng.state) & 0xFFFFFFFF,
    }


class Gate16MultiSeedSeasonStressTests(unittest.TestCase):
    def test_six_edge_case_seeds_complete_full_autonomous_seasons(self):
        audits = tuple(run_autonomous_season(seed) for seed in STRESS_SEEDS)
        self.assertEqual(len(audits), 6)
        self.assertTrue(all(item["result_count"] == 380 for item in audits))
        self.assertTrue(all(item["days"] <= 366 for item in audits))
        self.assertEqual(
            [item["seed"] for item in audits],
            [seed & 0xFFFFFFFF for seed in STRESS_SEEDS],
        )

    def test_repeated_seed_replays_identical_complete_season(self):
        first = run_autonomous_season(0x12345678)
        second = run_autonomous_season(0x12345678)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
