"""Exact 40CF31 default branch IEEE754 original write/no-write tests."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase

from original_native_40cbc0_coeff_route import (
    source_original_5da967_40cbc0_club_coefficient_route,
)
from original_native_40cbc0_full_category_join import source_original_40cbc0_full_linked_category
from original_native_40cf31_default_coeff import (
    Original40CF31DefaultSourceError,
    source_original_40cf31_default_coefficient_pair,
)
from test_original_native_40cbc0_full_category_join import reached

def default_case(raw_index=2, *, nondefault=False):
    src=reached(matches=(raw_index,) if raw_index is not None else ())
    route=src['original_40cbc0_reached_query_category_inputs']
    dispatch=route['original_40cbc0_dispatch_input']
    club=bytearray(dispatch['original_40cbc0_club_record'])
    pack_into('<I',club,0x14,24 if nondefault else 25)
    next_dispatch=dispatch|{'original_40cbc0_club_record':bytes(club)}
    new_route=source_original_5da967_40cbc0_club_coefficient_route(**next_dispatch)
    route['original_40cbc0_dispatch_input']=next_dispatch
    route['original_4056d0_query_input']=route['original_4056d0_query_input']|{
        'original_route':new_route,'original_40cbc0_club_record_at_query':bytes(club)}
    # Source indexed native field!=0x21 bypasses exception remapping.
    cat=route['original_4fa520_category_input']
    cat['original_reached_slot_dword_record']=(0x20).to_bytes(4,'little')
    grp=src['original_4fa510_group_source_inputs']
    grp['original_reached_index_slot_dword']=(0x20).to_bytes(4,'little')
    grp['original_reached_410ff0_group_pointer']=0x200000+0x20*108
    cat['original_4fa510_returned_eax']=raw_index if raw_index is not None else 0xffffffff
    return source_original_40cbc0_full_linked_category(**src)

def native(result):
    return dict(original_reached_source_category=result,
                original_40cbc0_ebp8_first_output_pointer=0x50000,
                original_40cbc0_ebpc_second_output_pointer=0x50100,
                original_first_output_before=bytes([0xaa])*8,
                original_second_output_before=bytes([0xbb])*8)

class Original40CF31DefaultCoefficientTests(TestCase):
    def test_all_five_original_category_constant_mul_pairs(self):
        cases=((0,15.,11.25),(1,10.,7.5),(2,8.,6.),(3,6.,4.5),(4,4.5,3.375))
        for idx,first,second in cases:
            with self.subTest(index=idx):
                output=source_original_40cf31_default_coefficient_pair(**native(default_case(idx)))
                self.assertTrue(output.original_both_native_outputs_written)
                self.assertEqual(unpack_from('<d',output.original_first_output_after)[0],first)
                self.assertEqual(unpack_from('<d',output.original_second_output_after)[0],second)
                self.assertFalse(output.original_native_match_executed)
                self.assertFalse(output.live_game_state_updated)

    def test_original_unmatched_410ff0_produces_no_writes(self):
        output=source_original_40cf31_default_coefficient_pair(**native(default_case(None)))
        self.assertEqual(output.original_native_category,0xffffffff)
        self.assertFalse(output.original_both_native_outputs_written)
        self.assertEqual(output.original_first_output_after,bytes([0xaa])*8)
        self.assertEqual(output.original_second_output_after,bytes([0xbb])*8)

    def test_case_24_and_aliasing_native_output_both_fail_closed(self):
        inp=native(default_case(2))
        for change in (
            {'original_40cbc0_ebp8_first_output_pointer':0},
            {'original_40cbc0_ebpc_second_output_pointer':0x50000},
            {'original_first_output_before':bytes(4)},
        ):
            with self.subTest(change=change):
                with self.assertRaises(Original40CF31DefaultSourceError):
                    source_original_40cf31_default_coefficient_pair(**(inp|change))
        with self.assertRaisesRegex(Original40CF31DefaultSourceError,'not reached'):
            source_original_40cf31_default_coefficient_pair(**native(default_case(2,nondefault=True)))

    def test_private_original_coefficients_and_jumptable_exact_sites(self):
        path=environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('original EXE private, hosted CI deliberately skips binary byte checks')
        exe=Path(path).read_bytes()
        self.assertEqual(sha256(exe).hexdigest(),
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3')
        originals=(30.,20.,16.,12.,9.)
        for i,v in enumerate(originals):
            self.assertEqual(unpack_from('<d',exe,0x822040-0x400000+i*16)[0],v)
        self.assertEqual(unpack_from('<d',exe,0x7bd6a8-0x400000)[0],0.5)
        self.assertEqual(unpack_from('<d',exe,0x7bd558-0x400000)[0],0.75)
        target=tuple(unpack_from('<I',exe,0x40d01c-0x400000+i*4)[0] for i in range(5))
        self.assertEqual(target,(0x40cf5f,0x40cf67,0x40cf6f,0x40cf77,0x40cf7f))
        sites={0x40cf31:'8b 47 10',0x40cf4c:'e8 cf d5 0e 00',
               0x40cf51:'8b 00',0x40cf53:'83 f8 04',
               0x40cf56:'77 3d',0x40cf58:'ff 24 85 1c d0 40 00',
               0x40cf5f:'dd 05 40 20 82 00',
               0x40cf67:'dd 05 50 20 82 00',
               0x40cf6f:'dd 05 60 20 82 00',
               0x40cf77:'dd 05 70 20 82 00',
               0x40cf7f:'dd 05 80 20 82 00',
               0x40cf85:'dc 0d a8 d6 7b 00',
               0x40cf8b:'dd 16',0x40cf8d:'dc 0d 58 d5 7b 00',
               0x40cf93:'dd 1b'}
        for va,dump in sites.items():
            with self.subTest(va=hex(va)):
                expect=bytes.fromhex(dump)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(expect)],expect)
