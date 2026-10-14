"""Strict tests for original Type4 pair-family selection and fail-closed bounds."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack, pack_into
import unittest

from original_native_type4_pair_selector import (
    OriginalType4PairSourceError,
    source_original_type4_pair_selection_4f2a78_4faf70,
)


def embedded_type4(*, selector=0, cache=0, owner=0xBEEF0000,
                   type_word=4, vtable=0x7C4D50):
    r = bytearray(0x14)
    pack_into("<I", r, 0, vtable)
    pack_into("<I", r, 4, cache)
    pack_into("<I", r, 8, owner)
    pack_into("<H", r, 0x0C, type_word)
    pack_into("<H", r, 0x0E, selector)
    return bytes(r)


PAIRS_74 = ((0x1001, 0x1002), (0x3001, 0x3002), (0x5001, 0x5002))
PAIRS_7C = ((0x2001, 0x2002), (0x4001, 0x4002), (0x6001, 0x6002))


def run(selector=0, **change):
    args = dict(
        original_embedded_side_ref_before_getter=embedded_type4(selector=selector),
        original_reached_4faea0_al=1,
        original_owner_pairs_74_after_gate=PAIRS_74,
        original_owner_pairs_7c_after_gate=PAIRS_7C,
    )
    return source_original_type4_pair_selection_4f2a78_4faf70(**(args | change))


class OriginalNativeType4PairTests(unittest.TestCase):
    def test_every_source_bit_selection_and_group_index(self):
        for index in range(3):
            for low in range(4):
                selector=(index<<2)|low
                family=0x74 if low&1 else 0x7C
                member=0 if low&2 else 1
                pairs=PAIRS_74 if low&1 else PAIRS_7C
                with self.subTest(selector=selector):
                    result=run(selector)
                    self.assertEqual(result.source_original_pair_family_offset,family)
                    self.assertEqual(result.source_original_pair_index,index)
                    self.assertEqual(result.source_original_pair_member_index,member)
                    self.assertEqual(result.source_original_selected_sidereference_pointer,
                                     pairs[index][member])

    def test_source_gate_fails_before_array_read(self):
        result=run(0xFFFF,
            original_reached_4faea0_al=0,
            original_owner_pairs_74_after_gate=None,
            original_owner_pairs_7c_after_gate=None)
        self.assertEqual(result.source_original_gate_4faea0_al,0)
        self.assertIsNone(result.source_original_selected_sidereference_pointer)
        self.assertIsNone(result.source_original_pair_index)

    def test_unknown_native_inputs_do_not_turn_into_safe_lookups(self):
        for change in (
            dict(original_embedded_side_ref_before_getter=embedded_type4(cache=1)),
            dict(original_embedded_side_ref_before_getter=embedded_type4(owner=0)),
            dict(original_embedded_side_ref_before_getter=embedded_type4(type_word=1)),
            dict(original_embedded_side_ref_before_getter=embedded_type4(vtable=0x7C4D60)),
            dict(original_embedded_side_ref_before_getter=b"bad"),
            dict(original_reached_4faea0_al=None),
            dict(original_reached_4faea0_al=2),
            dict(original_owner_pairs_74_after_gate=None),
            dict(original_owner_pairs_7c_after_gate=((0x1000, 0),)),
            dict(original_owner_pairs_74_after_gate=((0x1111,),)),
            dict(original_owner_pairs_7c_after_gate=[(0x2001,0x2002)]),
        ):
            with self.subTest(change=repr(change)[:110]):
                with self.assertRaises(OriginalType4PairSourceError):
                    run(**change)
        for selector in (12,0xFFFC,0xFFFF):
            with self.subTest(selector=selector):
                with self.assertRaises(OriginalType4PairSourceError):
                    run(selector)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "original private executable deliberately not distributed in hosted CI")
    def test_original_private_x86_control_flow_matches_bounded_selector(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x4F2A78:"8b 4e 08",
            0x4F2A7B:"e8 20 84 00 00",
            0x4F2A80:"84 c0",
            0x4F2A88:"8a 56 0e",
            0x4F2A91:"80 e2 01",
            0x4F2A96:"d1 e8",
            0x4F2A98:"c1 e9 02",
            0x4F2A9B:"83 e0 01",
            0x4F2AA4:"e8 c7 84 00 00",
            0x4FAF70:"8a 44 24 04",
            0x4FAF74:"84 c0",
            0x4FAF78:"8b 41 74",
            0x4FAF84:"8b 51 7c",
            0x4FAF8E:"8b 54 24 08",
            0x4FAF92:"8b 01",
            0x4FAF94:"8b 49 04",
            0x4FAF97:"85 d2",
            0x4FAF9B:"8b c1",
            0x4FAF9D:"c2 0c 00",
        }
        for addr,opcode in sites.items():
            with self.subTest(va=hex(addr)):
                self.assertEqual(pe.read(addr,len(bytes.fromhex(opcode))),
                                 bytes.fromhex(opcode))


if __name__=="__main__":
    unittest.main()
