"""Original native Static and club-group routing; no hidden random choice."""
import unittest
from dataclasses import replace

from fm2001_data import Club
from original_supportstart_name_group_source import (
    OriginalNameGroupError,
    ORIGINAL_COUNTRY_COUNT,
    ORIGINAL_NAME_GROUP_FALLBACK,
    ORIGINAL_STATIC_SHA256,
    parse_original_static_name_group_tables,
    source_original_name_group_route,
)


def fixture_static_bytes():
    from struct import pack_into
    data=bytearray(0x25E0)
    pack_into("<I",data,0x4A,209)
    for i in range(209):
        pack_into("<I",data,0x4E+i*43+6,i)
    pack_into("<I",data,0x4E+199*43+6,0xFFFFFFFF)
    pack_into("<I",data,0x2369,209)
    for i in range(209):
        pack_into("<BH",data,0x236D+i*3,i,634+i)
    return bytes(data)


def club(i, country):
    # Source record's exact name fields are irrelevant to the group counter.
    return Club(i,"source name", "source abbreviation", "stadium", 0, 0, country)


class OriginalNameGroupTests(unittest.TestCase):
    def setUp(self):
        self.table = parse_original_static_name_group_tables(
            fixture_static_bytes(),require_original_sha256=False)
        self.clubs=tuple(club(i,1 if i<11 else (26 if i<21 else 0))
                         for i in range(1246))

    def test_source_country_map_is_not_assumed_identity_and_199_uses_26(self):
        self.assertEqual(self.table.group_records_offset,0x236D)
        self.assertEqual(len(self.table.country_to_group),ORIGINAL_COUNTRY_COUNT)
        self.assertEqual(self.table.resolved_name_group(199),26)
        self.assertEqual(self.table.resolved_name_group(84),84)
        self.assertEqual(self.table.serialized_group_labels[208],842)

    def test_source_club_threshold_requires_strictly_greater_than_ten(self):
        first=source_original_name_group_route(
            self.table,country_index=1,source_clubs=self.clubs,
            original_global_player_count=30064)
        self.assertEqual(first.candidate_source,"country_clubs")
        self.assertEqual(first.source_record_positions,tuple(range(11)))
        self.assertEqual(first.original_group_club_count,11)
        fallback=source_original_name_group_route(
            self.table,country_index=199,source_clubs=self.clubs,
            original_global_player_count=30064)
        self.assertEqual(fallback.resolved_group_id,26)
        self.assertEqual(fallback.original_group_club_count,10)
        self.assertEqual(fallback.candidate_source,"global_players")
        self.assertEqual(fallback.source_record_positions,())

    def test_untrusted_or_missing_source_fails_closed(self):
        fixture=fixture_static_bytes()
        with self.assertRaisesRegex(OriginalNameGroupError,"checksum"):
            parse_original_static_name_group_tables(fixture)
        for data in (fixture[:0x236D],fixture[:0x4A], b""):
            with self.assertRaises(OriginalNameGroupError):
                parse_original_static_name_group_tables(data,require_original_sha256=False)
        for bad in (-1,209,True,None):
            with self.subTest(country=bad):
                with self.assertRaises(OriginalNameGroupError):
                    self.table.resolved_name_group(bad)
        with self.assertRaises(OriginalNameGroupError):
            source_original_name_group_route(
                self.table,country_index=1,
                source_clubs=self.clubs[:-1],original_global_player_count=30064)
        with self.assertRaises(OriginalNameGroupError):
            source_original_name_group_route(
                self.table,country_index=1,
                source_clubs=self.clubs,original_global_player_count=1612)


if __name__=="__main__":
    unittest.main()
