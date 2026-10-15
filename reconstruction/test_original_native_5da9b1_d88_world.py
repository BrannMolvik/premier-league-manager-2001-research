"""Original 5DA987 coefficient-positive human/nonhuman D88 source tests."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack,pack_into,unpack_from
from unittest import TestCase
from original_native_5da967_coeff_guard import source_original_5da967_two_native_qwords_to_zero_guard
from original_native_5da9b1_d88_world import (
    Original5DA9B1D88SourceError, source_original_5da9b1_match_d88_stage,
)
from test_original_native_5da967_coeff_guard import fixture as coefficient_fixture

def args(*,human=False,coefficient_kind=25,coefficient_category=2):
    guard=source_original_5da967_two_native_qwords_to_zero_guard(
        **coefficient_fixture(coefficient_kind,coefficient_category))
    source=dict(
        original_coefficients_at_5da981=guard,
        original_5da9a8_5e48d0_return_qword=pack('<d',123.9),
        original_5da987_match_processing_context_pointer=0xC0000,
        original_processing_context_before_d88=bytes([0xaa])*0xd8c,
        original_5da9b3_first_side_club_pointer=0x70000,
        original_5da9b3_4037b0_human_result=human,
        original_5da9be_403850_selected_user_pointer_if_human=None,
        original_5da9d6_403850_selected_user_pointer_if_human=None,
        original_5da9c3_selected_user694_pointer_first_if_human=None,
        original_5da9db_selected_user694_pointer_second_if_human=None,
        original_reached_694_first_record_if_human=None,
        original_reached_694_second_record_if_human=None,
        original_reached_x87_stack30_fstp_qword_if_human=None)
    if human:
        first=bytearray(16)
        second=bytearray(16)
        pack_into('<i',first,0xc,-3)
        pack_into('<i',second,0xc,17)
        source.update(
            original_5da9be_403850_selected_user_pointer_if_human=0x42000,
            original_5da9d6_403850_selected_user_pointer_if_human=0x42000,
            original_5da9c3_selected_user694_pointer_first_if_human=0xA0000,
            original_5da9db_selected_user694_pointer_second_if_human=0xA0000,
            original_reached_694_first_record_if_human=bytes(first),
            original_reached_694_second_record_if_human=bytes(second),
            original_reached_x87_stack30_fstp_qword_if_human=pack('<d',-123.25))
    return source

class SourceOriginal5DA9B1D88Tests(TestCase):
    def test_nonhuman_native_668350_truncates_reached_5e48d0_to_d88(self):
        s=args()
        o=source_original_5da9b1_match_d88_stage(**s)
        self.assertEqual(unpack_from('<I',o.original_context_after_d88,0xd88)[0],123)
        self.assertEqual(o.original_stack_30_qword_after_branch,bytes(8))
        self.assertIsNone(o.original_user694_first_read_dword_if_human)
        self.assertFalse(o.original_5e48d0_executed)
        self.assertFalse(o.original_game_state_updated)

    def test_human_selected_repeated_user694_reads_and_preserves_x87_delta(self):
        s=args(human=True)
        o=source_original_5da9b1_match_d88_stage(**s)
        self.assertEqual(unpack_from('<I',o.original_context_after_d88,0xd88)[0],17)
        self.assertEqual(o.original_user694_first_read_dword_if_human,0xfffffffd)
        self.assertEqual(o.original_user694_second_read_dword_if_human,17)
        self.assertEqual(o.original_stack_30_qword_after_branch,pack('<d',-123.25))
        self.assertEqual(o.original_context_after_d88[:0xd88],s['original_processing_context_before_d88'][:0xd88])

    def test_coefficient_zero_guard_skips_5da987_entirely(self):
        with self.assertRaisesRegex(Original5DA9B1D88SourceError,'zero branch bypasses'):
            source_original_5da9b1_match_d88_stage(**args(coefficient_kind=33,coefficient_category=3))
        with self.assertRaisesRegex(Original5DA9B1D88SourceError,'zero branch bypasses'):
            source_original_5da9b1_match_d88_stage(**args(coefficient_category=0xffffffff))

    def test_human_only_data_pointer_mismatch_and_invalid_fpu_fail_closed(self):
        base=args(human=True)
        for bad in (
            {'original_5da9b3_first_side_club_pointer':0x71000},
            {'original_5da9be_403850_selected_user_pointer_if_human':0x45000},
            {'original_5da9db_selected_user694_pointer_second_if_human':0xAA000},
            {'original_reached_694_first_record_if_human':b''},
            {'original_reached_x87_stack30_fstp_qword_if_human':b''},
            {'original_processing_context_before_d88':bytes(12)},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(Original5DA9B1D88SourceError):
                    source_original_5da9b1_match_d88_stage(**(base|bad))
        ai=args()
        for bad in (
            {'original_5da9b3_4037b0_human_result':1},
            {'original_5da9a8_5e48d0_return_qword':pack('<d',float('nan'))},
            {'original_5da9a8_5e48d0_return_qword':b''},
            {'original_5da9d6_403850_selected_user_pointer_if_human':0x42000},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(Original5DA9B1D88SourceError):
                    source_original_5da9b1_match_d88_stage(**(ai|bad))

    def test_optional_original_pe_native_d88_human_versus_ai_sites(self):
        path=environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('original canonical PE absent in hosted CI')
        exe=Path(path).read_bytes()
        self.assertEqual(sha256(exe).hexdigest(),
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3')
        sites={
            0x5da987:'8b 84 24 94 00 00 00',
            0x5da99d:'8d 4c 24 34',0x5da9a1:'e8 0a 9a 00 00',
            0x5da9a8:'e8 23 9f 00 00',
            0x5da9b1:'8b ce',0x5da9b3:'e8 f8 8d e2 ff',
            0x5da9b8:'84 c0',0x5da9ba:'74 30',
            0x5da9be:'e8 8d 8e e2 ff',0x5da9c3:'8b 80 94 06 00 00',
            0x5da9cb:'db 40 0c',0x5da9ce:'dc 64 24 38',
            0x5da9d2:'dd 5c 24 30',0x5da9d6:'e8 75 8e e2 ff',
            0x5da9db:'8b 80 94 06 00 00',
            0x5da9e1:'8b 50 0c',0x5da9e4:'89 97 88 0d 00 00',
            0x5da9ec:'dd 44 24 38',0x5daa00:'e8 4b d9 08 00',
            0x5daa05:'89 87 88 0d 00 00',
        }
        for va,bytes_hex in sites.items():
            with self.subTest(va=hex(va)):
                want=bytes.fromhex(bytes_hex)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(want)],want)
