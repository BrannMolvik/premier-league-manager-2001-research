"""Original stage QWORD integer truncation/pair proof, private PE regressions."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into
from unittest import TestCase
from original_match_four_stage_integer_totals import (
    OriginalFourStageIntegerTotalError,source_original_5db37c_four_stage_integer_totals)

def stack(values):
    b=bytearray(0x70)
    for off,val in zip((0x60,0x58,0x68,0x50),values):
        pack_into('<d',b,off,val)
    return bytes(b)

class FourStageIntegerTotalTests(TestCase):
    def test_paired_order_is_first_third_and_fourth_second(self):
        r=source_original_5db37c_four_stage_integer_totals(
            original_stage_stack_at_5db37c=stack((2.9,3.9,4.9,5.9)),
            original_entered_stage_guards=(True,)*4)
        self.assertEqual(r.original_stage_converted_s64,(2,3,4,5))
        self.assertEqual((r.original_pre_human_ebx_first_and_third_u32,
                          r.original_pre_human_edi_fourth_and_second_u32),(6,8))
        self.assertFalse(r.original_native_executed)
        self.assertFalse(r.original_context_written)

    def test_native_truncation_sign_and_32bit_wrap(self):
        r=source_original_5db37c_four_stage_integer_totals(
            original_stage_stack_at_5db37c=stack((-3.9,-1.9,2.9,4.9)),
            original_entered_stage_guards=(True,)*4)
        self.assertEqual(r.original_stage_converted_s64,(-3,-1,2,4))
        self.assertEqual((r.original_pre_human_ebx_first_and_third_u32,
                          r.original_pre_human_edi_fourth_and_second_u32),(0xffffffff,3))
        r=source_original_5db37c_four_stage_integer_totals(
            original_stage_stack_at_5db37c=stack((float(2**31),0.,float(2**31),1.)),
            original_entered_stage_guards=(True,)*4)
        self.assertEqual(r.original_pre_human_ebx_first_and_third_u32,0)

    def test_skipped_stage_slots_must_remain_initialized_zero(self):
        r=source_original_5db37c_four_stage_integer_totals(
            original_stage_stack_at_5db37c=stack((0.,4.9,0.,0.)),
            original_entered_stage_guards=(False,True,False,False))
        self.assertEqual(r.original_stage_converted_s64,(0,4,0,0))
        with self.assertRaises(OriginalFourStageIntegerTotalError):
            source_original_5db37c_four_stage_integer_totals(
                original_stage_stack_at_5db37c=stack((1.,0.,0.,0.)),
                original_entered_stage_guards=(False,)*4)

    def test_nonfinite_overflow_missing_source_fail_closed(self):
        for b,g in ((b'',(True,)*4),(stack((0.,)*4),(1,True,True,True)),
                    (stack((0.,)*4),(True,True,True)),
                    (stack((float('nan'),0.,0.,0.)),(True,)*4),
                    (stack((float('inf'),0.,0.,0.)),(True,)*4),
                    (stack((float(2**63),0.,0.,0.)),(True,)*4)):
            with self.subTest(guards=g):
                with self.assertRaises(OriginalFourStageIntegerTotalError):
                    source_original_5db37c_four_stage_integer_totals(
                        original_stage_stack_at_5db37c=b,original_entered_stage_guards=g)

    def test_original_pe_four_init_slots_four_calls_and_pair_add(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE unavailable in hosted CI')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
            4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x5DA8E7:'51 52',
            0x5DA8EB:'c7 44 24 68 00 00 00 00',
            0x5DA8F3:'c7 44 24 6c 00 00 00 00',
            0x5DA8FB:'c7 44 24 60 00 00 00 00',
            0x5DA903:'c7 44 24 64 00 00 00 00',
            0x5DA90B:'c7 44 24 70 00 00 00 00',
            0x5DA913:'c7 44 24 74 00 00 00 00',
            0x5DA91B:'c7 44 24 58 00 00 00 00',
            0x5DA923:'c7 44 24 5c 00 00 00 00',
            0x5DB37C:'dd 44 24 68 e8 cb cf 08 00 dd 44 24 60 8b d8 e8 c0 cf 08 00',
            0x5DB390:'dd 44 24 50 03 d8 89 5c 24 10 e8 b1 cf 08 00',
            0x5DB39F:'dd 44 24 58 8b f8 e8 a6 cf 08 00 03 f8',
            0x5DB3AC:'8b ce 89 7c 24 18',
        }
        for va,s in sites.items():
            with self.subTest(va=hex(va)):
                b=bytes.fromhex(s)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
