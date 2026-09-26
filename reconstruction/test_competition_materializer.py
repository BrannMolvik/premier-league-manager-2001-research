import unittest
from dataclasses import dataclass

from competition_materializer import materialize_primary_rng_driven_schedule
from match_schedule import MsvcCrtRng


@dataclass(frozen=True)
class Competition:
    id: int
    runtime_kind_code: int
    schedule_container_code: int = 0
    parent_competition_id: int | None = None
    initialization_order_value: int = 0
    country_region_id: int = 1
    runtime_instance_count: int = 1
    scheduled_matchday_count: int = 0


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
class Allocation:
    id: int
    destination_competition_id: int
    sequence_index: int
    instruction_type: int
    source_reference: int
    quantity: int
    auxiliary: int = 0


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
class RealFixture:
    id: int
    round_index: int
    home_club_id: int
    away_club_id: int


class IntegratedCompetitionMaterializerTests(unittest.TestCase):
    def _fixture(self):
        competitions = (
            Competition(
                20,
                1,
                initialization_order_value=0,
                scheduled_matchday_count=6,
            ),
            Competition(
                50,
                2,
                initialization_order_value=1,
            ),
        )
        league_rounds = tuple(
            Round(
                id=index,
                competition_id=20,
                type_code=4,
                team_count=4,
                new_entrants=0,
                scheduled_week=index + 1,
                scheduled_weekday=1,
            )
            for index in range(6)
        )
        cup_round = Round(
            id=100,
            competition_id=50,
            type_code=1,
            team_count=4,
            new_entrants=4,
            scheduled_week=7,
            scheduled_weekday=1,
        )
        allocations = (
            Allocation(1, 50, 1, 3, 20, 4),
        )
        clubs = tuple(
            Club(
                index=club_id,
                short_name=f"Club {club_id}",
                competition_id=20,
                historical_competition_id=20,
                historical_slot_index=slot,
            )
            for slot, club_id in enumerate((10, 11, 12, 13))
        )
        return (
            competitions,
            league_rounds + (cup_round,),
            allocations,
            clubs,
            (Country(1),),
        )

    def test_one_crt_stream_interleaves_league_before_cup(self):
        competitions, rounds, allocations, clubs, countries = self._fixture()
        rng = MsvcCrtRng(0x12345678)

        result = materialize_primary_rng_driven_schedule(
            rng,
            competitions,
            rounds,
            clubs,
            countries,
            allocations,
            fixed_fixture_competition_ids=(),
        )

        self.assertEqual(result.rng_plan_total_draw_count, 9)
        self.assertEqual(result.rng_plan_event_count, 2)
        self.assertEqual(result.cup_runtime.ordered_bounds, (4, 3, 2))
        self.assertEqual(result.schedule_node_count, 14)
        self.assertEqual(
            tuple(node.node_kind for node in result.schedule_nodes[:12]),
            ("league_match",) * 12,
        )
        self.assertEqual(
            tuple(node.node_kind for node in result.schedule_nodes[12:]),
            ("cup_match", "cup_match"),
        )
        self.assertEqual(
            tuple(node.competition_id for node in result.schedule_nodes[:12]),
            (20,) * 12,
        )
        self.assertEqual(
            tuple(node.competition_id for node in result.schedule_nodes[12:]),
            (50, 50),
        )
        self.assertEqual(
            rng.state,
            result.state_entering_primary_shuffle,
        )

    def test_fixed_league_zero_draw_nodes_keep_traversal_position(self):
        competitions = (
            Competition(0, 1, initialization_order_value=0),
            Competition(50, 2, initialization_order_value=1),
        )
        rounds = (
            Round(0, 0, 4, 4, 0, 1, 6),
            Round(1, 0, 4, 4, 0, 2, 3),
            Round(100, 50, 1, 4, 4, 3, 1),
        )
        allocations = (Allocation(1, 50, 1, 3, 0, 4),)
        clubs = tuple(
            Club(
                index=club_id,
                short_name=f"Club {club_id}",
                competition_id=0,
                historical_competition_id=0,
                historical_slot_index=slot,
            )
            for slot, club_id in enumerate((10, 11, 12, 13))
        )
        fixtures = (
            RealFixture(0, 0, 10, 11),
            RealFixture(1, 0, 12, 13),
            RealFixture(2, 1, 10, 12),
            RealFixture(3, 1, 11, 13),
        )

        result = materialize_primary_rng_driven_schedule(
            MsvcCrtRng(0x12345678),
            competitions,
            rounds,
            clubs,
            (Country(1),),
            allocations,
            real_fixtures=fixtures,
        )

        self.assertEqual(result.rng_plan_total_draw_count, 3)
        self.assertEqual(result.rng_plan_event_count, 2)
        self.assertEqual(result.schedule_node_count, 6)
        self.assertEqual(
            tuple(node.node_kind for node in result.schedule_nodes),
            (
                "fixed_league_match",
                "fixed_league_match",
                "fixed_league_match",
                "fixed_league_match",
                "cup_match",
                "cup_match",
            ),
        )

    def test_integrated_schedule_digest_is_repeatable(self):
        fixture = self._fixture()

        first = materialize_primary_rng_driven_schedule(
            MsvcCrtRng(0x12345678),
            fixture[0],
            fixture[1],
            fixture[3],
            fixture[4],
            fixture[2],
            fixed_fixture_competition_ids=(),
        )
        second = materialize_primary_rng_driven_schedule(
            MsvcCrtRng(0x12345678),
            fixture[0],
            fixture[1],
            fixture[3],
            fixture[4],
            fixture[2],
            fixed_fixture_competition_ids=(),
        )

        self.assertEqual(first.schedule_sha256, second.schedule_sha256)
        self.assertEqual(len(first.schedule_sha256), 64)
        self.assertEqual(
            first.cup_runtime.participant_sha256,
            second.cup_runtime.participant_sha256,
        )
        self.assertEqual(
            first.cup_runtime.pairing_sha256,
            second.cup_runtime.pairing_sha256,
        )


if __name__ == "__main__":
    unittest.main()
