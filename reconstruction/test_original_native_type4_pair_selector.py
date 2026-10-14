"""Strict tests for original Type4 pair-family selection and fail-closed bounds."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack, pack_into
import unittest

from procedural_league import materialize_scot_premier_split_match_emissions

from original_native_type4_pair_selector import (
    OriginalType4PairSourceError,
    source_original_type4_pair_selection_4f2a78_4faf70,
    source_original_type4_owner_read_only_gate_4faea0,
    source_original_type4_classify_reached_pairs_before_617500_4faea0,
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



def owner_state(*, team_count=12, raw68=31, raw78=0, raw70=0, source6c=0):
    r=bytearray(0x84)
    pack_into("<i",r,0x3C,team_count)
    pack_into("<i",r,0x68,raw68)
    pack_into("<i",r,0x78,raw78)
    pack_into("<i",r,0x70,raw70)
    pack_into("<I",r,0x6C,source6c)
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

    def test_real_reconstruction_scot_split_selectors_match_original_native_bit_routing(self):
        # Current normal Scottish split emission contract, not proof of
        # original 4FAEA0 postgate ranking/world state or real pointers.
        emissions=materialize_scot_premier_split_match_emissions(12,38)
        self.assertEqual(len(emissions),30)
        top=tuple((0x100000+8*i,0x100004+8*i) for i in range(15))
        bottom=tuple((0x200000+8*i,0x200004+8*i) for i in range(15))
        self.assertEqual({e.split_group for e in emissions},{"top","bottom"})
        for emission in emissions:
            family=0x74 if emission.split_group=="top" else 0x7C
            for side,selector in enumerate((
                emission.participant_0_selector,emission.participant_1_selector)):
                with self.subTest(group=emission.split_group,slot=emission.pair_index,
                                  side=side):
                    got=source_original_type4_pair_selection_4f2a78_4faf70(
                        original_embedded_side_ref_before_getter=embedded_type4(
                            selector=selector),
                        original_reached_4faea0_al=1,
                        original_owner_pairs_74_after_gate=top,
                        original_owner_pairs_7c_after_gate=bottom)
                    source_pair=(top if emission.split_group=="top" else bottom)[
                        emission.pair_index]
                    self.assertEqual(got.source_original_pair_family_offset,family)
                    self.assertEqual(got.source_original_pair_index,emission.pair_index)
                    self.assertEqual(got.source_original_selected_sidereference_pointer,
                                     source_pair[0 if side==0 else 1])

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

    def test_source_read_only_4faea0_gate_signed_half_times_half_minus_one(self):
        # Canonical 12 teams: native 0x4FAEA0 computes 6*5=30.
        too_early=source_original_type4_owner_read_only_gate_4faea0(
            original_native_league_owner_record_before_gate=owner_state(raw68=31))
        self.assertEqual(too_early.source_half_team_count_trunc_toward_zero,6)
        self.assertEqual(too_early.source_gate_threshold_half_times_half_minus_one,30)
        self.assertEqual(too_early.source_4faea0_al_if_no_mutating_callback,0)
        self.assertIsNone(too_early.source_owner_raw_78)
        self.assertFalse(too_early.source_requires_mutating_split_array_initialization)

        at_threshold=source_original_type4_owner_read_only_gate_4faea0(
            original_native_league_owner_record_before_gate=owner_state(raw68=30,raw78=0))
        self.assertIsNone(at_threshold.source_4faea0_al_if_no_mutating_callback)
        self.assertTrue(at_threshold.source_requires_mutating_split_array_initialization)

        initialized=source_original_type4_owner_read_only_gate_4faea0(
            original_native_league_owner_record_before_gate=owner_state(raw68=30,raw78=2))
        self.assertEqual(initialized.source_4faea0_al_if_no_mutating_callback,1)
        self.assertFalse(initialized.source_requires_mutating_split_array_initialization)

        # Odd positive team counts use native signed divide-by-two truncation.
        odd=source_original_type4_owner_read_only_gate_4faea0(
            original_native_league_owner_record_before_gate=owner_state(
                team_count=13,raw68=29,raw78=1))
        self.assertEqual(odd.source_gate_threshold_half_times_half_minus_one,30)
        self.assertEqual(odd.source_4faea0_al_if_no_mutating_callback,1)

    def test_owner_gate_refuses_unproven_overflow_or_nonoriginal_inputs(self):
        for value in (None,b"",bytearray(owner_state()),
                      owner_state(team_count=3),
                      owner_state(team_count=0),
                      owner_state(team_count=-100),
                      owner_state(team_count=65536)):
            with self.subTest(value=str(value)[:60]):
                with self.assertRaises(OriginalType4PairSourceError):
                    source_original_type4_owner_read_only_gate_4faea0(
                        original_native_league_owner_record_before_gate=value)

    def test_4faea0_rank_classification_stages_both_original_pair_arrays(self):
        # Native original +6C order and exact reached rank EAX per pointer.
        pairs=((0x1000,0x1001),(0x2000,0x2001),
               (0x3000,0x3001),(0x4000,0x4001))
        ranks=((0,5),(6,11),(5,6),(1,1))
        got=source_original_type4_classify_reached_pairs_before_617500_4faea0(
            original_native_league_owner_record_before_gate=owner_state(
                raw68=30,raw78=0,raw70=4,source6c=0xABCD),
            original_source_6c_pairs_before_gate=pairs,
            original_reached_4f40b0_rank_pair_eax_in_iteration_order=ranks)
        self.assertEqual(got.source_original_top_pairs_74_before_617500,
                         (pairs[0],pairs[3]))
        self.assertEqual(got.source_original_bottom_pairs_7c_before_617500,
                         (pairs[1],))
        self.assertEqual(got.source_original_cross_half_pair_count,1)
        self.assertTrue(got.source_original_617500_sort_and_side_effects_unresolved)

    def test_4faea0_pre_sort_replay_rejects_mismatched_or_guessed_native_owner_inputs(self):
        pair=((0x1000,0x2000),)
        valid=dict(
            original_native_league_owner_record_before_gate=owner_state(
                raw68=30,raw78=0,raw70=1,source6c=0xAAAA),
            original_source_6c_pairs_before_gate=pair,
            original_reached_4f40b0_rank_pair_eax_in_iteration_order=((1,2),),
        )
        for mutation in (
            dict(original_native_league_owner_record_before_gate=owner_state(
                raw68=31,raw78=0,raw70=1,source6c=0xAAAA)),
            dict(original_native_league_owner_record_before_gate=owner_state(
                raw68=30,raw78=1,raw70=1,source6c=0xAAAA)),
            dict(original_native_league_owner_record_before_gate=owner_state(
                raw68=30,raw78=0,raw70=1,source6c=0)),
            dict(original_native_league_owner_record_before_gate=owner_state(
                raw68=30,raw78=0,raw70=2,source6c=0xAAAA)),
            dict(original_reached_4f40b0_rank_pair_eax_in_iteration_order=()),
            dict(original_reached_4f40b0_rank_pair_eax_in_iteration_order=((1,True),)),
            dict(original_source_6c_pairs_before_gate=((0,0x2000),)),
            dict(original_source_6c_pairs_before_gate=[(0x1000,0x2000)]),
        ):
            with self.subTest(change=repr(mutation)[:110]):
                with self.assertRaises(OriginalType4PairSourceError):
                    source_original_type4_classify_reached_pairs_before_617500_4faea0(
                        **(valid|mutation))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "original private executable deliberately not distributed in hosted CI")
    def test_original_private_x86_control_flow_matches_bounded_selector(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x4FAEDB:"8b 56 6c",
            0x4FAEE0:"8b 3c da",
            0x4FAEE8:"e8 c3 91 ff ff",
            0x4FAEF6:"0f 9d 44 24 17",
            0x4FAEFB:"e8 b0 91 ff ff",
            0x4FAF0A:"0f 9d c0",
            0x4FAF15:"8b 46 78",
            0x4FAF1B:"89 3c c1",
            0x4FAF2F:"8b 96 80 00 00 00",
            0x4FAF38:"89 3c d0",
            0x4FAEA6:"8b 46 3c",
            0x4FAEAA:"2b c2",
            0x4FAEAC:"d1 f8",
            0x4FAEB2:"8d 48 ff",
            0x4FAEB5:"0f af c8",
            0x4FAEB8:"3b 4e 68",
            0x4FAEBB:"7d 07",
            0x4FAEBD:"32 c0",
            0x4FAEC4:"8b 46 78",
            0x4FAEC9:"0f 85 9a 00 00 00",
            0x4FAF56:"6a 01",
            0x4FAF5A:"e8 a1 c5 11 00",
            0x4FAF5F:"6a 00",
            0x4FAF63:"e8 98 c5 11 00",
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
