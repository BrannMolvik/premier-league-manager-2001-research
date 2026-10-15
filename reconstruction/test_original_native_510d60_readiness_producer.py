"""Original 510D60 v34 team-readiness and 511120 wrapper native source."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase

from original_native_510d60_readiness_producer import (
    Original510D60ReadinessSourceError,
    source_original_510d60_actual_four_team_guard_results as source,
    source_original_511120_preserves_510d60_native_readiness as wrapped,
)


def match(vtable=0x7c4c24):
    b=bytearray(0x60)
    pack_into('<I',b,0,vtable)
    pack_into('<I',b,0x50,0x7000)
    return bytes(b)


def ctx():
    b=bytearray(0xd60)
    pack_into('<I',b,0,0x4000)
    pack_into('<I',b,0x5b0,0x5000)
    return bytes(b)


def inputs(vtable=0x7c4c24,checks=(True,True,True,True)):
    return dict(
       original_native_match_record_before_v34=match(vtable),
       original_processing_context_after_native_team_getters=ctx(),
       original_first_team_407770_zero_arg_eax_nonzero=checks[0],
       original_second_team_407770_zero_arg_eax_nonzero_if_reached=checks[1],
       original_first_team_407770_one_arg_eax_nonzero_if_reached=checks[2],
       original_second_team_407770_one_arg_eax_nonzero_if_reached=checks[3],
    )


class Original510D60NativeSourceTests(TestCase):
    def test_all_four_original_407770_gates_reach_exact_native_exits(self):
        cases=(
          ((False,None,None,None),0x511106,False,False),
          ((True,False,None,None),0x511106,False,False),
          ((True,True,False,None),0x5110ee,False,True),
          ((True,True,True,False),0x5110ee,False,True),
          ((True,True,True,True),0x5110e4,True,True),
        )
        for checks,site,result,prep in cases:
            with self.subTest(checks=checks):
                x=source(**inputs(checks=checks))
                self.assertEqual((x.original_510d60_exit_va,
                                  x.original_510d60_return_al_nonzero,
                                  x.original_mutable_preparation_5111a0_reached),
                                 (site,result,prep))
                self.assertEqual(x.original_false_exit_zeroes_context_5a4_b54,not result)
                self.assertFalse(x.actual_407770_callbacks_executed)
                self.assertFalse(x.game_state_modified)

    def test_original_wrapped_classes_preserve_base_510d60_al_even_after_kind5_writes(self):
        for vt in (0x7c9d9c,0x7c9e80,0x7c9ef8,0x7c9f70):
            for checks in ((False,None,None,None),(True,True,True,True)):
                with self.subTest(vt=hex(vt),checks=checks):
                    native=match(vt)
                    base=source(**inputs(vt,checks))
                    x=wrapped(original_base_readiness=base,
                              original_native_match_record_at_511120=native,
                              original_reached_virtual28_kind=2)
                    self.assertEqual(x.source_final_v34_return_al_nonzero,
                                     base.original_510d60_return_al_nonzero)
                    self.assertFalse(x.actual_original_510d60_or_511120_executed)
                    self.assertFalse(x.original_world_preparation_completed)
                    self.assertEqual(x.source_511120_wrapper_projection.returned_al_nonzero,
                                     base.original_510d60_return_al_nonzero)
                    expected=((0xd24,0x7000),) if checks[0] else ()
                    self.assertEqual(x.source_511120_wrapper_projection.original_written_context_dwords,
                                     expected)

    def test_wrapper_special_kind5_fields_require_actual_reached_method_results(self):
        native=bytearray(match(0x7c9d9c))
        pack_into('<I',native,0x54,0x8800)
        base=source(**inputs(0x7c9d9c,(False,None,None,None)))
        result=wrapped(original_base_readiness=base,
            original_native_match_record_at_511120=bytes(native),
            original_reached_virtual28_kind=5,
            original_reached_513e80_result=13,
            original_reached_513e70_result=21)
        self.assertFalse(result.source_final_v34_return_al_nonzero)
        self.assertEqual(result.source_511120_wrapper_projection.original_written_context_dwords,
                         ((0xd28,13),(0xd2c,21)))
        with self.assertRaises(Original510D60ReadinessSourceError):
            wrapped(original_base_readiness=base,
                original_native_match_record_at_511120=bytes(native),
                original_reached_virtual28_kind=5)

    def test_nonwrapped_source_v34_must_not_invoke_511120_wrapper(self):
        base=source(**inputs())
        self.assertFalse(base.source_wrapped_511120_required)
        with self.assertRaises(Original510D60ReadinessSourceError):
            wrapped(original_base_readiness=base,
                    original_native_match_record_at_511120=match(),
                    original_reached_virtual28_kind=2)

    def test_source_skip_bad_native_team_owner_unreached_flags_and_cross_vtable(self):
        good=inputs()
        cases=(
          {'original_first_team_407770_zero_arg_eax_nonzero':1},
          {'original_first_team_407770_zero_arg_eax_nonzero':False},
          {'original_native_match_record_before_v34':match(0x11223344)},
          {'original_native_match_record_before_v34':b''},
          {'original_processing_context_after_native_team_getters':ctx()[:0x5b3]},
          {'original_processing_context_after_native_team_getters':bytearray(ctx())},
          {'original_first_team_407770_one_arg_eax_nonzero_if_reached':None},
          {'original_second_team_407770_one_arg_eax_nonzero_if_reached':0},
        )
        for changes in cases:
            with self.subTest(changes=changes),self.assertRaises(Original510D60ReadinessSourceError):
                source(**(good|changes))
        for checks in ((False,True,None,None),
                       (True,False,True,None),
                       (True,True,False,True)):
            with self.subTest(checks=checks),self.assertRaises(Original510D60ReadinessSourceError):
                source(**inputs(checks=checks))
        for changed in (
            {'original_native_match_record_at_511120':match(0x7c4c24)},
            {'original_native_match_record_at_511120':bytes(0x60)},
        ):
            native=source(**inputs(0x7c9d9c))
            with self.subTest(changed=changed),self.assertRaises(Original510D60ReadinessSourceError):
                wrapped(original_base_readiness=native,
                        original_reached_virtual28_kind=2,**changed)

    def test_private_original_510d60_reads_exact_both_407770_0_and_1_calls(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('canonical private original PE not mounted')
        original=Path(p).read_bytes()
        self.assertEqual((len(original),sha256(original).hexdigest()),
                         (4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
          0x510d60:'51 a1 fc 47 98 00',
          0x510d85:'89 06',
          0x510d8f:'89 86 b0 05 00 00',
          0x510ee2:'8b 0e 57',
          0x510ee5:'e8 86 68 ef ff',
          0x510ef2:'8b 8e b0 05 00 00',
          0x510ef8:'57 e8 72 68 ef ff',
          0x510f06:'56 8b cd e8 92 02 00 00',
          0x510ff2:'6a 01 88 86 47 0d 00 00',
          0x510ffa:'e8 71 67 ef ff',
          0x51100d:'6a 01',
          0x51100f:'e8 5c 67 ef ff',
          0x5110e7:'b0 01',
          0x5110ee:'33 c0 5f 89 86 a4 05 00 00',
          0x511106:'89 be a4 05 00 00',
          0x511120:'53 56 57',
          0x51112a:'e8 31 fc ff ff',
          0x51112f:'8a d8',
          0x511167:'8a c3',
        }
        for va,sig in sites.items():
            with self.subTest(site=hex(va)):
                bs=bytes.fromhex(sig)
                self.assertEqual(original[va-0x400000:va-0x400000+len(bs)],bs)
