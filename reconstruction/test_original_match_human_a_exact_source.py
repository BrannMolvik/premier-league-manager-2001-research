"""Source-qualified exact x87 human stat minus original 40CBC0 QWORD."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack, pack_into
from unittest import TestCase

from original_match_human_a_exact_source import (
    OriginalScoredHumanAError,source_exact_original_human_5da250_a)
from original_match_four_5da250_argument_source import source_original_four_stage_5da250_arguments
from test_original_match_40cbc0_5e48d0_b_join import join,source

def user(stat8=-11,statc=17):
    b=bytearray(16)
    pack_into('<i',b,8,stat8)
    pack_into('<i',b,12,statc)
    return bytes(b)

class OriginalHumanScoreATests(TestCase):
    def test_four_original_human_stat_offsets_and_source_exact_operands(self):
        for stage,source_stat,expected in ((1,17,-3.),(2,17,-3.),(3,-11,-26.),(4,-11,-26.)):
            with self.subTest(stage=stage):
                o=source_exact_original_human_5da250_a(
                    original_stage_callback=join(stage,True),
                    original_selected_user_694_record_if_human=user())
                self.assertEqual(o.original_user_694_stat_offset,12 if stage<=2 else 8)
                self.assertEqual(o.original_reached_stat_signed_dword,source_stat)
                self.assertEqual(o.original_5da250_a_qword,pack('<d',expected))
                self.assertTrue(o.all_x87_precision_modes_exact)
                self.assertFalse(o.original_native_executed)
                self.assertFalse(o.game_state_updated)

    def test_exact_quarter_and_eighth_coefficients_signed_stat(self):
        for stage in range(1,5):
            c=join(stage,True,receipt=source(4.5))
            out=source_exact_original_human_5da250_a(
                original_stage_callback=c,original_selected_user_694_record_if_human=user(-11,100))
            self.assertEqual(out.original_5da250_a_qword,
                             pack('<d',100.-4.5 if stage<=2 else -11.-3.375))

    def test_original_two_arguments_join_to_already_verified_5da250_abi(self):
        for stage in range(1,5):
            c=join(stage,True)
            u=user()
            first=source_exact_original_human_5da250_a(
                original_stage_callback=c,original_selected_user_694_record_if_human=u)
            stack=bytearray(0x40)
            stack[0x30:0x38]=first.original_5da250_a_qword
            stack[0x38:0x40]=c.original_5e48d0_qword
            r=source_original_four_stage_5da250_arguments(
                source_stage=stage,original_stage_stack_before_argument_pushes=bytes(stack),
                original_4037b0_human_gate=True,
                original_selected_user_694_record_if_human=u,
                original_5e48d0_stored_qword_if_directly_copied_to_b=c.original_5e48d0_qword)
            self.assertEqual(r.native_first_qword_a,first.original_5da250_a_qword)
            self.assertEqual(r.native_second_qword_b,c.original_5e48d0_qword)
            self.assertFalse(r.live_game_state_updated)

    def test_unknown_native_user_or_pc24_rounding_fails_closed(self):
        for stage in range(1,5):
            for c,u in ((join(stage,False),user()),(join(stage,True),None),
                        (join(stage,True),b'\x00'*7),
                        (join(stage,True),user(2147483647,2147483647))):
                with self.subTest(stage=stage,callback=c,user=u):
                    with self.assertRaises(OriginalScoredHumanAError):
                        source_exact_original_human_5da250_a(
                            original_stage_callback=c,original_selected_user_694_record_if_human=u)

    def test_original_pe_human_fild_fsub_store_opcodes(self):
        path=environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('private original PE absent in CI')
        raw=Path(path).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
            4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x5DA9CB:'db 40 0c dc 64 24 38 dd 5c 24 30',
            0x5DAC6C:'db 40 0c dc 64 24 20 dd 5c 24 30',
            0x5DAEEA:'db 40 08 dc 64 24 20 dd 5c 24 30',
            0x5DB168:'db 40 08 dc 64 24 20 dd 5c 24 30',
        }
        for va,code in sites.items():
            with self.subTest(site=hex(va)):
                b=bytes.fromhex(code)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
