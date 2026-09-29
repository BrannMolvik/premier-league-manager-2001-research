import unittest
from dataclasses import dataclass
from types import SimpleNamespace

from competition_schedule import StartupScheduleNode, direct_club_ref
from cup_progression import CupResultRegistry
from domestic_cup_state import DomesticCupScheduleState
from match_schedule import MsvcCrtRng
from season_regeneration import (
    capture_annual_type3_qualification_snapshot,
    clubs_with_live_competition_memberships,
    materialize_annual_primary_schedule,
)


@dataclass(frozen=True)
class Competition:
    id: int
    runtime_kind_code: int
    schedule_container_code: int = 0
    parent_competition_id: int | None = None
    initialization_order_value: int = 0
    country_region_id: int = 1
    runtime_instance_count: int = 1
    scheduled_matchday_count: int = 3


@dataclass(frozen=True)
class Round:
    id: int
    competition_id: int
    type_code: int
    team_count: int
    new_entrants: int
    scheduled_week: int
    scheduled_weekday: int
    replay_week: int = 0
    replay_weekday: int = 1
    source_competition_reference: int = 0xFFFFFFFF


@dataclass(frozen=True)
class Club:
    index: int
    short_name: str
    competition_id: int
    historical_competition_id: int
    historical_slot_index: int
    country_id: int = 1
    runtime_value_1c_source: int = 0
    team_category_code: int = 1


@dataclass(frozen=True)
class Country:
    id: int
    eu_status_flag: int = 0


@dataclass(frozen=True)
class Allocation:
    id: int
    destination_competition_id: int
    sequence_index: int
    instruction_type: int
    source_reference: int
    quantity: int
    auxiliary: int = 0


