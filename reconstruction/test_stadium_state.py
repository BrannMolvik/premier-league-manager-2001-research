import struct
import unittest

from stadium_state import (
    BUILDING_SERIALIZED_RECORD_SIZE,
    MAP_HEADER_SIZE,
    MAP_TRAILING_SIZE,
    SECTION_ANCHORS,
    parse_buildings_dat,
    parse_stadium_map,
)


def building_record(
    *,
    first_extent=1,
    second_extent=1,
    terrace=0,
    seating=0,
    auxiliary=0,
):
    live = bytearray(0x74)
    struct.pack_into("<II", live, 0, first_extent, second_extent)
    struct.pack_into("<I", live, 0x14, terrace)
    struct.pack_into("<I", live, 0x18, auxiliary)
    struct.pack_into("<I", live, 0x20, seating)
    return bytes(live) + bytes(live[0x08:0x64])


def map_bytes(cells, flags, *, dynamic_anchor=(0xFFFFFFFF, 0xFFFFFFFF)):
    state = bytearray(MAP_HEADER_SIZE)
    struct.pack_into("<II", state, 0, *dynamic_anchor)
    grid = [0xFFFFFFFF] * (40 * 40)
    for first, second, packed in cells:
        grid[first * 40 + second] = packed
    return (
        b"FM\0"
        + bytes(state)
        + struct.pack("<1600I", *grid)
        + bytes(flags)
        + bytes(MAP_TRAILING_SIZE)
    )


class StadiumSourceStateTests(unittest.TestCase):
    def test_building_parser_uses_recovered_capacity_offsets(self):
        data = building_record(
            first_extent=3,
            second_extent=5,
            terrace=1200,
            seating=3400,
            auxiliary=77,
        )
        records = parse_buildings_dat(data)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].first_extent, 3)
        self.assertEqual(records[0].second_extent, 5)
        self.assertEqual(records[0].terrace_capacity, 1200)
        self.assertEqual(records[0].seating_capacity, 3400)
        self.assertEqual(records[0].auxiliary_capacity, 77)

    def test_building_parser_rejects_wrong_overlay_layout(self):
        data = bytearray(building_record())
        data[-1] ^= 1
        with self.assertRaises(ValueError):
            parse_buildings_dat(data)

    def test_map_rotation_swaps_instance_extents(self):
        buildings = parse_buildings_dat(
            building_record(first_extent=2, second_extent=4, seating=100)
        )
        packed = 0 | (1 << 14)
        stadium = parse_stadium_map(map_bytes([(10, 11, packed)], [0]), buildings)
        instance = stadium.instances[0]
        self.assertEqual(
            (instance.first_min, instance.second_min, instance.first_max, instance.second_max),
            (10, 11, 14, 13),
        )

    def test_descending_anchor_pass_preserves_original_overwrite_behavior(self):
        first, second = SECTION_ANCHORS[4]
        # One 10x10 stand covers several consecutive fixed anchors. The
        # original descending pass ends with the lowest matching section index.
        buildings = parse_buildings_dat(
            building_record(first_extent=10, second_extent=10, seating=7000)
        )
        stadium = parse_stadium_map(
            map_bytes([(first, second, 0)], [0]),
            buildings,
        )
        mapped = [
            index
            for index, instance in enumerate(stadium.section_instances)
            if instance is not None
        ]
        self.assertEqual(mapped[0], 4)
        self.assertIs(stadium.section_instances[4], stadium.instances[0])

    def test_fresh_section_state_and_capacity_follow_instance_flag(self):
        anchor0 = SECTION_ANCHORS[0]
        anchor4 = SECTION_ANCHORS[4]
        buildings = parse_buildings_dat(
            building_record(seating=1000)
            + building_record(terrace=500)
        )
        stadium = parse_stadium_map(
            map_bytes(
                [
                    (anchor0[0], anchor0[1], 0),
                    (anchor4[0], anchor4[1], 1),
                ],
                [0, 0x02],
            ),
            buildings,
        )
        self.assertEqual(stadium.initial_section_states[0], 0)
        self.assertEqual(stadium.initial_section_states[4], -1)
        self.assertEqual(stadium.initial_home_capacity.terrace, 0)
        self.assertEqual(stadium.initial_home_capacity.seating, 1000)


if __name__ == "__main__":
    unittest.main()
