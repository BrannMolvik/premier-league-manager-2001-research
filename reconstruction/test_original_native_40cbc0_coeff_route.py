"""Original 5DA967->40CBC0 dispatch checked without native match execution."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase
from original_native_40cbc0_coeff_route import (
    Original40CBC0SourceError,source_original_5da967_40cbc0_club_coefficient_route,
)

SOURCE_EXCEPTIONS={24:0x40ce83,26:0x40cbf2,31:0x40ceda,
                   33:0x40ccc9,40:0x40cd5d,66:0x40ce09,73:0x40cdb3}
ORIGINAL_JUMPS=(0x40ce83,0x40cbf2,0x40ceda,0x40ccc9,
                0x40cd5d,0x40ce09,0x40cdb3,0x40cf31)

def reached(kind):
    record=bytearray(0x18)
    pack_into('<I',record,0x14,kind)
    return dict(original_5da967_first_side_club_pointer=0x70000,
                original_40cbc0_ecx_club_pointer=0x70000,
                original_40cbc0_club_record=bytes(record))

class SourceOriginal40CBC0DispatchTests(TestCase):
    def test_all_fifty_in_range_selector_cases_are_source_exact(self):
        for kind in range(24,74):
            with self.subTest(kind=kind):
                receipt=source_original_5da967_40cbc0_club_coefficient_route(**reached(kind))
                self.assertEqual(receipt.original_selected_jump_target,
                                 SOURCE_EXCEPTIONS.get(kind,0x40cf31))
                self.assertEqual(receipt.original_dispatch_table_selector,
                                 (24,26,31,33,40,66,73).index(kind)
                                 if kind in SOURCE_EXCEPTIONS else 7)
                self.assertFalse(receipt.original_coefficients_computed)
                self.assertFalse(receipt.live_game_state_updated)

    def test_out_of_range_uint32_including_wrapping_never_indexes_table(self):
        for kind in (0,1,23,74,0xfffffff0,0xffffffff):
            with self.subTest(kind=kind):
                result=source_original_5da967_40cbc0_club_coefficient_route(**reached(kind))
                self.assertIsNone(result.original_dispatch_table_selector)
                self.assertEqual(result.original_selected_jump_target,0x40cf31)

    def test_forged_pointer_or_incomplete_club_record_fails_closed(self):
        data=reached(24)
        for bad in ({'original_5da967_first_side_club_pointer':0},
                    {'original_40cbc0_ecx_club_pointer':0},
                    {'original_40cbc0_ecx_club_pointer':0x71000},
                    {'original_40cbc0_ecx_club_pointer':True},
                    {'original_40cbc0_club_record':bytes(20)},
                    {'original_40cbc0_club_record':None}):
            with self.subTest(bad=bad):
                with self.assertRaises(Original40CBC0SourceError):
                    source_original_5da967_40cbc0_club_coefficient_route(**(data|bad))

    def test_optional_original_pe_dispatch_tables_and_opcode_sites(self):
        file=environ.get('FM2001_ORIGINAL_EXE')
        if not file:
            self.skipTest('original proprietary executable intentionally omitted in hosted CI')
        executable=Path(file).read_bytes()
        self.assertEqual((len(executable),sha256(executable).hexdigest()),
          (4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        image_base=0x400000
        choices=executable[0x40cfc0-image_base:0x40cfc0-image_base+50]
        for i,value in enumerate(choices):
            expected=(24,26,31,33,40,66,73).index(i+24) if i+24 in SOURCE_EXCEPTIONS else 7
            with self.subTest(club_kind=i+24):
                self.assertEqual(value,expected)
        native=tuple(unpack_from('<I',executable,0x40cfa0-image_base+i*4)[0]
                     for i in range(8))
        self.assertEqual(native,ORIGINAL_JUMPS)
        for va,opcode in ((0x40cbd4,'8b 47 14'),(0x40cbda,'83 f8 31'),
                          (0x40cbe3,'33 c9'),(0x40cbe5,'8a 88 c0 cf 40 00'),
                          (0x40cbeb,'ff 24 8d a0 cf 40 00')):
            with self.subTest(source_va=hex(va)):
                raw=bytes.fromhex(opcode)
                self.assertEqual(executable[va-image_base:va-image_base+len(raw)],raw)
