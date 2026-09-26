import unittest
from dataclasses import dataclass

from competition_runtime import replay_primary_mode0_complete_competition_rng
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


@dataclass(frozen=True)
class Round:
    competition_id: int
    team_count: int
    id: int = 0
    type_code: int = 1
    scheduled_week: int = 0
    scheduled_weekday: int = 1
    source_competition_reference: int = 0xFFFFFFFF


@dataclass(frozen=True)
class Club:
    index: int
    competition_id: int
    country_id: int = 1
    runtime_value_1c_source: int = 0
    team_category_code: int = 1


@dataclass(frozen=True)
class Country:
    id: int
    eu_status_flag: int = 0


class CompleteCompetitionRuntimeReplayTests(unittest.TestCase):
    def test_procedural_root_runs_before_child_instances(self):
        competitions = (
            Competition(20, 1, parent_competition_id=None),
            Competition(
                30,
                1,
                parent_competition_id=20,
                runtime_instance_count=2,
            ),
        )
        rounds = (
            Round(20, 4, id=100),
            Round(30, 4, id=200),
        )
        clubs = tuple(Club(i, 20) for i in range(4))
        rng = MsvcCrtRng(0x12345678)

        replay = replay_primary_mode0_complete_competition_rng(
            rng,
            competitions,
            rounds,
            clubs,
            (Country(1),),
            fixed_fixture_competition_ids=(),
        )

        self.assertEqual(replay.procedural_league_instance_count, 3)
        self.assertEqual(replay.procedural_league_draw_count, 18)
        self.assertEqual(replay.total_draw_count, 18)
        self.assertEqual(
            tuple(
                (
                    event.kind,
                    event.competition_id,
                    event.competition_context,
                    event.participant_count,
                    len(event.bounds),
                )
                for event in replay.events
            ),
            (
                ("procedural_league_round_robin", 20, 0, 4, 6),
                ("procedural_league_round_robin", 30, 0, 4, 6),
                ("procedural_league_round_robin", 30, 1, 4, 6),
            ),
        )

    def test_fixed_fixture_league_adds_no_round_robin_rng(self):
        competitions = (Competition(0, 1),)
        rounds = (Round(0, 20),)
        clubs = tuple(Club(i, 0) for i in range(20))
        rng = MsvcCrtRng(0x12345678)

        replay = replay_primary_mode0_complete_competition_rng(
            rng,
            competitions,
            rounds,
            clubs,
            (Country(1),),
        )

        self.assertEqual(replay.events, ())
        self.assertEqual(replay.total_draw_count, 0)
        self.assertEqual(replay.state_entering_primary_shuffle, 0x12345678)

    def test_dummy_root_does_not_use_procedural_league_builder(self):
        competitions = (Competition(50, 3),)
        rounds = (Round(50, 8),)
        clubs = tuple(Club(i, 50) for i in range(8))
        rng = MsvcCrtRng(0x12345678)

        replay = replay_primary_mode0_complete_competition_rng(
            rng,
            competitions,
            rounds,
            clubs,
            (Country(1),),
            fixed_fixture_competition_ids=(),
        )

        self.assertEqual(replay.events, ())
        self.assertEqual(replay.total_draw_count, 0)


if __name__ == "__main__":
    unittest.main()
