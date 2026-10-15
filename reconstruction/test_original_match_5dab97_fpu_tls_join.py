"""Source first/second 5DAB97 FPU score bound joined to real TLS 66D553."""
from dataclasses import replace
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack,unpack_from
from unittest import TestCase

from original_native_66d553_tls_initial_state import (
    source_original_66d553_reached_crt_tls_record,
)
from original_match_5dab97_fpu_tls_join import (
    OriginalScoringFpuBoundSourceError,
    source_original_5dab97_fpu_bound_to_66d553_tls_rand as join,
)


def initialized():
    return source_original_66d553_reached_crt_tls_record(
        original_tls_slot_dword_84ad40=9,
        original_tlsgvalue_return_pointer=0,
        original_existing_tls_record_if_reached=None,
        original_calloc_return_pointer_if_fresh=0x7000,
        original_calloc_zero_record_if_fresh=bytes(0x74),
        original_tlssetvalue_return_eax_if_fresh=1,
        original_thread_id_callback_return_eax_if_fresh=0x123,
    )


def args(side=1,stage=0.5,clamped=250.,eax=2):
    return dict(
        original_scoring_side=side,
        original_native_stage_ratio_qword_at_esp10=pack('<d',stage),
        original_native_clamped_fpu_st0_qword_before_5dab97=pack('<d',clamped),
        original_independently_reached_668350_signed_eax=eax,
        original_reached_66d553_thread_record=initialized(),
    )


class OriginalScoringFpuTlsJoinTests(TestCase):
    def test_first_stage_le_one_uses_original_binary64_one_percent_then_source_rng(self):
        r=join(**args())
        self.assertEqual(r.original_native_branch_va,0x5dabc2)
        self.assertEqual(r.original_native_668350_eax_signed,2)
        self.assertTrue(r.original_source_float_truncation_consistency_verified)
        self.assertEqual(r.original_native_rng_projection.original_positive_clamped_edi_bound,2)
        step=r.original_native_rng_projection.original_score_rng_source
        self.assertEqual((step.original_seed_before,step.original_seed_after,
                          step.original_66951c_rand15,step.original_64d540_return_eax),
                         (1,0x29e2c0,41,0))
        self.assertFalse(r.actual_original_x87_executed)
        self.assertFalse(r.actual_native_rng_consumed)
        self.assertFalse(r.live_game_state_updated)

    def test_large_ratio_denominator_original_plus100_and_times1000_before_rng(self):
        for side in (1,2):
            with self.subTest(side=side):
                r=join(**args(side=side,stage=2.,clamped=2750.,eax=2))
                self.assertEqual(r.original_native_branch_va,
                                 0x5daba8 if side==1 else 0x5dae23)
                self.assertEqual(r.original_float_formula_value,2.5)
                self.assertEqual(r.original_native_rng_projection.source_score_side,side)
                self.assertEqual(r.original_native_rng_projection.original_score_rng_source.original_call_site,
                                 0x5dabed if side==1 else 0x5dae68)

    def test_native_bound_zero_or_negative_clamped_to_edi_one_not_fabricated_score(self):
        x=join(**args(stage=2.,clamped=700.,eax=0))
        self.assertEqual(x.original_native_rng_projection.original_positive_clamped_edi_bound,1)
        y=join(**args(stage=0.5,clamped=-250.,eax=-2))
        self.assertEqual(y.original_native_rng_projection.original_positive_clamped_edi_bound,1)
        self.assertFalse(y.original_native_rng_projection.saved_match_world_modified)

    def test_existing_crt_tls_seed_must_not_reinitialize_before_original_score(self):
        from struct import pack_into
        raw=bytearray(0x74)
        pack_into('<I',raw,0x14,0xdeadbeef)
        tls=source_original_66d553_reached_crt_tls_record(
            original_tls_slot_dword_84ad40=9,
            original_tlsgvalue_return_pointer=0x7010,
            original_existing_tls_record_if_reached=bytes(raw),
            original_calloc_return_pointer_if_fresh=None,
            original_calloc_zero_record_if_fresh=None,
            original_tlssetvalue_return_eax_if_fresh=None,
            original_thread_id_callback_return_eax_if_fresh=None,
        )
        self.assertFalse(tls.source_original_new_tls_initialized)
        score=join(**(args()|{
            'original_reached_66d553_thread_record':tls,
        }))
        self.assertEqual(score.original_native_rng_projection.original_score_rng_source.original_seed_before,
                         0xdeadbeef)
        self.assertNotEqual(score.original_native_rng_projection.original_score_rng_source.original_seed_before,1)

    def test_incorrect_fpu_native_observation_and_unvisited_tls_fields_fail_closed(self):
        good=args()
        for change in (
            {'original_scoring_side':3},
            {'original_scoring_side':True},
            {'original_native_stage_ratio_qword_at_esp10':pack('<d',float('nan'))},
            {'original_native_stage_ratio_qword_at_esp10':pack('<d',float('inf'))},
            {'original_native_stage_ratio_qword_at_esp10':bytes(5)},
            {'original_native_clamped_fpu_st0_qword_before_5dab97':pack('<d',float('-inf'))},
            {'original_native_clamped_fpu_st0_qword_before_5dab97':pack('<d',float('nan'))},
            {'original_native_clamped_fpu_st0_qword_before_5dab97':pack('<d',100000001.)},
            {'original_independently_reached_668350_signed_eax':3},
            {'original_independently_reached_668350_signed_eax':True},
            {'original_independently_reached_668350_signed_eax':0x80000000},
            {'original_reached_66d553_thread_record':None},
            {'original_reached_66d553_thread_record':replace(initialized(),original_seed_at_plus14=19)},
        ):
            with self.subTest(change=change),self.assertRaises(OriginalScoringFpuBoundSourceError):
                join(**(good|change))

    def test_native_original_pe_source_branches_and_true_double_constants(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('original private PE not available in hosted CI')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        source={
            0x5dab97:'dd 44 24 10',
            0x5dab9b:'dc 1d b0 d6 7b 00',
            0x5daba3:'f6 c4 41',
            0x5daba8:'dd 44 24 10',
            0x5dabac:'dc 25 b0 d6 7b 00',
            0x5dabb2:'dc 0d 28 68 7c 00',
            0x5dabb8:'dc 05 a0 d6 7b 00',
            0x5dabbe:'d8 f9',
            0x5dabc2:'d9 c0',
            0x5dabc4:'dc 0d 00 d6 7b 00',
            0x5dabca:'e8 81 d7 08 00',
            0x5dae12:'dd 44 24 10',
            0x5dae16:'dc 1d b0 d6 7b 00',
            0x5dae23:'dd 44 24 10',
            0x5dae2d:'dc 0d 28 68 7c 00',
            0x5dae39:'d8 f9',
            0x5dae3d:'d9 c0',
            0x5dae3f:'dc 0d 00 d6 7b 00',
            0x5dae45:'e8 06 d5 08 00',
        }
        for va,h in source.items():
            with self.subTest(va=hex(va)):
                data=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(data)],data)
        from struct import unpack_from
        self.assertEqual(tuple(unpack_from('<d',raw,va-0x400000)[0] for va in
            (0x7bd6b0,0x7c6828,0x7bd6a0,0x7bd600)),(1.,1000.,100.,.01))
