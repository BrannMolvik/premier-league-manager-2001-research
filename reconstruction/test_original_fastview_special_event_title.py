"""Original shipped 0x51FC37 reached event header text and early return."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack_into
import unittest

from original_fastview_special_event_title import (
    OriginalFastViewSpecialTitleError,
    source_fastview_original_special_event_title_51fc37,
)


def original_special_event_record():
    record=bytearray(b"\xA1"*0x50)
    pack_into("<H",record,0x40,0xFFFF)
    return bytes(record)


class OriginalFastViewSpecialTitleSourceTests(unittest.TestCase):
    def test_original_two_club_native_literal_and_early_exit(self):
        rec=original_special_event_record()
        got=source_fastview_original_special_event_title_51fc37(
            original_candidate_event_record=rec,
            original_event_first_club_indirect_title_nul=b"First Club\0unused",
            original_event_second_club_indirect_title_nul=b"Other Club\0ignored")
        self.assertEqual(got.original_resolved_title_nul,b"First Club v Other Club\0")
        self.assertEqual(got.native_local_flag_2b4_after,0)
        self.assertTrue(got.native_control_exits_to_5211de)
        self.assertEqual(rec[0x40:0x42],b"\xFF\xFF")

    def test_original_names_are_bytes_and_case_exact_including_empty_strings(self):
        for first,second,expected in (
            (b"\0",b"\0",b" v \0"),
            (b"\x80\xff\0",b"Az\0",b"\x80\xff v Az\0"),
            (b"club\0",b"CLUB\0",b"club v CLUB\0"),
        ):
            with self.subTest(first=first,second=second):
                got=source_fastview_original_special_event_title_51fc37(
                    original_candidate_event_record=original_special_event_record(),
                    original_event_first_club_indirect_title_nul=first,
                    original_event_second_club_indirect_title_nul=second)
                self.assertEqual(got.original_resolved_title_nul,expected)

    def test_unreached_special_and_unknown_original_indirect_club_fail_closed(self):
        args=dict(original_candidate_event_record=original_special_event_record(),
                  original_event_first_club_indirect_title_nul=b"A\0",
                  original_event_second_club_indirect_title_nul=b"B\0")
        invalid=(
            dict(original_candidate_event_record=bytes(0x41)),
            dict(original_candidate_event_record=bytearray(args["original_candidate_event_record"])),
            dict(original_candidate_event_record=bytes(0x50)),
            dict(original_event_first_club_indirect_title_nul=None),
            dict(original_event_first_club_indirect_title_nul=b"A"),
            dict(original_event_second_club_indirect_title_nul=None),
            dict(original_event_second_club_indirect_title_nul=bytearray(b"B\0")),
        )
        for change in invalid:
            with self.subTest(change=repr(change)[:80]),self.assertRaises(OriginalFastViewSpecialTitleError):
                source_fastview_original_special_event_title_51fc37(**(args|change))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),"original private PE not mounted")
    def test_original_51fc37_exact_machine_calls_and_original_literal_bytes(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        checks={
            0x51fb60:"66 83 7b 40 ff",0x51fb65:"0f 84 cc 00 00 00",
            0x51fc37:"8d 4b 14",0x51fc3a:"c6 85 b4 02 00 00 00",
            0x51fc41:"8b 01",0x51fc43:"ff 10",
            0x51fc45:"8b 48 0c",
            0x51fc50:"6a 01",0x51fc67:"e8 f4 f2 ee ff",
            0x51fc8d:"bf 54 97 82 00",
            0x51fc9d:"68 54 97 82 00",
            0x51fca4:"e8 47 6e 00 00",
            0x51fca9:"8b 53 28",
            0x51fcaf:"8b cb",0x51fcb1:"ff 12",
            0x51fcb3:"8b 40 0c",
            0x51fcc8:"e8 23 6e 00 00",
            0x51fccd:"e9 0c 15 00 00",
            0x829754:"20 76 20 00",
        }
        for va,hx in checks.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


if __name__=="__main__":
    unittest.main()
