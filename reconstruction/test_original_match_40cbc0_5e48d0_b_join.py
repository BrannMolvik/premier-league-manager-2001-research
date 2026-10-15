"""Finite original 40CBC0 coefficient -> four scored 5E48D0 callback receipt."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack
from unittest import TestCase
from original_native_40cbc0_all_paths import SourceOriginal40CBC0AllPathReceipt
from original_match_40cbc0_5e48d0_b_join import (
    Original40CBC05E48D0JoinError, source_original_40cbc0_callback_to_stage_b)

Z=b'\x00'*8
ONE=pack('<d',1.)
def source(base=20.):
    return SourceOriginal40CBC0AllPathReceipt(
        0x40CBF2,0,1,(),pack('<d',base),pack('<d',base*0.75),True)
def join(stage,human,receipt=None,factor=Z,reached=True):
    return source_original_40cbc0_callback_to_stage_b(
        original_40cbc0_coefficients=source() if receipt is None else receipt,
        original_stage=stage,original_scored_stage_entered=reached,
        original_4037b0_human_club=human,
        original_87ad88_qword_before_constructor=factor)

class OriginalFourStage40CBC0CallbackJoinTests(TestCase):
    def test_first_two_stages_use_first_output_later_two_use_second(self):
        for stage,value,slot in ((1,20.,'40cbc0-ebp8-first'),(2,20.,'40cbc0-ebp8-first'),
                                 (3,15.,'40cbc0-ebpc-second'),(4,15.,'40cbc0-ebpc-second')):
            with self.subTest(stage=stage):
                r=join(stage,True)
                self.assertEqual(r.original_coefficient_qword,pack('<d',value))
                self.assertEqual(r.original_5e48d0_qword,pack('<d',value))
                self.assertEqual(r.original_input_slot,slot)
                self.assertEqual(r.original_factor_after_constructor,ONE)
                self.assertIsNotNone(r.direct_native_b_store_site_if_reached)
                self.assertFalse(r.original_native_executed)
                self.assertFalse(r.game_state_updated)

    def test_both_first_use_zero_and_existing_one_all_exact_native_coefficients(self):
        bases=(30.,25.,20.,17.,16.,15.,12.,10.,9.,8.,6.,4.5)
        for base in bases:
            for stage in (1,2,3,4):
                for factor in (Z,ONE):
                    with self.subTest(base=base,stage=stage,factor=factor):
                        r=join(stage,True,receipt=source(base),factor=factor)
                        self.assertEqual(r.original_5e48d0_qword,
                            pack('<d',base if stage<=2 else base*0.75))
                        self.assertEqual(r.original_factor_before_constructor,factor)

    def test_nonhuman_stages_2_3_4_do_not_copy_fresh_callback_into_b(self):
        self.assertEqual(join(1,False).direct_native_b_store_site_if_reached,0x5DA9AD)
        for stage in (2,3,4):
            self.assertIsNone(join(stage,False).direct_native_b_store_site_if_reached)
            self.assertIsNotNone(join(stage,True).direct_native_b_store_site_if_reached)

    def test_original_zero_initialized_caller_when_40cbc0_wrote_nothing(self):
        blank=SourceOriginal40CBC0AllPathReceipt(0x40CF31,6,1,(),Z,Z,False)
        for stage in range(1,5):
            self.assertEqual(join(stage,True,receipt=blank).original_5e48d0_qword,Z)
        wrong=SourceOriginal40CBC0AllPathReceipt(0x40CF31,6,1,(),pack('<d',2.),Z,False)
        with self.assertRaises(Original40CBC05E48D0JoinError):
            join(1,True,receipt=wrong)

    def test_unreached_or_unproved_world_fails_closed(self):
        args=dict(original_40cbc0_coefficients=source(),original_stage=1,
            original_scored_stage_entered=True,original_4037b0_human_club=True,
            original_87ad88_qword_before_constructor=Z)
        for override in (
            dict(original_stage=0),dict(original_stage=True),
            dict(original_scored_stage_entered=False),dict(original_scored_stage_entered=1),
            dict(original_4037b0_human_club=1),
            dict(original_87ad88_qword_before_constructor=pack('<d',2.)),
            dict(original_87ad88_qword_before_constructor=b'\x00'),
            dict(original_40cbc0_coefficients=None),
            dict(original_40cbc0_coefficients=SourceOriginal40CBC0AllPathReceipt(
                0x40CBF2,1,1,(),pack('<d',19.),pack('<d',14.25),True)),
            dict(original_40cbc0_coefficients=SourceOriginal40CBC0AllPathReceipt(
                0x40CBF2,1,1,(),pack('<d',20.),pack('<d',15.5),True)),
        ):
            with self.subTest(override=override):
                with self.assertRaises(Original40CBC05E48D0JoinError):
                    source_original_40cbc0_callback_to_stage_b(**(args|override))

    def test_private_original_opcode_source_and_literal_coefficient_scale(self):
        path=environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('private canonical original PE unavailable in CI')
        raw=Path(path).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
            4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        self.assertEqual(raw[0x7bd558-0x400000:0x7bd560-0x400000],pack('<d',0.75))
        sites={
            0x5DA8D9:'8d 8c 24 98 00 00 00 8d 94 24 90 00 00 00 51 52',
            0x5DA93B:'c7 84 24 98 00 00 00 00 00 00 00',
            0x5DA946:'c7 84 24 9c 00 00 00 00 00 00 00',
            0x5DA951:'c7 84 24 a0 00 00 00 00 00 00 00',
            0x5DA95C:'c7 84 24 a4 00 00 00 00 00 00 00',
            0x5DA987:'8b 84 24 94 00 00 00 8b 8c 24 90 00 00 00',
            0x5DAC1A:'8b 8c 24 94 00 00 00 8b 94 24 90 00 00 00',
            0x5DAE98:'8b 94 24 9c 00 00 00 8b 84 24 98 00 00 00',
            0x5DB116:'8b 8c 24 9c 00 00 00 8b 94 24 98 00 00 00',
            0x5E4419:'8b 45 10 56 85 c0 8b f1 c7 44 24 04 00 00 00 00 74 0d',
            0x5E442B:'dd 05 88 ad 87 00 dc 4d 08 dd 1e eb 0b',
            0x5E445A:'8b 46 08 85 c0 0f 84 bc 03 00 00',
            0x5E48D0:'8b 44 24 04 dd 01 85 c0 74 06 dc 35 88 ad 87 00 c2 04 00',
            0x6596A0:'33 c0 c3',
        }
        for va,code in sites.items():
            with self.subTest(va=hex(va)):
                sig=bytes.fromhex(code)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(sig)],sig)
        for va in (0x5DA995,0x5DAC28,0x5DAEA6,0x5DB124):
            with self.subTest(stage_constructor=hex(va)):
                off=va-0x400000
                self.assertEqual(raw[off:off+6],bytes.fromhex('6a 00 6a 00 6a 01'))
                self.assertEqual(raw[off+10:off+12],bytes.fromhex('24 34'))
