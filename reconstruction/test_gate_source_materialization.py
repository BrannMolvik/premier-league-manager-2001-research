from datetime import date
from types import SimpleNamespace
import unittest

from game_state import GameCalendar, GameState
from stadium_state import (
    MAP_HEADER_SIZE,
    MAP_TRAILING_SIZE,
    StadiumBuildingDefinition,
    StadiumBuildingInstance,
    StadiumSourceState,
)


def stadium_with_sections(capacities):
    buildings = []
    instances = []
    section_instances = [None] * 26
    for section_index, (terrace, seating) in capacities.items():
        building_id = len(buildings)
        buildings.append(
            StadiumBuildingDefinition(
                building_id=building_id,
                first_extent=1,
                second_extent=1,
                terrace_capacity=int(terrace),
                auxiliary_capacity=0,
                seating_capacity=int(seating),
            )
        )
        instance = StadiumBuildingInstance(
            first_min=0,
            second_min=0,
            first_max=1,
            second_max=1,
            building_id=building_id,
            rotation=0,
            flags=0,
            section_index=section_index,
        )
        instances.append(instance)
        section_instances[section_index] = instance
    return StadiumSourceState(
        buildings=tuple(buildings),
        instances=instances,
        section_instances=tuple(section_instances),
        initial_section_states=(0,) * 26,
        map_state=bytes(MAP_HEADER_SIZE),
        trailing_state=bytes(MAP_TRAILING_SIZE),
    )


class GateSourceMaterializationTests(unittest.TestCase):
    def test_arsenal_shape_uses_shipped_rank_band_and_visiting_threshold(self):
        fan_indexes = (
            31, 28, 31, 22, 25, 28, 31, 23, 32, 23,
            28, 21, 28, 27, 23, 20, 23, 22, 26, 21,
        )
        clubs = {
            club_id: SimpleNamespace(
                competition_id=0,
                fan_base_index=fan_index,
                runtime_value_1c_source=38500 if club_id == 0 else 30000,
            )
            for club_id, fan_index in enumerate(fan_indexes)
        }
        state = GameState(
            calendar=GameCalendar(date(2000, 8, 1)),
            players={},
            clubs=clubs,
        )
        # The visiting allocator begins section 24 then 10. Together these
        # cross Arsenal's exact 10*floor(38500/100) = 3850 threshold.
        stadium = stadium_with_sections({
            24: (0, 2000),
            10: (0, 2000),
            9: (0, 1500),
            0: (0, 5000),
        })
        tickets = state.materialize_gate_source_state(
            0,
            stadium,
            seating_reference=30.0,
            terrace_reference=22.5,
        )

        self.assertIs(state.stadium_sources[0], stadium)
        self.assertIs(state.ticket_states[0], tickets)
        self.assertEqual(tickets.seating_price, 30)
        self.assertEqual(tickets.terrace_price, 22)
        self.assertEqual(tickets.section_states[24], 1)
        self.assertEqual(tickets.section_states[10], 1)
        self.assertEqual(tickets.section_states[9], 0)
        self.assertEqual(tickets.capacity(stadium, 1).seating, 4000)

    def test_rank_count_uses_less_than_or_equal_fan_base_index(self):
        clubs = {
            0: SimpleNamespace(
                competition_id=0,
                fan_base_index=20,
                runtime_value_1c_source=10000,
            ),
            1: SimpleNamespace(
                competition_id=0,
                fan_base_index=20,
                runtime_value_1c_source=10000,
            ),
            2: SimpleNamespace(
                competition_id=0,
                fan_base_index=21,
                runtime_value_1c_source=10000,
            ),
            3: SimpleNamespace(
                competition_id=0,
                fan_base_index=22,
                runtime_value_1c_source=10000,
            ),
            4: SimpleNamespace(
                competition_id=0,
                fan_base_index=23,
                runtime_value_1c_source=10000,
            ),
            5: SimpleNamespace(
                competition_id=0,
                fan_base_index=24,
                runtime_value_1c_source=10000,
            ),
        }
        state = GameState(
            calendar=GameCalendar(date(2000, 8, 1)),
            players={},
            clubs=clubs,
        )
        stadium = stadium_with_sections({})
        tickets = state.materialize_gate_source_state(
            0,
            stadium,
            seating_reference=100.0,
            terrace_reference=75.0,
        )
        # Two clubs have fan-base index <=20; N=6, floor(N/2)=3 -> 90%.
        self.assertEqual((tickets.terrace_price, tickets.seating_price), (67, 90))


if __name__ == "__main__":
    unittest.main()
