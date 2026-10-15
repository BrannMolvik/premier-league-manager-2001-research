"""Original stage4 coefficient jump and 21-DWORD per-player lookup tests."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into, unpack_from
from unittest import TestCase
from original_match_stage4_coefficient_player_source import (
    OriginalStageFourSourceError, source_original_stage_four_coefficient_player,
)


def fixture(category=0, player_index=1, ah=0):
    club=bytearray(0x74)
    pack_into("<I",club,0x70,player_index)
    table=bytearray(3*84)
    pack_into("<i",table,8,-17)
    pack_into("<i",table,84+8,61)
    pack_into("<i",table,168+8,-2147483648)
    return dict(original_reached_stage4_x87_ah=ah,
                original_410ff0_category_eax=category,
                original_first_side_club_pointer=0x40000,
                original_first_side_club_before_stage=bytes(club),
                original_874c08_global_player_table_pointer=0x90000,
                original_global_player_21_dword_records=bytes(table))


class SourceOriginalStageFourCoefficientTests(TestCase):
    def test_six_jump_entries_and_unsigned_default(self):
        values=(0.9,0.8,0.7,0.6,0.5,0.5)
        jumps=(0x5db1cd,0x5db1da,0x5db1f0,0x5db205,0x5db212,0x5db228)
        for cat in range(6):
            with self.subTest(cat=cat):
                q=source_original_stage_four_coefficient_player(**fixture(category=cat))
                self.assertEqual(q.original_jump_target,jumps[cat])
                self.assertEqual(q.original_coefficient_qword, __import__('struct').pack('<d',values[cat]))
                self.assertEqual(q.original_global_player_signed_dword,61)
                self.assertFalse(q.original_rng_64d540_executed)
        for cat in (6,7,0xffffffff):
            with self.subTest(default=cat):
                q=source_original_stage_four_coefficient_player(**fixture(category=cat))
                self.assertEqual((q.original_jump_target,q.original_coefficient_qword_va),(0x5db23d,0x821e20))

    def test_first_last_signed_player_row_and_excluded_wrap(self):
        for idx,expected in ((0,-17),(2,-2147483648)):
            q=source_original_stage_four_coefficient_player(**fixture(player_index=idx))
            self.assertEqual(q.original_global_player_signed_dword,expected)
        for idx in (3,0xffffffff,0xccccccc):
            with self.assertRaises(OriginalStageFourSourceError):
                source_original_stage_four_coefficient_player(**fixture(player_index=idx))

    def test_invalid_native_guard_owner_and_records_fail_closed(self):
        inputs=fixture()
        for change in (
            {'original_reached_stage4_x87_ah':0x40},
            {'original_reached_stage4_x87_ah':True},
            {'original_410ff0_category_eax':-1},
            {'original_first_side_club_pointer':0},
            {'original_874c08_global_player_table_pointer':0},
            {'original_first_side_club_before_stage':b''},
            {'original_global_player_21_dword_records':b''},
            {'original_global_player_21_dword_records':bytes(85)},
        ):
            with self.subTest(change=change):
                with self.assertRaises(OriginalStageFourSourceError):
                    source_original_stage_four_coefficient_player(**(inputs|change))

    def test_private_pe_jump_table_and_coefficients_when_available(self):
        path=environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('private original PE absent in hosted CI')
        pe=Path(path).read_bytes()
        self.assertEqual((len(pe),sha256(pe).hexdigest()),(4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        expected_jumps=(0x5db1cd,0x5db1da,0x5db1f0,0x5db205,0x5db212,0x5db228)
        self.assertEqual(tuple(unpack_from('<I',pe,0x5dba44-0x400000+4*i)[0] for i in range(6)),expected_jumps)
        for i,v in enumerate((0.9,0.8,0.7,0.6,0.5)):
            with self.subTest(coeff=i):
                self.assertEqual(pe[0x821e00-0x400000+i*8:0x821e00-0x400000+(i+1)*8],__import__('struct').pack('<d',v))
        sites={0x5db1c1:'83 f8 05',0x5db1c4:'77 77',0x5db1c6:'ff 24 85 44 ba 5d 00',0x5db250:'8b 43 70',0x5db253:'8d 0c 80',0x5db256:'8d 14 88',0x5db259:'a1 08 4c 87 00',0x5db262:'db 44 90 08',0x5db280:'e8 cb ef ff ff',0x5db364:'e8 d7 21 07 00'}
        for va,h in sites.items():
            with self.subTest(va=hex(va)):
                sig=bytes.fromhex(h)
                self.assertEqual(pe[va-0x400000:va-0x400000+len(sig)],sig)
