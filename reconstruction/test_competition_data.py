import struct
import unittest

from fm2001_data import (
    COMPETITION_RECORD_SIZE,
    COMPETITION_TABLE_OFFSET,
    FM2001Database,
)


class FakeStrings:
    def get(self, index):
        return f"name-{index}"


class CompetitionParserTests(unittest.TestCase):
    def test_competition_non_eu_limit_is_packed_byte_34(self):
        data = bytearray(
            COMPETITION_TABLE_OFFSET + 4 + 2 * COMPETITION_RECORD_SIZE
        )
        struct.pack_into("<I", data, COMPETITION_TABLE_OFFSET, 2)
        base = COMPETITION_TABLE_OFFSET + 4

        first = base
        struct.pack_into("<I", data, first + 0, 0)
        struct.pack_into("<i", data, first + 4, -1)
        struct.pack_into("<H", data, first + 12, 100)
        data[first + 14] = 1
        struct.pack_into("<h", data, first + 15, 9)
        data[first + 34] = 3
        struct.pack_into("<I", data, first + 27, 26)
        struct.pack_into("<I", data, first + 45, 1)

        second = base + COMPETITION_RECORD_SIZE
        struct.pack_into("<I", data, second + 0, 25)
        struct.pack_into("<i", data, second + 4, 0)
        struct.pack_into("<H", data, second + 12, 101)
        data[second + 14] = 2
        struct.pack_into("<h", data, second + 15, -3)
        data[second + 34] = 99
        struct.pack_into("<I", data, second + 27, 123)
        struct.pack_into("<I", data, second + 45, 2)

        db = FM2001Database.__new__(FM2001Database)
        db.static = bytes(data)
        db.english = FakeStrings()
        db.competitions = []

        db._parse_competitions()

        self.assertEqual(len(db.competitions), 2)
        self.assertEqual(db.competitions[0].id, 0)
        self.assertEqual(db.competitions[0].name, "name-100")
        self.assertEqual(db.competitions[0].max_non_eu_players, 3)
        self.assertEqual(db.competitions[0].schedule_container_code, 1)
        self.assertFalse(db.competitions[0].uses_secondary_schedule_container)
        self.assertEqual(db.competitions[0].runtime_kind, "league")
        self.assertTrue(db.competitions[0].is_root_competition)
        self.assertEqual(db.competitions[0].initialization_order_value, 9)
        self.assertEqual(db.competitions[0].country_region_id, 26)
        self.assertEqual(db.competitions[1].id, 25)
        self.assertEqual(db.competitions[1].max_non_eu_players, 99)
        self.assertEqual(db.competitions[1].schedule_container_code, 2)
        self.assertTrue(db.competitions[1].uses_secondary_schedule_container)
        self.assertEqual(db.competitions[1].runtime_kind, "cup")
        self.assertEqual(db.competitions[1].parent_competition_id, 0)
        self.assertFalse(db.competitions[1].is_root_competition)
        self.assertEqual(db.competitions[1].initialization_order_value, -3)
        self.assertEqual(db.competitions[1].country_region_id, 123)


if __name__ == "__main__":
    unittest.main()
