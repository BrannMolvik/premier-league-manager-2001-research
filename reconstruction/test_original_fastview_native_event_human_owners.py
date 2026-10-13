"""Original 0x510C30 source human event pointer comparison, 2–6 humans."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack_into
import unittest

from original_fastview_native_event_human_owners import (
    OriginalFastViewHumanEventSourceError,
    source_fastview_original_human_event_510c30,
    source_fastview_original_selected_event_both_human_51fb1c,
)
from original_fastview_native_event_selection import (
    OriginalFastViewNativeLinkedEventCandidate,
    OriginalFastViewEventCollectionSourceError,
    source_fastview_original_standard_event_members_51fa70,
)


class OriginalFastViewEventHumanOwnerSourceTests(unittest.TestCase):
    @staticmethod
    def args():
        return dict(
            original_human_count_global_8755e4=3,
            original_manager_club_pointers_by_413b10_index=(
                0x100100,0x200200,0x300300),
            original_event_first_club_pointer=0xDEAD,
            original_event_second_club_pointer=0x300300,
        )

    def test_callback_any_registered_human_not_just_first_manager(self):
        args=self.args()
        got=source_fastview_original_human_event_510c30(**args)
        self.assertTrue(got.original_callback_510c30_nonzero)
        self.assertEqual(got.first_matching_original_human_ordinal,2)
        self.assertEqual(got.matched_event_club_ordinal,1)
        left=source_fastview_original_human_event_510c30(**(args|{
            "original_event_first_club_pointer":0x200200,
            "original_event_second_club_pointer":0x200200,
        }))
        self.assertEqual((left.first_matching_original_human_ordinal,left.matched_event_club_ordinal),(1,0))
        none=source_fastview_original_human_event_510c30(**(args|{
            "original_event_first_club_pointer":0xDEAD,
            "original_event_second_club_pointer":0xBEEF,
        }))
        self.assertFalse(none.original_callback_510c30_nonzero)
        self.assertIsNone(none.first_matching_original_human_ordinal)

    def test_first_manager_first_club_match_skips_unreached_second_getter(self):
        args=self.args()|{
            "original_event_first_club_pointer":0x100100,
            "original_event_second_club_pointer":None,
        }
        got=source_fastview_original_human_event_510c30(**args)
        self.assertEqual(
            (got.first_matching_original_human_ordinal,got.matched_event_club_ordinal),
            (0,0))
        # First-club match with manager 2 cannot omit the second accessor:
        # managers 0/1 would have accessed the second club before reaching 2.
        with self.assertRaises(OriginalFastViewHumanEventSourceError):
            source_fastview_original_human_event_510c30(
                **(args|{"original_event_first_club_pointer":0x300300}))
        for bad in (0,True,0x100000000):
            with self.subTest(second=bad):
                first=source_fastview_original_human_event_510c30(
                    **(args|{"original_event_second_club_pointer":bad}))
                self.assertEqual(first.first_matching_original_human_ordinal,0)

    def test_zero_or_six_humans_and_duplicate_club_pointer_source_order(self):
        args=self.args()
        self.assertFalse(source_fastview_original_human_event_510c30(
            original_human_count_global_8755e4=0,
            original_manager_club_pointers_by_413b10_index=(),
            original_event_first_club_pointer=None,
            original_event_second_club_pointer=None
        ).original_callback_510c30_nonzero)
        humans=tuple(0x100000+i*100 for i in range(6))
        six=source_fastview_original_human_event_510c30(
            original_human_count_global_8755e4=6,
            original_manager_club_pointers_by_413b10_index=humans,
            original_event_first_club_pointer=5,
            original_event_second_club_pointer=humans[-1])
        self.assertTrue(six.original_callback_510c30_nonzero)
        self.assertEqual(six.first_matching_original_human_ordinal,5)
        dup=source_fastview_original_human_event_510c30(
            original_human_count_global_8755e4=3,
            original_manager_club_pointers_by_413b10_index=(55,99,55),
            original_event_first_club_pointer=99,
            original_event_second_club_pointer=55)
        self.assertEqual((dup.first_matching_original_human_ordinal,dup.matched_event_club_ordinal),(0,1))

    def test_original_event_human_matching_is_pointer_not_numeric_id_or_name(self):
        args=self.args()
        # Different native object pointers, even for logically same club ID,
        # must not be considered equivalent by 0x510C30.
        out=source_fastview_original_human_event_510c30(**(args|{
            "original_event_first_club_pointer":0x100101,
            "original_event_second_club_pointer":0x200201,
        }))
        self.assertFalse(out.original_callback_510c30_nonzero)
        # Original selected event instead uses the 0x4037B0 club ID test:
        self.assertTrue(source_fastview_original_selected_event_both_human_51fb1c(
            original_event_first_club_id_from_getter=12,
            original_event_second_club_id_from_getter=25,
            original_human_manager_club_ids_in_link_order=(99,12,25)))
        self.assertFalse(source_fastview_original_selected_event_both_human_51fb1c(
            original_event_first_club_id_from_getter=12,
            original_event_second_club_id_from_getter=25,
            original_human_manager_club_ids_in_link_order=(12,)))
        self.assertFalse(source_fastview_original_selected_event_both_human_51fb1c(
            original_event_first_club_id_from_getter=12,
            original_event_second_club_id_from_getter=None,
            original_human_manager_club_ids_in_link_order=()))
        with self.assertRaises(OriginalFastViewHumanEventSourceError):
            source_fastview_original_selected_event_both_human_51fb1c(
                original_event_first_club_id_from_getter=12,
                original_event_second_club_id_from_getter=25,
                original_human_manager_club_ids_in_link_order=())

    def test_source_510c30_callback_controls_real_linked_event_append(self):
        args=self.args()
        def rec(pointer,club1,club2,selected=False):
            buf=bytearray(0x50)
            pack_into("<I",buf,0x4C,777)
            pack_into("<H",buf,0x40,1)
            return OriginalFastViewNativeLinkedEventCandidate(
                pointer,bytes(buf),(b"Selected\0" if selected else b"Linked\0"),
                None if selected else source_fastview_original_human_event_510c30(
                    **(args|{"original_event_first_club_pointer":club1,
                             "original_event_second_club_pointer":club2})).original_callback_510c30_nonzero)
        named=source_fastview_original_standard_event_members_51fa70(
            original_selected_event_pointer=101,
            original_selected_event_owner_pointer_plus4c=777,
            original_selected_event_indirect_name_nul=b"Selected\0",
            original_linked_candidate_events=(
                rec(101,0x100100,0x200200,selected=True),
                rec(202,0xDEAD,0x300300),
                rec(303,0xDEAD,0xBEEF),
            ))
        self.assertEqual(named,((101,b"Selected\0"),(303,b"Linked\0")))

    def test_missing_original_linked_club_identity_fails_closed(self):
        args=self.args()
        changes=(
            {"original_human_count_global_8755e4":7},
            {"original_human_count_global_8755e4":True},
            {"original_human_count_global_8755e4":-1},
            {"original_manager_club_pointers_by_413b10_index":(1,2)},
            {"original_manager_club_pointers_by_413b10_index":[1,2,3]},
            {"original_manager_club_pointers_by_413b10_index":(1,True,3)},
            {"original_manager_club_pointers_by_413b10_index":(1,0,3)},
            {"original_event_first_club_pointer":None},
            {"original_event_second_club_pointer":0},
            {"original_event_second_club_pointer":0x100000000},
        )
        for change in changes:
            with self.subTest(change=str(change)), self.assertRaises(OriginalFastViewHumanEventSourceError):
                source_fastview_original_human_event_510c30(**(args|change))
        with self.assertRaises(OriginalFastViewHumanEventSourceError):
            source_fastview_original_human_event_510c30(
                original_human_count_global_8755e4=0,
                original_manager_club_pointers_by_413b10_index=(),
                original_event_first_club_pointer=1,
                original_event_second_club_pointer=2)
        with self.assertRaises(ValueError):
            source_fastview_original_selected_event_both_human_51fb1c(
                original_event_first_club_id_from_getter=True,
                original_event_second_club_id_from_getter=2,
                original_human_manager_club_ids_in_link_order=(2,))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "authenticated private original executable not mounted")
    def test_original_event_human_pointer_and_special_early_exit_opcode_signatures(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x510c30:"a1 e4 55 87 00",
            0x510c3b:"85 c0",0x510c3f:"74 34",
            0x510c41:"8d 7d 14",0x510c44:"53",
            0x510c45:"b9 10 4c 87 00",
            0x510c4a:"e8 c1 2e f0 ff",
            0x510c4f:"8b b0 b4 05 00 00",
            0x510c55:"8b 07",0x510c59:"ff 10",
            0x510c5b:"3b c6",0x510c5d:"74 1d",
            0x510c5f:"8b 55 28",0x510c65:"ff 12",
            0x510c67:"3b c6",0x510c69:"74 11",
            0x510c6b:"a1 e4 55 87 00",
            0x510c70:"43",0x510c71:"3b d8",
            0x510c78:"32 c0",0x510c7f:"b0 01",
            0x413b10:"8b 81 cc 09 00 00",
            0x413b1c:"8b 4c 24 04",
            0x413b24:"8b 40 04",
            0x413b31:"8b 00",
            0x51fb1c:"8b 53 14",
            0x51fb26:"e8 85 3c ee ff",
            0x51fb2f:"8b 43 28",
            0x51fb39:"e8 72 3c ee ff",
            0x51fb42:"c6 44 24 23 00",
            0x51fb50:"e8 db 10 ff ff",
            0x51fb59:"c6 44 24 23 00",
            0x51fb60:"66 83 7b 40 ff",
            0x51fb65:"0f 84 cc 00 00 00",
            0x51fc37:"8d 4b 14",
            0x51fccd:"e9 0c 15 00 00",
        }
        for va,hx in sites.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))
