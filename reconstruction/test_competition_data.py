import struct
import unittest

from fm2001_data import (
    COMPETITION_RECORD_SIZE,
    COMPETITION_TABLE_OFFSET,
    ROUND_RECORD_SIZE,
    ROUND_TABLE_OFFSET,
    LEAGUE_ALLOCATION_TABLE_OFFSET,
    LEAGUE_ALLOCATION_RECORD_SIZE,
    REAL_FIXTURE_TABLE_OFFSET,
    ACCESS_SKILL_FINANCIAL_TABLE_OFFSET,
    ACCESS_SKILL_FINANCIAL_RECORD_SIZE,
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
        struct.pack_into("<I", data, first + 8, 1)
        struct.pack_into("<H", data, first + 12, 100)
        data[first + 14] = 1
        struct.pack_into("<h", data, first + 15, 9)
        data[first + 18] = 38
        data[first + 31] = 1
        data[first + 34] = 3
        struct.pack_into("<I", data, first + 27, 26)
        struct.pack_into("<I", data, first + 45, 1)

        second = base + COMPETITION_RECORD_SIZE
        struct.pack_into("<I", data, second + 0, 25)
        struct.pack_into("<i", data, second + 4, 0)
        struct.pack_into("<I", data, second + 8, 8)
        struct.pack_into("<H", data, second + 12, 101)
        data[second + 14] = 2
        struct.pack_into("<h", data, second + 15, -3)
        data[second + 18] = 6
        data[second + 31] = 255
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
        self.assertEqual(db.competitions[0].runtime_instance_count, 1)
        self.assertEqual(db.competitions[0].scheduled_matchday_count, 38)
        self.assertEqual(db.competitions[0].valuation_division_category, 1)
        self.assertEqual(db.competitions[1].id, 25)
        self.assertEqual(db.competitions[1].max_non_eu_players, 99)
        self.assertEqual(db.competitions[1].schedule_container_code, 2)
        self.assertTrue(db.competitions[1].uses_secondary_schedule_container)
        self.assertEqual(db.competitions[1].runtime_kind, "cup")
        self.assertEqual(db.competitions[1].parent_competition_id, 0)
        self.assertFalse(db.competitions[1].is_root_competition)
        self.assertEqual(db.competitions[1].initialization_order_value, -3)
        self.assertEqual(db.competitions[1].country_region_id, 123)
        self.assertEqual(db.competitions[1].runtime_instance_count, 8)
        self.assertEqual(db.competitions[1].scheduled_matchday_count, 6)
        self.assertEqual(db.competitions[1].valuation_division_category, 255)


class LeagueAllocationParserTests(unittest.TestCase):
    def test_table_boundary_and_rows_are_lossless(self):
        self.assertEqual(
            LEAGUE_ALLOCATION_TABLE_OFFSET
            + 4
            + 28 * LEAGUE_ALLOCATION_RECORD_SIZE,
            REAL_FIXTURE_TABLE_OFFSET,
        )

        data = bytearray(REAL_FIXTURE_TABLE_OFFSET)
        struct.pack_into("<I", data, LEAGUE_ALLOCATION_TABLE_OFFSET, 2)
        base = LEAGUE_ALLOCATION_TABLE_OFFSET + 4
        first = (10, 20, 30, 40, 50, 60, 70)
        second = (11, 21, 31, 41, 51, 61, 71)
        struct.pack_into("<7I", data, base, *first)
        struct.pack_into(
            "<7I",
            data,
            base + LEAGUE_ALLOCATION_RECORD_SIZE,
            *second,
        )

        db = FM2001Database.__new__(FM2001Database)
        db.static = bytes(data)
        db.league_allocation_records = []
        db._parse_league_allocation_records()

        self.assertEqual(len(db.league_allocation_records), 2)
        self.assertEqual(
            (
                db.league_allocation_records[0].id,
                db.league_allocation_records[0].competition_a_id,
                db.league_allocation_records[0].competition_a_start,
                db.league_allocation_records[0].competition_a_end,
                db.league_allocation_records[0].competition_b_id,
                db.league_allocation_records[0].competition_b_start,
                db.league_allocation_records[0].competition_b_end,
            ),
            first,
        )
        self.assertEqual(
            (
                db.league_allocation_records[1].id,
                db.league_allocation_records[1].competition_a_id,
                db.league_allocation_records[1].competition_a_start,
                db.league_allocation_records[1].competition_a_end,
                db.league_allocation_records[1].competition_b_id,
                db.league_allocation_records[1].competition_b_start,
                db.league_allocation_records[1].competition_b_end,
            ),
            second,
        )
        self.assertEqual(db.league_allocation_records[0].exchange_count, 11)
        self.assertEqual(db.league_allocation_records[1].exchange_count, 11)


class AccessSkillFinancialParserTests(unittest.TestCase):
    def test_financial_rows_decode_packed_id_plus_six_dwords(self):
        data = bytearray(
            ACCESS_SKILL_FINANCIAL_TABLE_OFFSET
            + 4
            + 2 * ACCESS_SKILL_FINANCIAL_RECORD_SIZE
        )
        struct.pack_into("<I", data, ACCESS_SKILL_FINANCIAL_TABLE_OFFSET, 2)
        base = ACCESS_SKILL_FINANCIAL_TABLE_OFFSET + 4
        struct.pack_into(
            "<H6I", data, base,
            0, 50, 10, 1000, 250, 10, 2,
        )
        struct.pack_into(
            "<H6I",
            data,
            base + ACCESS_SKILL_FINANCIAL_RECORD_SIZE,
            1, 125, 25, 2000, 500, 13, 3,
        )

        db = FM2001Database.__new__(FM2001Database)
        db.static = bytes(data)
        db.access_skill_financial_values = []

        db._parse_access_skill_financial_values()

        self.assertEqual(len(db.access_skill_financial_values), 2)
        self.assertEqual(
            db.access_skill_financial_values[0].weekly_wage_base,
            1000,
        )
        self.assertEqual(
            db.access_skill_financial_values[0].weekly_wage_random_range,
            250,
        )
        self.assertEqual(db.access_skill_financial_value(1).id, 1)


class RoundParserTests(unittest.TestCase):
    def test_round_source_competition_reference_is_packed_dword_20(self):
        data = bytearray(ROUND_TABLE_OFFSET + 4 + 2 * ROUND_RECORD_SIZE)
        struct.pack_into("<I", data, ROUND_TABLE_OFFSET, 2)
        base = ROUND_TABLE_OFFSET + 4

        first = base
        struct.pack_into("<I", data, first + 0, 201)
        struct.pack_into("<H", data, first + 4, 3)
        struct.pack_into("<H", data, first + 6, 9)
        struct.pack_into("<H", data, first + 10, 4)
        struct.pack_into("<H", data, first + 14, 500)
        struct.pack_into("<I", data, first + 20, 14)
        struct.pack_into("<H", data, first + 24, 8)
        struct.pack_into("<H", data, first + 26, 8)
        struct.pack_into("<H", data, first + 28, 1)
        data[first + 30] = 1
        data[first + 31] = 0

        second = base + ROUND_RECORD_SIZE
        struct.pack_into("<I", data, second + 0, 202)
        struct.pack_into("<H", data, second + 4, 1)
        struct.pack_into("<H", data, second + 6, 9)
        struct.pack_into("<H", data, second + 10, 5)
        struct.pack_into("<H", data, second + 14, 501)
        struct.pack_into("<I", data, second + 20, 0x0002FFFF)
        struct.pack_into("<H", data, second + 28, 0)
        data[second + 30] = 0
        data[second + 31] = 1

        db = FM2001Database.__new__(FM2001Database)
        db.static = bytes(data)
        db.english = FakeStrings()
        db.rounds = []
        db._parse_rounds()

        self.assertEqual(db.rounds[0].source_competition_reference, 14)
        self.assertEqual(db.rounds[0].source_competition_id, 14)
        self.assertEqual(db.rounds[0].source_child_code, 0)
        self.assertEqual(db.rounds[1].source_competition_reference, 0x0002FFFF)
        self.assertIsNone(db.rounds[1].source_competition_id)
        self.assertEqual(db.rounds[1].source_child_code, 2)
        self.assertEqual(db.rounds[0].cup_extra_time_flag, 1)
        self.assertEqual(db.rounds[0].cup_auxiliary_flag, 1)
        self.assertFalse(db.rounds[0].cup_decisive_tiebreak)
        self.assertTrue(db.rounds[0].cup_extra_time_capable)
        self.assertEqual(db.rounds[1].cup_extra_time_flag, 0)
        self.assertEqual(db.rounds[1].cup_auxiliary_flag, 0)
        self.assertTrue(db.rounds[1].cup_decisive_tiebreak)
        self.assertFalse(db.rounds[1].cup_extra_time_capable)


if __name__ == "__main__":
    unittest.main()
