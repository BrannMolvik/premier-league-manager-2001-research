"""Gate-16 long-calendar stress for the shared Gate-12 primary scheduler."""

from datetime import timedelta
from types import SimpleNamespace
import unittest

from competition_schedule import StartupScheduleNode, direct_club_ref
from competition_state import season_weekday_date
from domestic_cup_state import DomesticCupScheduleState
from game_state import GameState
from primary_schedule import primary_schedule_source_bucket
from test_game_state_competition import AutonomousDatabase, coefficient_matrix


SEASON_YEAR = 2000
CYCLE_WEEKS = (2, 8, 14, 20, 26, 32, 38, 44)


class MixedPrimaryDatabase(AutonomousDatabase):
    """Keep the proven two-club AI fixture while removing unused synthetic PL ties."""

    real_fixtures = (AutonomousDatabase.real_fixtures[0],)
    premier_league_rounds = (
        SimpleNamespace(
            round_number=1,
            scheduled_week=1,
            scheduled_weekday=6,
        ),
    )


def _cup_nodes(competition_id: int, weekday: int):
    nodes = []
    for index, week in enumerate(CYCLE_WEEKS):
        left, right = ((1, 2) if index % 2 == 0 else (2, 1))
        round_id = int(competition_id) * 1000 + index
        nodes.append(
            StartupScheduleNode(
                node_kind="cup_match",
                competition_id=int(competition_id),
                competition_context=0,
                round_id=round_id,
                pair_index=0,
                schedule_index=None,
                scheduled_week=int(week),
                scheduled_weekday=int(weekday),
                participant_0_ref=direct_club_ref(left),
                participant_1_ref=direct_club_ref(right),
                node_token=("cup_result", int(competition_id), round_id, 0),
                round_number=index + 1,
                extra_time_capable=True,
                decisive_tiebreak=True,
                auxiliary_flag=False,
            )
        )
    return tuple(nodes)


def _procedural_nodes():
    nodes = []
    for index, week in enumerate(CYCLE_WEEKS):
        left, right = ((1, 2) if index % 2 == 0 else (2, 1))
        nodes.append(
            StartupScheduleNode(
                node_kind="league_match",
                competition_id=2,
                competition_context=0,
                round_id=None,
                pair_index=index,
                schedule_index=index,
                scheduled_week=int(week),
                scheduled_weekday=4,
                participant_0_ref=direct_club_ref(left),
                participant_1_ref=direct_club_ref(right),
                node_token=("league_match", 2, 0, index),
            )
        )
    return tuple(nodes)


def _raw_primary_buckets(nodes):
    max_bucket = max(
        primary_schedule_source_bucket(
            int(node.scheduled_week),
            int(node.scheduled_weekday),
        )
        for node in nodes
    )
    buckets = [[] for _ in range(max_bucket + 1)]
    for node in nodes:
        bucket = primary_schedule_source_bucket(
            int(node.scheduled_week),
            int(node.scheduled_weekday),
        )
        if bucket < 0:
            raise AssertionError("mixed-primary fixture produced a negative source bucket")
        buckets[bucket].append(node)
    return tuple(tuple(bucket) for bucket in buckets)


def _build_state(seed: int):
    state = GameState.from_database(
        MixedPrimaryDatabase(),
        season_weekday_date(SEASON_YEAR, 1, 6) - timedelta(days=1),
        seed=int(seed),
        season_year=SEASON_YEAR,
    )

    for competition_id in (1, 9, 19):
        state.competitions[competition_id] = SimpleNamespace(
            id=competition_id,
            substitute_quota=5,
            max_non_eu_players=10,
            scheduled_matchday_count=len(CYCLE_WEEKS),
            initialization_order_value=6,
        )
    state.competitions[2] = SimpleNamespace(
        id=2,
        substitute_quota=5,
        max_non_eu_players=10,
    )

    domestic = _cup_nodes(1, 1)
    european = _cup_nodes(9, 2)
    qualification = _cup_nodes(19, 3)
    procedural = _procedural_nodes()
    pl_shadow = StartupScheduleNode(
        node_kind="league_match",
        competition_id=0,
        competition_context=0,
        round_id=None,
        pair_index=0,
        schedule_index=0,
        scheduled_week=1,
        scheduled_weekday=6,
        participant_0_ref=direct_club_ref(1),
        participant_1_ref=direct_club_ref(2),
        node_token=("league_match", 0, 0, 0),
    )

    all_nodes = (pl_shadow,) + domestic + european + qualification + procedural
    buckets = _raw_primary_buckets(all_nodes)
    state.install_primary_schedule_shadow(buckets, season_year=SEASON_YEAR)
    state.install_primary_matchday_order(
        buckets,
        season_year=SEASON_YEAR,
        procedural_league_ids=(2,),
    )

    state.domestic_cups = DomesticCupScheduleState.from_startup_nodes(
        domestic,
        season_year=SEASON_YEAR,
        competition_ids=(1,),
    )
    state.european_cups = DomesticCupScheduleState.from_startup_nodes(
        european,
        season_year=SEASON_YEAR,
        competition_ids=(9,),
    )
    state.qualification_cups = DomesticCupScheduleState.from_startup_nodes(
        qualification,
        season_year=SEASON_YEAR,
        competition_ids=(19,),
    )
    state.refresh_primary_procedural_leagues((2,))
    if (2, 0) not in state.procedural_leagues:
        raise AssertionError("synthetic procedural League failed to materialize")

    return state


