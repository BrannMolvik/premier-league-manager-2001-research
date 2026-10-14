"""Original 0x615950 native direct event +4/+10 linked-date slot writes."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack,pack_into,unpack_from
import unittest

from original_native_dated_event_insert_source import (
    OriginalNativeDatedEventInsertionSourceError,
    source_original_leaguematch_insert_into_reached_native_date_bucket_615950,
)


def source_match(vt=0x7C4C24,identity=0):
    buf=bytearray(b"\x7e"*0x58)
    pack_into("<I",buf,0,vt)
    pack_into("<I",buf,0x0C,identity)
    pack_into("<I",buf,4,0)
    pack_into("<I",buf,0x10,0xFFFFFFFF)
    return bytes(buf)


def insert(**kwargs):
    params=dict(
        original_source_match_event_pointer=0x405000,
        original_source_match_record_before_insert=source_match(),
        original_reached_dated_collection_pointer=0x947AD8,
        original_reached_collection_base_bucket_pointer=0x102000,
        original_reached_date_bucket_slot_pointer=0x102008,
        original_reached_source_collection_bucket_count=5,
        original_reached_slot_prior_head_pointer=0x406000,
    )
    return source_original_leaguematch_insert_into_reached_native_date_bucket_615950(
        **(params|kwargs))


class NativeOriginalDatedEventInsertSourceTests(unittest.TestCase):
    def test_match_vtable_self_payload_native_linked_head_and_bucket_index(self):
        for vt in (0x7C4C24,0x7C4CE4,0x7C9D9C,0x7C9E14,
                   0x7C9E80,0x7C9EF8):
            with self.subTest(vtable=hex(vt)):
                before=source_match(vt)
                got=insert(original_source_match_record_before_insert=before)
                after=got.original_native_event_record_after_insert
                self.assertEqual(got.original_native_event_date_bucket_index_10,2)
                self.assertEqual(got.original_source_slot_prior_head_event_pointer,0x406000)
                self.assertEqual(got.original_source_slot_new_head_event_pointer,0x405000)
                self.assertEqual(unpack_from("<I",after,4)[0],0x406000)
                self.assertEqual(unpack_from("<I",after,0x10)[0],2)
                self.assertEqual(after[:4],before[:4])
                self.assertEqual(after[8:0x10],before[8:0x10])
                self.assertEqual(after[0x14:],before[0x14:])

    def test_original_event_bit0_selects_actual_secondary_date_array(self):
        for identity in (1,3,0xFFFFFFFF):
            with self.subTest(identity=identity):
                rec=source_match(0x7C9F70,identity)
                got=insert(
                    original_source_match_record_before_insert=rec,
                    original_reached_dated_collection_pointer=0x947AF0,
                    original_reached_date_bucket_slot_pointer=0x102000,
                    original_reached_slot_prior_head_pointer=0)
                self.assertEqual(got.original_native_event_id_dword_0c,identity)
                self.assertEqual(got.original_selected_collection_pointer,0x947AF0)
                self.assertEqual(got.original_native_event_date_bucket_index_10,0)
                self.assertEqual(unpack_from("<I",got.original_native_event_record_after_insert,4)[0],0)

    def test_actual_native_second_insertion_head_prepends_existing_node(self):
        first=insert(original_reached_slot_prior_head_pointer=0)
        second=insert(original_source_match_event_pointer=0x407000,
                      original_reached_slot_prior_head_pointer=first.original_source_slot_new_head_event_pointer)
        self.assertEqual(first.original_source_slot_new_head_event_pointer,0x405000)
        self.assertEqual(second.original_source_slot_prior_head_event_pointer,0x405000)
        self.assertEqual(second.original_source_slot_new_head_event_pointer,0x407000)
        self.assertEqual(unpack_from("<I",second.original_native_event_record_after_insert,4)[0],0x405000)

    def test_no_premature_native_pointer_aliases_or_unqualified_slots(self):
        cases=(
            dict(original_source_match_record_before_insert=bytes(0x13)),
            dict(original_source_match_record_before_insert=bytearray(source_match())),
            dict(original_source_match_record_before_insert=source_match(0xDEADBEEF)),
            dict(original_source_match_event_pointer=0),
            dict(original_source_match_event_pointer=True),
            dict(original_reached_dated_collection_pointer=0x947AE0),
            dict(original_reached_dated_collection_pointer=True),
            dict(original_reached_dated_collection_pointer=0x947AF0),
            dict(original_reached_collection_base_bucket_pointer=0),
            dict(original_reached_collection_base_bucket_pointer=True),
            dict(original_reached_collection_base_bucket_pointer=0x100000000),
            dict(original_reached_date_bucket_slot_pointer=0x101FFC),
            dict(original_reached_date_bucket_slot_pointer=0x102001),
            dict(original_reached_date_bucket_slot_pointer=0x102014),
            dict(original_reached_date_bucket_slot_pointer=0x100000000),
            dict(original_reached_source_collection_bucket_count=0),
            dict(original_reached_source_collection_bucket_count=-1),
            dict(original_reached_source_collection_bucket_count=2),
            dict(original_reached_source_collection_bucket_count=0x100000000),
            dict(original_reached_slot_prior_head_pointer=-1),
            dict(original_reached_slot_prior_head_pointer=True),
        )
        for change in cases:
            with self.subTest(change=str(change)[:85]),self.assertRaises(
                OriginalNativeDatedEventInsertionSourceError):
                insert(**change)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "owner-private original PE not mounted for hosted CI")
    def test_exact_original_native_slot_index_and_link_source_opcodes(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x615A26:"8b 17",
            0x615A2F:"ff 50 18",
            0x615A34:"e8 c7 a8 ef ff",
            0x615A39:"8b 10",
            0x615A3D:"2b ca",
            0x615A40:"c1 f9 02",
            0x615A43:"89 4b 10",
            0x615A46:"8b 16",
            0x615A48:"89 53 04",
            0x615A4B:"89 1e",
        }
        for va,hx in sites.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


if __name__=="__main__":
    unittest.main()
