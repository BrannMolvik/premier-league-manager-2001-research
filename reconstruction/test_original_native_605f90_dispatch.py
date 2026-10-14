"""Original source 605F90 event subtype/RNG routing and 606540 pre-human tests."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
from struct import pack_into,unpack_from
import hashlib
import os
import unittest

from original_native_41a5b0_extra_event import (
    source_original_41a5b0_optional_extra_from_reached,
)
from test_original_native_41a5b0_extra_event import staged
from original_native_605f90_dispatch import (
    Original605F90SourceError, Original605F90Thresholds,
    Original605F90ReachedCall, Original606540Reached,
    source_original_605f90_select_handler,
    source_original_605f90_predispatch_from_reached,
    source_original_606540_pre_human_from_reached,
)

INIT0=(3,6,12,18,26,34,40,50,60,69,78,84,88,96)
INIT1=(10,20,30,40,50,60,70,80)
INIT2=(10,20,30,40,60)
ADD0=(0x8222c0,0x8222c4,0x8222c8,0x8222cc,0x8222d0,
      0x8222d4,0x8222d8,0x8222dc,0x8222e0,0x8222e4,
      0x8222e8,0x8222ec,0x8222f0,0x8222f8)
ADD1=tuple(range(0x8222fc,0x82231c,4))
ADD2=(0x8222fc,0x822300,0x822304,0x822308,0x822310)


def thresholds(subtype=0,values=None):
    originals={0:(ADD0,INIT0),1:(ADD1,INIT1),2:(ADD2,INIT2)}
    addrs,defaults=originals[subtype]
    return Original605F90Thresholds(addrs,defaults if values is None else values)


def qualified(subtype=1,draw=0):
    original=source_original_41a5b0_optional_extra_from_reached(
        staged(registered=True,source_77=60 if subtype==1 else 90,threshold=75)
    )
    p=bytearray(original.original_player_after_row_at_call)
    pointer=0x50000
    pack_into("<I",p,0x24c,pointer)
    descriptor=bytearray(12)
    pack_into("<I",descriptor,0,0xffffffff)
    descriptor[4]=3
    descriptor[5]=4
    return Original605F90ReachedCall(
        original_caller=original,
        original_allocated_descriptor_pointer=pointer,
        original_descriptor_after_605f70=bytes(descriptor),
        original_player_after_41a5b0_pointer_store=bytes(p),
        original_first_resolved_native_player=bytes(p),
        original_second_resolved_native_player=bytes(p),
        original_rng100_result=draw,
        original_mutable_thresholds=thresholds(subtype),
    )


def predispatched(subtype=1,draw=0):
    return source_original_605f90_predispatch_from_reached(qualified(subtype,draw))


class Original605F90DispatchTests(unittest.TestCase):
    def test_native_subtype_handler_cutoffs_include_equality_and_last_fallback(self):
        examples=[
            (0,0,0x606300),(0,3,0x606540),
            (0,6,0x606d20),(0,95,0x60a3d0),(0,96,0x60a630),
            (1,0,0x606540),(1,9,0x606540),
            (1,10,0x606d20),(1,79,0x6098c0),(1,80,0x609b30),
            (2,9,0x606540),(2,10,0x606d20),
            (2,29,0x6074e0),(2,30,0x607cc0),
            (2,40,0x608a00),(2,60,0x6091e0),
        ]
        for subtype,draw,target in examples:
            with self.subTest(subtype=subtype,draw=draw):
                s=source_original_605f90_select_handler(
                    original_subtype=subtype,original_reached_rng100_result=draw,
                    original_reached_thresholds=thresholds(subtype))
                self.assertEqual(s.original_selected_handler_address,target)
                self.assertEqual(s.original_rng_draws_consumed_through_selector,1)
                self.assertFalse(s.original_handler_executed)
                self.assertFalse(s.live_game_state_mutated)

    def test_native_subtype_zero_reads_8222f8_not_unused_8222f4(self):
        r=source_original_605f90_select_handler(
            original_subtype=0,original_reached_rng100_result=94,
            original_reached_thresholds=thresholds(0))
        self.assertEqual(r.original_selected_handler_address,0x60a3d0)
        self.assertEqual(r.original_native_threshold_addresses[-1],0x8222f8)
        self.assertNotIn(0x8222f4,r.original_native_threshold_addresses)

    def test_mutable_thresholds_use_first_comparison_not_sorted_or_clamped(self):
        source=thresholds(1,(50,10,10,10,10,10,10,10))
        r=source_original_605f90_select_handler(
            original_subtype=1,original_reached_rng100_result=15,
            original_reached_thresholds=source)
        self.assertEqual(r.original_first_matching_threshold_index,0)
        r=source_original_605f90_select_handler(
            original_subtype=2,original_reached_rng100_result=0,
            original_reached_thresholds=thresholds(2,(-5,0,0,101,-12)))
        self.assertEqual(r.original_selected_handler_address,0x607cc0)

    def test_source_allocation_and_repeated_native_getters_two_subtypes(self):
        for subtype,draw in ((0,3),(1,0)):
            with self.subTest(subtype=subtype):
                output=predispatched(subtype,draw)
                self.assertEqual(output.original_player_id,123)
                self.assertEqual(output.original_subtype,subtype)
                self.assertEqual(output.original_descriptor_pointer,0x50000)
                self.assertEqual(unpack_from("<I",output.original_descriptor_at_subhandler_entry,0)[0],0xffffffff)
                self.assertEqual(output.original_descriptor_at_subhandler_entry[4:6],bytes((subtype,4)))
                self.assertEqual(unpack_from("<I",output.original_descriptor_at_subhandler_entry,8)[0],123)
                self.assertEqual((output.original_first_getter_returned_id,
                                  output.original_second_getter_returned_id),(123,123))
                self.assertFalse(output.original_handler_choice.original_handler_executed)
                self.assertFalse(output.original_player24c_lifecycle_complete)
                self.assertFalse(output.original_event_delivery_verified)

    def test_failed_allocation_source_would_deref_null_and_fails_closed(self):
        x=qualified()
        with self.assertRaisesRegex(Original605F90SourceError,"descriptor"):
            source_original_605f90_predispatch_from_reached(
                replace(x,original_allocated_descriptor_pointer=0))
        b=bytearray(x.original_descriptor_after_605f70);b[4]=0
        with self.assertRaisesRegex(Original605F90SourceError,"constructor"):
            source_original_605f90_predispatch_from_reached(
                replace(x,original_descriptor_after_605f70=bytes(b)))
        with self.assertRaisesRegex(Original605F90SourceError,"allocation/store"):
            source_original_605f90_predispatch_from_reached(
                replace(x,original_player_after_41a5b0_pointer_store=x.original_caller.original_player_after_row_at_call))
        with self.assertRaisesRegex(Original605F90SourceError,"player ID mismatch"):
            wrong=bytearray(x.original_second_resolved_native_player)
            pack_into("<H",wrong,4,456)
            source_original_605f90_predispatch_from_reached(
                replace(x,original_second_resolved_native_player=bytes(wrong)))
        with self.assertRaisesRegex(Original605F90SourceError,"source-positive"):
            source_original_605f90_predispatch_from_reached(
                replace(x,original_caller=replace(
                    x.original_caller,
                    original_would_allocate_605f70_and_store_player24c=False,
                    source_branch_complete_without_world_effects=True,
                )))

    def test_outstanding_or_wrong_dynamic_rng_and_threshold_inputs_rejected(self):
        for sub,val in ((0,-1),(0,100),(1,True),(2,101)):
            with self.subTest(sub=sub,val=val):
                with self.assertRaisesRegex(Original605F90SourceError,"RNG"):
                    source_original_605f90_select_handler(
                        original_subtype=sub,original_reached_rng100_result=val,
                        original_reached_thresholds=thresholds(sub))
        with self.assertRaisesRegex(Original605F90SourceError,"address coverage"):
            source_original_605f90_select_handler(
                original_subtype=0,original_reached_rng100_result=20,
                original_reached_thresholds=thresholds(1))
        with self.assertRaisesRegex(Original605F90SourceError,"signed32"):
            source_original_605f90_select_handler(
                original_subtype=0,original_reached_rng100_result=20,
                original_reached_thresholds=thresholds(0,INIT0[:-1]+(1<<40,)))

    def test_606540_short_branch_uses_single_rng_and_no_second_threshold(self):
        p=predispatched(subtype=1,draw=0)
        out=source_original_606540_pre_human_from_reached(
            Original606540Reached(p,10,50,original_82232c_short_base=10))
        self.assertEqual(out.original_source_descriptor_before_417340[5],0)
        self.assertEqual(out.original_schedule_base_from_mutable_source,10)
        self.assertEqual(out.original_schedule_delta_from_rng,1)
        self.assertFalse(out.original_second_rng4_reached)
        self.assertTrue(out.original_handler_417340_callback_outstanding)
        self.assertTrue(out.original_60aa20_descriptor_schedule_callback_outstanding)
        self.assertFalse(out.original_event_pending_or_delivered)

    def test_606540_subtype2_uses_rng75_and_avoids_long_branch(self):
        p=replace(predispatched(subtype=1),original_subtype=2)
        # This test uses a source-qualified dispatch choice for native subtype2.
        choice=source_original_605f90_select_handler(
            original_subtype=2,original_reached_rng100_result=0,
            original_reached_thresholds=thresholds(2))
        # Synthetic subtype2 descriptor for a READ-ONLY selector test.
        # The positive 41A5B0 caller independently supports only 0/1;
        # a real 41A670 subtype2 source caller must be proven separately.
        d=bytearray(p.original_descriptor_at_subhandler_entry);d[4]=2
        p=replace(p,original_handler_choice=choice,
                  original_descriptor_at_subhandler_entry=bytes(d))
        out=source_original_606540_pre_human_from_reached(
            Original606540Reached(
                p,70,50,original_822324_second_threshold=80,
                original_second_rng4_result=3,original_822330_medium_base=35))
        self.assertEqual(out.original_first_rng_bound,75)
        self.assertEqual(out.original_source_descriptor_before_417340[5],1)
        self.assertEqual(out.original_schedule_delta_from_rng,6)

    def test_forged_handler_subtype_without_matching_descriptor_fails(self):
        p=predispatched(subtype=1)
        with self.assertRaisesRegex(Original605F90SourceError,"subtype/descriptor"):
            source_original_606540_pre_human_from_reached(
                Original606540Reached(
                    replace(p,original_subtype=2),0,50,
                    original_82232c_short_base=10))

    def test_606540_medium_and_long_draws_require_exact_native_branches(self):
        p=predispatched(subtype=1,draw=0)
        medium=source_original_606540_pre_human_from_reached(
            Original606540Reached(p,65,50,original_822324_second_threshold=80,
                original_second_rng4_result=0,original_822330_medium_base=35))
        self.assertEqual(medium.original_source_descriptor_before_417340[5],1)
        self.assertEqual(medium.original_schedule_delta_from_rng,3)
        for draw,expected_status in ((85,2),(97,3)):
            out=source_original_606540_pre_human_from_reached(
                Original606540Reached(p,draw,50,
                    original_822324_second_threshold=80,
                    original_822328_third_threshold=95,
                    original_second_rng4_result=2,original_822334_long_base=60))
            self.assertEqual(out.original_source_descriptor_before_417340[5],expected_status)
            self.assertEqual(out.original_schedule_delta_from_rng,13)
        with self.assertRaisesRegex(Original605F90SourceError,"skips"):
            source_original_606540_pre_human_from_reached(
                Original606540Reached(p,0,50,original_822324_second_threshold=80,
                    original_82232c_short_base=10))
        with self.assertRaisesRegex(Original605F90SourceError,"RNG"):
            source_original_606540_pre_human_from_reached(
                Original606540Reached(p,85,50,original_822324_second_threshold=80,
                    original_822328_third_threshold=95,
                    original_822334_long_base=60))
        with self.assertRaisesRegex(Original605F90SourceError,"must choose"):
            source_original_606540_pre_human_from_reached(
                Original606540Reached(predispatched(subtype=0,draw=0),0,50,
                    original_82232c_short_base=10))

    def test_private_original_opcode_and_initial_mutable_globals_if_supplied(self):
        p=os.environ.get("FM2001_ORIGINAL_EXE")
        if not p:
            self.skipTest("original executable is kept private outside GitHub")
        data=Path(p).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
             "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        signatures={
            0x605f70:"8b c1 c7 00 ff ff ff ff",
            0x605f78:"c6 40 04 03",
            0x605f7c:"c6 40 05 04",
            0x605f90:"53 56 8b f1 57",
            0x605fa8:"33 c9 66 8b 48 04",
            0x605fae:"88 5e 04",
            0x605fb1:"89 4e 08",
            0x605fcd:"74 18",
            0x605fd5:"8b ce e8 b4 02 00 00",
            0x605fde:"8b ce e8 0b 02 00 00",
            0x605fe7:"8b ce e8 f2 00 00 00",
            0x605ffb:"e8 40 13 e1 ff",
            0x6060e3:"6a 64 e8 56 74 04 00",
            0x6061f3:"6a 64 e8 46 73 04 00",
            0x606293:"6a 64 e8 a6 72 04 00",
            0x606560:"8a 47 04",
            0x606566:"3c 02",
            0x60656a:"6a 4b",
            0x606580:"7d 13",
            0x606582:"c6 47 05 00",
            0x6065ad:"c6 47 05 02",
            0x6065ef:"c6 47 05 01",
        }
        for va,hexes in signatures.items():
            with self.subTest(va=hex(va)):
                signature=bytes.fromhex(hexes)
                self.assertEqual(data[va-0x400000:va-0x400000+len(signature)],signature)
        initial=INIT0+INIT1
        for addr,value in zip(ADD0+ADD1,initial):
            self.assertEqual(unpack_from("<i",data,addr-0x400000)[0],value)


if __name__=="__main__":
    unittest.main()
