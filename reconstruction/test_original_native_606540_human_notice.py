"""Source 606540 human notice: three independent native lookup families.

Private original executable optional SHA/opcode/jump-table checks; no original
game run, native notice construction, delivered mail or GameState mutation.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from struct import pack_into,unpack_from
import hashlib
import os
import unittest

from original_native_605f90_dispatch import (
    Original606540Reached, source_original_606540_pre_human_from_reached,
    source_original_605f90_select_handler,
)
from original_native_606540_human_notice import (
    Original606540HumanNoticeReached,Original606540HumanNoticeSourceError,
    source_original_606540_human_notice_plan,
)
from test_original_native_605f90_dispatch import (
    predispatched,qualified,thresholds,
)
from test_original_native_41a5b0_extra_event import manager_proof


def notice(*,first=True,second=None,status=0,subtype=1):
    if subtype==2:
        # ONLY a synthetic selector exercise. The independent 41A670 native
        # caller which can reach subtype2 is not qualified by 41A5B0.
        p=predispatched(subtype=1,draw=0)
        selected=source_original_605f90_select_handler(
            original_subtype=2,original_reached_rng100_result=0,
            original_reached_thresholds=thresholds(2))
        desc=bytearray(p.original_descriptor_at_subhandler_entry); desc[4]=2
        p=replace(p,original_subtype=2,original_handler_choice=selected,
                  original_descriptor_at_subhandler_entry=bytes(desc))
        raw=qualified(subtype=1,draw=0).original_player_after_41a5b0_pointer_store
    else:
        p=predispatched(subtype=subtype,draw=(3 if subtype==0 else 0))
        raw=qualified(subtype=subtype,draw=(3 if subtype==0 else 0)).original_player_after_41a5b0_pointer_store
    if status==0:
        kw=dict(original_first_rng_result=10,original_822320_first_threshold=50,
                original_82232c_short_base=10)
    elif status==1:
        kw=dict(original_first_rng_result=65,original_822320_first_threshold=50,
                original_822324_second_threshold=80,original_second_rng4_result=0,
                original_822330_medium_base=35)
    elif status==2:
        kw=dict(original_first_rng_result=85,original_822320_first_threshold=50,
                original_822324_second_threshold=80,original_822328_third_threshold=95,
                original_second_rng4_result=0,original_822334_long_base=60)
    else:
        kw=dict(original_first_rng_result=97,original_822320_first_threshold=50,
                original_822324_second_threshold=80,original_822328_third_threshold=95,
                original_second_rng4_result=0,original_822334_long_base=60)
    h=source_original_606540_pre_human_from_reached(Original606540Reached(
        p,**kw))
    return Original606540HumanNoticeReached(
        original_predispatch=p,
        original_prehuman=h,
        original_registered_417340_owner_proof=manager_proof(raw,registered=True),
        original_4d1190_lookup_nonnull=first,
        original_4d1110_lookup_nonnull_if_reached=second,
        original_raw_calendar_date_at_606c98=0xfffffffe,
    )


class Original606540HumanNoticeSourceTests(unittest.TestCase):
    def test_all_three_native_lookups_and_four_status_case_addresses(self):
        status_cases=(
            (0x60667e,0x606729,0x6067d6,0x6067d6),
            (0x606889,0x606939,0x6069e9,0x6069e9),
            (0x606a64,0x606b3c,0x606c11,0x606c11),
        )
        expected=(
            (0x58ad80,0x58b670,0x58bea0,0x58bea0),
            (0x58aa70,0x58b360,0x58bb90,0x58bb90),
            (0x58b090,0x58b980,0x58c1b0,0x58c1b0),
        )
        for family,flags in enumerate(((True,None),(False,True),(False,False))):
            for status in range(4):
                with self.subTest(family=family,status=status):
                    out=source_original_606540_human_notice_plan(notice(
                        first=flags[0],second=flags[1],status=status))
                    self.assertEqual(out.original_lookup_family,family)
                    self.assertEqual(out.original_native_status_case_address,status_cases[family][status])
                    self.assertEqual(out.original_selected_constructor_address,expected[family][status])
                    self.assertEqual(out.original_constructor_object_size,0x48 if family==2 else 0x44)
                    self.assertEqual(out.original_pending_queue_address,0x947aa8)
                    self.assertEqual(out.original_notice_envelope_vtable,0x7bd564)
                    self.assertEqual(out.original_following_player_event_handler,0x60aa20)
                    self.assertEqual(out.original_descriptor_status,status)
                    self.assertEqual(out.original_notice_wrapper_date_raw_u32,0xfffffffe)
                    self.assertEqual(out.original_notice_flags_or_mask,6)
                    self.assertEqual(out.original_enqueue_call_sites,(0x606cb8,0x60abdd))
                    self.assertFalse(out.original_native_constructor_executed)
                    self.assertFalse(out.original_notice_object_allocated)
                    self.assertFalse(out.original_947aa8_pending_queue_changed)
                    self.assertFalse(out.original_notice_delivered)

    def test_subtype2_status0_1_source_selector_and_status2_3_unknown(self):
        cases=(
            ((True,None),(0x59fec0,0x5a04e0)),
            ((False,True),(0x59f8e0,0x5a01d0)),
            ((False,False),(0x59fbf0,0x5a07f0)),
        )
        for (first,second),constructors in cases:
            for status in (0,1):
                # This is a synthetic subtype2 selector test, not a source
                # qualified 41A670 caller or actual original execution.
                plan=source_original_606540_human_notice_plan(notice(
                    first=first,second=second,status=status,subtype=2))
                self.assertEqual(plan.original_selected_constructor_address,constructors[status])
            for status in (2,3):
                with self.assertRaisesRegex(Original606540HumanNoticeSourceError,
                                             "without a qualified notice constructor"):
                    source_original_606540_human_notice_plan(notice(
                        first=first,second=second,status=status,subtype=2))

    def test_subtype_zero_reached_source_handler_and_human_constructor(self):
        plan=source_original_606540_human_notice_plan(notice(subtype=0,status=1))
        self.assertEqual((plan.original_descriptor_subtype,plan.original_descriptor_status),(0,1))
        self.assertEqual(plan.original_selected_constructor_address,0x58b670)

    def test_manager_and_secondary_lookup_paths_fail_closed(self):
        q=notice(first=True)
        for changed in (
            replace(q,original_4d1110_lookup_nonnull_if_reached=True),
            replace(q,original_4d1190_lookup_nonnull=1),
            replace(q,original_raw_calendar_date_at_606c98=-1),
            replace(q,original_raw_calendar_date_at_606c98=0x100000000),
            replace(q,original_registered_417340_owner_proof=replace(
                q.original_registered_417340_owner_proof,original_417340_return_al=0)),
            replace(q,original_registered_417340_owner_proof=replace(
                q.original_registered_417340_owner_proof,original_matching_user_pointer=None)),
            replace(q,original_prehuman=replace(q.original_prehuman,
                original_player_id=999)),
            replace(q,original_prehuman=replace(q.original_prehuman,
                original_event_pending_or_delivered=True)),
        ):
            with self.subTest(changed=changed):
                with self.assertRaises(Original606540HumanNoticeSourceError):
                    source_original_606540_human_notice_plan(changed)
        for invalid in (notice(first=False,second=None),notice(first=False,second=1)):
            with self.assertRaises(Original606540HumanNoticeSourceError):
                source_original_606540_human_notice_plan(invalid)

    def test_private_exe_native_opcode_switch_tables(self):
        filename=os.environ.get("FM2001_ORIGINAL_EXE")
        if not filename:
            self.skipTest("native original EXE intentionally outside public GitHub")
        exe=Path(filename).read_bytes()
        self.assertEqual(hashlib.sha256(exe).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        signatures={
            0x606618:"e8 23 0d e1 ff",
            0x60661d:"84 c0 0f 84 9c 06 00 00",
            0x606658:"e8 33 ab ec ff",
            0x606863:"e8 a8 a8 ec ff",
            0x606677:"ff 24 85 e4 6c 60 00",
            0x606882:"ff 24 85 f4 6c 60 00",
            0x606a5d:"ff 24 85 04 6d 60 00",
            0x606c88:"6a 0c e8 b1 14 06 00",
            0x606ca4:"c7 00 64 d5 7b 00",
            0x606caa:"83 4f 08 06",
            0x606cb3:"b9 a8 7a 94 00",
            0x606cce:"e8 4d 3d 00 00",
        }
        for va,signature in signatures.items():
            with self.subTest(va=hex(va)):
                b=bytes.fromhex(signature)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(b)],b)
        for va,expected in (
            (0x606ce4,(0x60667e,0x606729,0x6067d6,0x6067d6)),
            (0x606cf4,(0x606889,0x606939,0x6069e9,0x6069e9)),
            (0x606d04,(0x606a64,0x606b3c,0x606c11,0x606c11)),
        ):
            for i,addr in enumerate(expected):
                self.assertEqual(unpack_from('<I',exe,va-0x400000+4*i)[0],addr)


if __name__=='__main__':
    unittest.main()
