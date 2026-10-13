"""Original LeagueMatch source class virtual 0C→PResults pre-count."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack_into,pack
import unittest

from original_presults_native_leaguematch_vtables import (
    SOURCE_ORIGINAL_LEAGUE_MATCH_VTABLES_COMMON,
    SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_VTABLE,
    source_original_league_match_native_precount_node_4a7210,
)
from original_presults_native_event_work import (
    OriginalPResultsEventSourceError,OriginalPResultsNativeDateBucket,
    source_original_presults_precount_4a7210,
)


def match_source(vt=0x7C4C24, *, flags44=0, event8=0, special_pointer=0):
    buf=bytearray(0x58)
    pack_into("<I",buf,0,vt)
    pack_into("<I",buf,8,event8)
    pack_into("<I",buf,0x44,flags44)
    pack_into("<I",buf,0x54,special_pointer)
    return bytes(buf)


def precount(**kw):
    basic=dict(
        original_event_object_pointer=0xAABB00,
        original_match_record_before_v0c=match_source(),
        original_first_club_virtual_result_pointer=0x12345678,
        original_second_club_virtual_result_pointer=0x87654321,
        original_special_owner_record_via_plus54=None,
        original_match_record_after_reached_v0c=match_source(),
    )
    return source_original_league_match_native_precount_node_4a7210(**(basic|kw))


class NativeLeagueMatchPResultsVtableTests(unittest.TestCase):
    def test_common_original_vtables_all_qualify_both_source_clubs(self):
        for vt in SOURCE_ORIGINAL_LEAGUE_MATCH_VTABLES_COMMON:
            with self.subTest(vtable=hex(vt)):
                before=match_source(vt)
                actual=precount(original_match_record_before_v0c=before,
                                original_match_record_after_reached_v0c=before)
                self.assertTrue(actual.source_virtual_0c_nonzero)
                self.assertEqual(actual.reached_event8,0)
                self.assertEqual(actual.reached_payload44,0)
                self.assertEqual(actual.original_event_pointer,0xAABB00)

    def test_native_bit5_early_exit_skips_both_side_getters_and_payload(self):
        for vt in (*SOURCE_ORIGINAL_LEAGUE_MATCH_VTABLES_COMMON,
                   SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_VTABLE):
            got=precount(original_match_record_before_v0c=match_source(vt,flags44=0x20),
                         original_first_club_virtual_result_pointer=None,
                         original_second_club_virtual_result_pointer=None,
                         original_match_record_after_reached_v0c=None)
            self.assertFalse(got.source_virtual_0c_nonzero)
            self.assertIsNone(got.reached_event8)
            self.assertIsNone(got.reached_payload44)

    def test_native_first_club_null_skips_second_and_payload(self):
        got=precount(original_first_club_virtual_result_pointer=0,
                     original_second_club_virtual_result_pointer=None,
                     original_match_record_after_reached_v0c=None)
        self.assertFalse(got.source_virtual_0c_nonzero)
        with self.assertRaises(OriginalPResultsEventSourceError):
            precount(original_first_club_virtual_result_pointer=0,
                     original_second_club_virtual_result_pointer=1,
                     original_match_record_after_reached_v0c=None)

    def test_second_null_skips_payload_but_first_nonnull_is_required(self):
        got=precount(original_second_club_virtual_result_pointer=0,
                     original_match_record_after_reached_v0c=None)
        self.assertFalse(got.source_virtual_0c_nonzero)
        with self.assertRaises(OriginalPResultsEventSourceError):
            precount(original_first_club_virtual_result_pointer=None)

    def test_special_native_owner_bit0_additional_filter_not_a_generic_league_rule(self):
        vt=SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_VTABLE
        before=match_source(vt,special_pointer=0x6000)
        owner=bytearray(0x48)
        after=match_source(vt)
        pack_into("<I",owner,0x44,1)
        result=precount(original_match_record_before_v0c=before,
            original_special_owner_record_via_plus54=bytes(owner),
            original_match_record_after_reached_v0c=after)
        self.assertTrue(result.source_virtual_0c_nonzero)
        pack_into("<I",owner,0x44,2)
        result=precount(original_match_record_before_v0c=before,
            original_special_owner_record_via_plus54=bytes(owner),
            original_match_record_after_reached_v0c=None)
        self.assertFalse(result.source_virtual_0c_nonzero)
        for change in (
            dict(original_special_owner_record_via_plus54=None),
            dict(original_special_owner_record_via_plus54=bytes(0x47)),
            dict(original_match_record_before_v0c=match_source(vt,special_pointer=0)),
        ):
            with self.subTest(change=str(change)[:90]),self.assertRaises(OriginalPResultsEventSourceError):
                precount(**(dict(
                    original_match_record_before_v0c=before,
                    original_special_owner_record_via_plus54=bytes(owner),
                    original_match_record_after_reached_v0c=None)|change))

    def test_reached_event8_reads_payload_only_if_zero(self):
        got=precount(original_match_record_after_reached_v0c=match_source(event8=55))
        self.assertEqual(got.reached_event8,55)
        self.assertIsNone(got.reached_payload44)
        got=precount(original_match_record_after_reached_v0c=match_source(flags44=0x41))
        self.assertEqual(got.reached_payload44,0x41)
        self.assertEqual(source_original_presults_precount_4a7210(
            original_current_date_global_9847fc=100,
            original_inclusive_upper_date=101,
            original_947ad8_date_buckets=(
                OriginalPResultsNativeDateBucket(101,(got,)),),
            original_already_processed_64=4),4)
        with self.assertRaises(OriginalPResultsEventSourceError):
            precount(original_match_record_after_reached_v0c=match_source(0x7C4CE4))

    def test_original_vtable_indirect_source_and_unreached_fields_fail_closed(self):
        for change in (
            dict(original_match_record_before_v0c=match_source(0xDEADBEEF)),
            dict(original_match_record_before_v0c=bytes(0x57)),
            dict(original_match_record_before_v0c=bytearray(match_source())),
            dict(original_event_object_pointer=0),
            dict(original_event_object_pointer=True),
            dict(original_first_club_virtual_result_pointer=True),
            dict(original_second_club_virtual_result_pointer=0x100000000),
            dict(original_special_owner_record_via_plus54=bytes(0x48)),
        ):
            with self.subTest(change=str(change)[:80]), self.assertRaises(OriginalPResultsEventSourceError):
                precount(**change)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),"private original PE not mounted")
    def test_original_native_leaguematch_vtable_and_source_method_signatures(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for vt in SOURCE_ORIGINAL_LEAGUE_MATCH_VTABLES_COMMON|{SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_VTABLE}:
            with self.subTest(vtable=hex(vt)):
                expected=(0x510B00 if vt==SOURCE_ORIGINAL_LEAGUE_MATCH_SPECIAL_VTABLE
                          else 0x510AD0)
                self.assertEqual(pe.read(vt+0xC,4),pack("<I",expected))
                self.assertEqual(pe.read(vt+0x10,4),pack("<I",0x513010))
                self.assertEqual(pe.read(vt+0x18,4),pack("<I",0x6559A0))
        sites={
            0x510ad0:"56",0x510ad3:"8b 46 44",0x510ad6:"c1 e8 05",
            0x510ad9:"a8 01",0x510add:"8b 56 14",
            0x510ae3:"ff 12",0x510ae9:"8b 46 28",
            0x510aef:"ff 10",0x510af5:"b8 01 00 00 00",
            0x510b00:"56",0x510b03:"e8 c8 ff ff ff",
            0x510b0e:"8b 46 54",0x510b12:"8b 40 44",
            0x510b15:"83 e0 01",0x6559a0:"8b c1 c3",
            0x510395:"c7 40 08 00 00 00 00",
            0x512f27:"8b 79 44",0x512f2a:"83 cf 20",
            0x512f2d:"89 79 44",
        }
        for address,hx in sites.items():
            with self.subTest(address=hex(address)):
                self.assertEqual(pe.read(address,len(bytes.fromhex(hx))),bytes.fromhex(hx))


if __name__=="__main__":
    unittest.main()