def _run_mixed_primary(seed: int):
    state = _build_state(seed)
    attack = coefficient_matrix()
    defence = coefficient_matrix()
    final_scheduled_date = max(state.primary_matchday_order)
    stop_date = final_scheduled_date + timedelta(days=7)
    executed = []
    days = 0

    while state.calendar.current_date < stop_date:
        days += 1
        if days > 370:
            raise AssertionError("mixed-primary stress exceeded one-year day budget")
        on_date = state.calendar.current_date + timedelta(days=1)
        results = state.advance_one_day_with_primary_ai_matches(attack, defence)
        for entry, result in results:
            executed.append(
                (
                    on_date.isoformat(),
                    str(entry[0]),
                    tuple(entry[1]) if isinstance(entry[1], tuple) else int(entry[1]),
                    tuple(int(value) for value in result.score),
                )
            )

    kinds = {}
    for _on_date, kind, _identity, _score in executed:
        kinds[kind] = kinds.get(kind, 0) + 1

    expected_owner_count = len(CYCLE_WEEKS)
    if kinds != {
        "premier_league": 1,
        "domestic_cup": expected_owner_count,
        "european_cup": expected_owner_count,
        "qualification_cup": expected_owner_count,
        "procedural_league": expected_owner_count,
    }:
        raise AssertionError(f"unexpected shared-primary execution counts: {kinds!r}")

    for owner in (
        state.domestic_cups,
        state.european_cups,
        state.qualification_cups,
    ):
        if len(owner.nodes) != expected_owner_count:
            raise AssertionError("Cup owner node count changed during stress")
        if len(owner.completed_node_tokens) != expected_owner_count:
            raise AssertionError("Cup owner left scheduled nodes incomplete")
        if len(owner.match_states) != expected_owner_count:
            raise AssertionError("Cup owner retained unexpected transient match state")

    if len(state.cup_results.outcomes) != 3 * expected_owner_count:
        raise AssertionError("Cup result registry growth is not event-proportional")

    procedural = state.procedural_leagues[(2, 0)]
    if len(procedural.fixtures) != expected_owner_count:
        raise AssertionError("procedural League fixture identity changed")
    if len(procedural.results) != expected_owner_count:
        raise AssertionError("procedural League left scheduled matches incomplete")
    if not procedural.is_complete:
        raise AssertionError("procedural League did not reach complete state")
    if sum(int(row.played) for row in procedural.table()) != 2 * expected_owner_count:
        raise AssertionError("procedural League played totals do not reconcile")

    if len(state.premier_league.results) != 1:
        raise AssertionError("synthetic Premier League fixture was not completed")

    for club_id in (1, 2):
        roster = state.ordered_club_roster(club_id)
        if len(roster) != 16:
            raise AssertionError(f"club {club_id} roster changed size during mixed stress")
        if any(int(player.club_id) != club_id for player in roster):
            raise AssertionError(f"club {club_id} roster ownership diverged")

    for player in state.players.values():
        if not 0 <= int(player.condition) <= 100:
            raise AssertionError(f"invalid Condition for player {player.index}")
        if not 0 <= int(player.form_state) <= 4:
            raise AssertionError(f"invalid Form for player {player.index}")
        if int(player.suspension_matches_remaining) < 0:
            raise AssertionError(f"negative suspension for player {player.index}")
        if player.injured and player.injury_return_date is None:
            raise AssertionError(f"injured player {player.index} lacks a return date")

    if state.transfers.proposals or state.transfers.deals:
        raise AssertionError("mixed-primary calendar leaked transfer negotiation state")
    if state.transfers.bid_log or state.transfers.scheduled_transfers:
        raise AssertionError("mixed-primary calendar leaked pending transfer state")

    return {
        "days": days,
        "final_date": state.calendar.current_date.isoformat(),
        "executed": tuple(executed),
        "cup_outcomes": tuple(
            sorted(
                (
                    tuple(token),
                    int(outcome.winner_club_id),
                    int(outcome.loser_club_id),
                )
                for token, outcome in state.cup_results.outcomes.items()
            )
        ),
        "procedural_results": tuple(
            sorted(
                (
                    tuple(token),
                    int(result.home_goals),
                    int(result.away_goals),
                )
                for token, result in procedural.results.items()
            )
        ),
        "players": tuple(
            (
                int(player.index),
                int(player.condition),
                int(player.form_state),
                bool(player.injured),
                int(player.suspension_matches_remaining),
            )
            for player in sorted(state.players.values(), key=lambda item: int(item.index))
        ),
        "rng_state": int(state.rng.state) & 0xFFFFFFFF,
    }


class Gate16MixedPrimaryStressTests(unittest.TestCase):
    def test_shared_primary_scheduler_survives_long_mixed_owner_calendar(self):
        result = _run_mixed_primary(0x13579BDF)
        self.assertLessEqual(result["days"], 370)
        self.assertGreater(len(result["executed"]), 30)

    def test_mixed_primary_stress_replays_identically_for_same_seed(self):
        first = _run_mixed_primary(0x2468ACE0)
        second = _run_mixed_primary(0x2468ACE0)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