class AnnualPrimaryRegenerationTests(unittest.TestCase):
    def _fixture(self):
        competition = Competition(0, 1)
        rounds = tuple(
            Round(
                id=index,
                competition_id=0,
                type_code=4,
                team_count=4,
                new_entrants=0,
                scheduled_week=index + 7,
                scheduled_weekday=6,
            )
            for index in range(3)
        )
        clubs = (
            Club(10, "A", 0, 0, 0),
            Club(11, "B", 0, 0, 1),
            Club(12, "C", 0, 0, 2),
            Club(13, "D", 0, 0, 3),
            Club(20, "Promoted", 2, 2, 0),
        )
        return (competition,), rounds, clubs, (Country(1),)

    def test_live_membership_overlay_does_not_mutate_source_clubs(self):
        _competitions, _rounds, clubs, _countries = self._fixture()
        live = clubs_with_live_competition_memberships(
            clubs,
            {13: 2, 20: 0},
        )

        self.assertEqual(
            tuple((club.index, club.competition_id) for club in live),
            ((10, 0), (11, 0), (12, 0), (13, 2), (20, 0)),
        )
        self.assertEqual(clubs[3].competition_id, 0)
        self.assertEqual(clubs[4].competition_id, 2)

    def test_year_two_premier_league_is_procedural_from_live_memberships(self):
        competitions, rounds, clubs, countries = self._fixture()
        rng = MsvcCrtRng(0x12345678)

        result = materialize_annual_primary_schedule(
            rng,
            competitions,
            rounds,
            clubs,
            countries,
            (),
            (),
            club_competition_membership={13: 2, 20: 0},
            season_year=2001,
        )

        nodes = result.competition.schedule_nodes
        self.assertTrue(nodes)
        self.assertTrue(all(node.node_kind == "league_match" for node in nodes))
        direct_ids = {
            int(ref.direct_club_id)
            for node in nodes
            for ref in (node.participant_0_ref, node.participant_1_ref)
            if ref.direct_club_id is not None
        }
        self.assertEqual(direct_ids, {10, 11, 12, 20})
        self.assertNotIn(13, direct_ids)

    def test_annual_type3_requires_finished_season_qualification_ranking(self):
        competitions = (
            Competition(20, 1, initialization_order_value=0),
            Competition(50, 2, initialization_order_value=1),
        )
        rounds = tuple(
            Round(index, 20, 4, 4, 0, index + 1, 1)
            for index in range(3)
        ) + (
            Round(100, 50, 1, 2, 2, 7, 1),
        )
        clubs = (
            Club(10, "A", 20, 99, 3),
            Club(11, "B", 20, 99, 2),
            Club(12, "C", 20, 99, 1),
            Club(13, "Relegated", 20, 99, 0),
            Club(20, "Promoted", 2, 2, 0),
        )
        allocations = (Allocation(1, 50, 1, 3, 20, 2),)

        with self.assertRaisesRegex(
            ValueError,
            "annual type-3 League/Dummy qualification rankings",
        ):
            materialize_annual_primary_schedule(
                MsvcCrtRng(0x12345678),
                competitions,
                rounds,
                clubs,
                (Country(1),),
                allocations,
                (),
                club_competition_membership={13: 2, 20: 20},
                season_year=2001,
            )

    def test_annual_type3_uses_finished_ranking_not_post_swap_membership(self):
        competitions = (
            Competition(20, 1, initialization_order_value=0),
            Competition(50, 2, initialization_order_value=1),
        )
        rounds = tuple(
            Round(index, 20, 4, 4, 0, index + 1, 1)
            for index in range(3)
        ) + (
            Round(100, 50, 1, 2, 2, 7, 1),
        )
        clubs = (
            Club(10, "A", 20, 99, 3),
            Club(11, "B", 20, 99, 2),
            Club(12, "C", 20, 99, 1),
            Club(13, "Relegated", 20, 99, 0),
            Club(20, "Promoted", 2, 2, 0),
        )
        allocations = (Allocation(1, 50, 1, 3, 20, 2),)

        result = materialize_annual_primary_schedule(
            MsvcCrtRng(0x12345678),
            competitions,
            rounds,
            clubs,
            (Country(1),),
            allocations,
            (),
            club_competition_membership={13: 2, 20: 20},
            season_year=2001,
            qualification_rankings_by_competition={
                20: (13, 10, 11, 12),
            },
        )

        live_by_id = {club.index: club for club in result.live_clubs}
        self.assertEqual(live_by_id[13].competition_id, 2)
        self.assertEqual(live_by_id[13].historical_competition_id, 20)
        self.assertEqual(live_by_id[13].historical_slot_index, 0)
        self.assertEqual(live_by_id[20].competition_id, 20)
        selected = set(
            result.competition.cup_runtime.cups[0].selected_direct_club_ids
        )
        self.assertEqual(selected, {10, 13})
        self.assertIn(13, selected)
        self.assertNotIn(20, selected)

    def test_annual_type3_cup_source_requires_completed_result_pair(self):
        competitions = (
            Competition(40, 2, initialization_order_value=0),
            Competition(50, 2, initialization_order_value=1),
        )
        allocations = (Allocation(1, 50, 1, 3, 40, 1),)

        with self.assertRaisesRegex(
            ValueError,
            "annual type-3 Cup result enumerations",
        ):
            materialize_annual_primary_schedule(
                MsvcCrtRng(0x12345678),
                competitions,
                (),
                (),
                (Country(1),),
                allocations,
                (),
                club_competition_membership={},
                season_year=2001,
            )

    def test_annual_dummy_type5_uses_post_swap_membership(self):
        competitions = (
            Competition(89, 3, initialization_order_value=0),
            Competition(1, 2, initialization_order_value=1),
        )
        rounds = (
            Round(100, 1, 1, 2, 2, 7, 1),
        )
        clubs = (
            Club(70, "Stayed", 89, 89, 0),
            Club(71, "Moved Out", 89, 89, 1),
            Club(72, "Moved In", 7, 7, 0),
        )
        allocations = (Allocation(1, 1, 1, 5, 89, 2),)

        result = materialize_annual_primary_schedule(
            MsvcCrtRng(0x12345678),
            competitions,
            rounds,
            clubs,
            (Country(1),),
            allocations,
            (),
            club_competition_membership={71: 7, 72: 89},
            season_year=2001,
        )

        selected = set(
            result.competition.cup_runtime.cups[0].selected_direct_club_ids
        )
        self.assertEqual(selected, {70, 72})
        self.assertNotIn(71, selected)
        self.assertEqual(
            dict(result.competition.cup_runtime.ranked_source_club_ids).keys(),
            {89},
        )

    def test_live_annual_snapshot_preserves_binary_cup_winner_loser_order(self):
        competitions = (
            Competition(20, 1, initialization_order_value=0),
            Competition(40, 2, initialization_order_value=1),
            Competition(50, 2, initialization_order_value=2),
        )
        allocations = (
            Allocation(1, 50, 1, 3, 20, 1),
            Allocation(2, 50, 2, 3, 40, 1),
        )
        registry = CupResultRegistry()
        registry.replace_competition_ranking(20, (10, 11, 12))
        token = ("cup_result", 40, 100, 0)
        registry.record_knockout_outcome(token, 30, 31, 31)
        domestic = DomesticCupScheduleState.from_startup_nodes(
            (
                StartupScheduleNode(
                    node_kind="cup_match",
                    competition_id=40,
                    competition_context=0,
                    round_id=100,
                    pair_index=0,
                    schedule_index=None,
                    scheduled_week=30,
                    scheduled_weekday=6,
                    participant_0_ref=direct_club_ref(30),
                    participant_1_ref=direct_club_ref(31),
                    node_token=token,
                    round_number=9,
                ),
            ),
            season_year=2000,
            competition_ids=(40,),
        )
        state = SimpleNamespace(
            cup_results=registry,
            domestic_cups=domestic,
            european_cups=DomesticCupScheduleState(),
        )

        snapshot = capture_annual_type3_qualification_snapshot(
            state,
            competitions,
            allocations,
        )

        self.assertEqual(
            snapshot.qualification_rankings_by_competition,
            {20: (10, 11, 12)},
        )
        self.assertEqual(
            snapshot.cup_enumerated_club_ids_by_source,
            {40: (31, 30)},
        )

    def test_live_annual_snapshot_rejects_missing_league_source(self):
        competitions = (
            Competition(20, 1),
            Competition(50, 2),
        )
        allocations = (Allocation(1, 50, 1, 3, 20, 1),)
        state = SimpleNamespace(
            cup_results=CupResultRegistry(),
            domestic_cups=DomesticCupScheduleState(),
            european_cups=DomesticCupScheduleState(),
        )

        with self.assertRaisesRegex(
            RuntimeError,
            r"League/Dummy qualification rankings are unresolved for \(20,\)",
        ):
            capture_annual_type3_qualification_snapshot(
                state,
                competitions,
                allocations,
            )

    def test_live_annual_snapshot_rejects_unresolved_cup_final(self):
        competitions = (
            Competition(40, 2),
            Competition(50, 2),
        )
        allocations = (Allocation(1, 50, 1, 3, 40, 1),)
        token = ("cup_result", 40, 100, 0)
        domestic = DomesticCupScheduleState.from_startup_nodes(
            (
                StartupScheduleNode(
                    node_kind="cup_match",
                    competition_id=40,
                    competition_context=0,
                    round_id=100,
                    pair_index=0,
                    schedule_index=None,
                    scheduled_week=30,
                    scheduled_weekday=6,
                    participant_0_ref=direct_club_ref(30),
                    participant_1_ref=direct_club_ref(31),
                    node_token=token,
                    round_number=9,
                ),
            ),
            season_year=2000,
            competition_ids=(40,),
        )
        state = SimpleNamespace(
            cup_results=CupResultRegistry(),
            domestic_cups=domestic,
            european_cups=DomesticCupScheduleState(),
        )

        with self.assertRaisesRegex(
            RuntimeError,
            r"Cup final enumerations are unresolved for \(40,\)",
        ):
            capture_annual_type3_qualification_snapshot(
                state,
                competitions,
                allocations,
            )

    def test_same_crt_stream_continues_through_fresh_bucket_shuffle(self):
        competitions, rounds, clubs, countries = self._fixture()
        rng = MsvcCrtRng(0x12345678)

        result = materialize_annual_primary_schedule(
            rng,
            competitions,
            rounds,
            clubs,
            countries,
            (),
            (),
            club_competition_membership={13: 2, 20: 0},
            season_year=2001,
        )

        self.assertEqual(result.state_after, rng.state)
        self.assertEqual(
            result.state_entering_shuffle,
            result.competition.state_entering_primary_shuffle,
        )
        self.assertGreater(result.competition_draw_count, 0)
        self.assertGreater(result.bucket_shuffle_draw_count, 0)
        self.assertGreater(result.total_draw_count, result.competition_draw_count)
        self.assertNotEqual(result.state_before, result.state_entering_shuffle)
        self.assertNotEqual(result.state_entering_shuffle, result.state_after)


if __name__ == "__main__":
    unittest.main()
