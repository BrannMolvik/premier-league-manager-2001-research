"""Original first/second 5DAA47 / 5DACC0 native club-class score factor."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack,pack_into,unpack_from
from unittest import TestCase
from original_match_5daa47_stage_two_factor import (
    OriginalStageTwoFactorSourceError,
    source_original_5daa47_or_5dacc0_team_factor as source,
)


def kw(side=1,enum=0,klass=7):
    club=bytearray(0x18)
    pack_into('<I',club,0x14,klass)
    return dict(original_side=side,
        original_team_pointer=0x4000,
        original_team_record=bytes(club),
        original_874be0_global_class_table_pointer=0x100000,
        original_410ff0_reached_ecx_class_pointer=0x100000+klass*108,
        original_410ff0_return_eax=enum)


class OriginalStageTwoClassFactorsTests(TestCase):
    def test_both_original_scored_sides_share_six_source_factor_constants(self):
        starts={1:(0x5daa53,0x5daa60,0x5daa75,0x5daa8b,0x5daa98,0x5daaad),
                2:(0x5dacd1,0x5dacde,0x5dacf4,0x5dad09,0x5dad16,0x5dad2c)}
        for side in (1,2):
            for index,val in enumerate((.9,.8,.7,.6,.5,.5)):
                with self.subTest(side=side,index=index):
                    r=source(**kw(side,index))
                    self.assertEqual(r.original_qword_factor,pack('<d',val))
                    self.assertEqual(r.original_source_jump_va,starts[side][index])
                    self.assertFalse(r.original_lookup_executed)
                    self.assertFalse(r.original_5da250_calculator_executed)
                    self.assertFalse(r.game_state_mutated)

    def test_native_enum_six_or_large_uses_literal_fallback_last_factor_not_unknown_score(self):
        for side in (1,2):
            for value in (6,7,0x7fffffff,0xffffffff):
                x=source(**kw(side,value))
                self.assertEqual(x.original_qword_factor,pack('<d',.5))
                self.assertEqual(x.original_source_jump_va,0x5daac3 if side==1 else 0x5dad41)

    def test_unreached_full_native_class_table_pointer_or_wrong_team_rejected(self):
        valid=kw()
        for delta in (
            {'original_side':0},
            {'original_side':True},
            {'original_team_pointer':0},
            {'original_team_record':bytes(10)},
            {'original_team_record':bytearray(0x18)},
            {'original_874be0_global_class_table_pointer':0},
            {'original_410ff0_reached_ecx_class_pointer':0x100001},
            {'original_410ff0_return_eax':None},
            {'original_410ff0_return_eax':True},
            {'original_410ff0_return_eax':-1},
        ):
            with self.subTest(delta=delta),self.assertRaises(OriginalStageTwoFactorSourceError):
                source(**(valid|delta))
        overflowing=kw(klass=0xffffffff)
        with self.assertRaises(OriginalStageTwoFactorSourceError):
            source(**overflowing)

    def test_source_original_5daa0b_5dac89_paired_jump_tables_and_qword_constants(self):
        exe=environ.get('FM2001_ORIGINAL_EXE')
        if not exe:self.skipTest('canonical original executable not present in CI')
        raw=Path(exe).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
            4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x5daa2c:'8b 4e 14',
            0x5daa2f:'8b 15 e0 4b 87 00',
            0x5daa39:'8d 04 49',
            0x5daa3c:'8d 0c c0',
            0x5daa3f:'8d 0c 8a',
            0x5daa42:'e8 a9 65 e3 ff',
            0x5daa47:'83 f8 05',
            0x5daa4c:'ff 24 85 fc b9 5d 00',
            0x5dacaa:'8b 4b 14',
            0x5dacb4:'8b 0d e0 4b 87 00',
            0x5dacc0:'e8 2b 63 e3 ff',
            0x5dacc5:'83 f8 05',
            0x5dacca:'ff 24 85 14 ba 5d 00',
        }
        for va,h in sites.items():
            with self.subTest(addr=hex(va)):
                b=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
        for pos,expected in (
          (0x5db9fc,(0x5daa53,0x5daa60,0x5daa75,0x5daa8b,0x5daa98,0x5daaad)),
          (0x5dba14,(0x5dacd1,0x5dacde,0x5dacf4,0x5dad09,0x5dad16,0x5dad2c)),
        ):
            self.assertEqual(tuple(unpack_from('<I',raw,pos-0x400000+4*i)[0] for i in range(6)),expected)
        self.assertEqual(tuple(unpack_from('<d',raw,0x821e00-0x400000+i*8)[0] for i in range(5)),
                         (.9,.8,.7,.6,.5))
