"""Actual 5DA967 original stack coefficient owners and 5DA981 branch checks."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import unpack_from
from unittest import TestCase

from original_native_5da967_coeff_guard import (
    Original5DA967CoefficientGuardError,source_original_5da967_two_native_qwords_to_zero_guard,
)
from test_original_native_40cbc0_all_paths import stage, START_AND_CALLS

def fixture(kind=25,category=2):
    return dict(
        original_5da8e9_esi_first_side_club_pointer=0x70000,
        original_source_first_side_category_receipt=stage(kind,category),
        original_actual_categories_all_40cbc0_calls=tuple(
            [(category if category<=4 else 0xffffffff)]*START_AND_CALLS[kind][1]),
        original_esp_pointer_at_5da967=0x200000,
        original_stack_98_qword_after_source_zero_initialization=bytes(8),
        original_stack_a0_qword_after_source_zero_initialization=bytes(8),
    )

class Original5DA967CoeffGuardTests(TestCase):
    def test_source_complete_all_eight_dispatch_zero_or_nonzero_branch(self):
        for kind in START_AND_CALLS:
            for category in (0,1,2,3,4,0xffffffff):
                with self.subTest(kind=kind,category=category):
                    o=source_original_5da967_two_native_qwords_to_zero_guard(**fixture(kind,category))
                    self.assertEqual(o.original_40cbc0_first_output_pointer,0x200098)
                    self.assertEqual(o.original_40cbc0_second_output_pointer,0x2000a0)
                    skipped=(category==0xffffffff or (kind==33 and category>2))
                    self.assertEqual(o.original_5da981_taken_zero_branch_to_5dac05,skipped)
                    self.assertEqual(o.original_stack_a0_qword_after==bytes(8),skipped)
                    self.assertFalse(o.original_5da967_original_call_executed)
                    self.assertFalse(o.live_game_state_updated)

    def test_forged_source_esi_esp_and_nonzero_initial_qwords_fail_closed(self):
        source=fixture()
        for bad in (
            {'original_5da8e9_esi_first_side_club_pointer':0},
            {'original_5da8e9_esi_first_side_club_pointer':0x71000},
            {'original_esp_pointer_at_5da967':0xffffffff},
            {'original_esp_pointer_at_5da967':True},
            {'original_stack_98_qword_after_source_zero_initialization':b''},
            {'original_stack_a0_qword_after_source_zero_initialization':bytes.fromhex('00 00 00 00 00 00 f0 3f')},
            {'original_actual_categories_all_40cbc0_calls':()},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises((Original5DA967CoefficientGuardError, ValueError)):
                    source_original_5da967_two_native_qwords_to_zero_guard(**(source|bad))

    def test_optional_original_first_side_stack_and_x87_zero_branch_bytes(self):
        path=environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('private original source absent from hosted CI')
        exe=Path(path).read_bytes()
        self.assertEqual(sha256(exe).hexdigest(),
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3')
        self.assertEqual(unpack_from('<d',exe,0x7bd5f8-0x400000)[0],0.0)
        sites={
            0x5da8d9:'8d 8c 24 98 00 00 00',
            0x5da8e0:'8d 94 24 90 00 00 00',
            0x5da8e7:'51',0x5da8e8:'52',0x5da8e9:'8b ce',
            0x5da93b:'c7 84 24 98 00 00 00 00 00 00 00',
            0x5da946:'c7 84 24 9c 00 00 00 00 00 00 00',
            0x5da951:'c7 84 24 a0 00 00 00 00 00 00 00',
            0x5da95c:'c7 84 24 a4 00 00 00 00 00 00 00',
            0x5da967:'e8 54 22 e3 ff',
            0x5da96c:'dd 84 24 a0 00 00 00',
            0x5da973:'dc 1d f8 d5 7b 00',
            0x5da97c:'df e0',0x5da97e:'f6 c4 40',
            0x5da981:'0f 85 7e 02 00 00',
        }
        for va,dump in sites.items():
            with self.subTest(original_va=hex(va)):
                expected=bytes.fromhex(dump)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(expected)],expected)
