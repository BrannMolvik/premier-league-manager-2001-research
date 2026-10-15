"""Original native 5DA785 grid-coordinate math and 5112F0 conditional FPU factors."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase

from original_match_5da785_grid_distance import (
    OriginalMatchGridDistanceSourceError,
    _cell,
    source_original_5da785_team_grid_distance as distance,
    source_original_5da889_distance_multiplier as factor,
)


def record(x,y):
    b=bytearray(0x28)
    pack_into("<ii",b,0x20,x,y)
    return bytes(b)


def source(x=0,y=0,u=0,v=0):
    return dict(original_first_team_pointer=0x1000,
        original_first_team_record=record(x,y),
        original_opponent_from_5da30a_pointer=0x2000,
        original_opponent_reached_esp44_pointer_at_5da7fb=0x2000,
        original_opponent_team_record=record(u,v))


class OriginalMatchGridCoordinateTests(TestCase):
    def test_signed_coordinate_magic_division_writes_original_integer_cells(self):
        for value,expected in (
            (0,0),(1,0),(599,0),(600,1),(999,1),
            (1000,0),(1599,0),(1600,1),(10000,1),(10600,2),
            (-1,0),(-599,0),(-600,-1),(-999,-1),
            (-1000,0),(-1600,-1),(-10000,-1),(-10600,-2),
        ):
            with self.subTest(x=value):self.assertEqual(_cell(value),expected)

    def test_actual_native_signed_magic_numerators_match_trunc_division(self):
        magic600=0x1b4e81b5
        magic10000=0x68db8bad
        def tc_div(x,n):
            return x//n if x>=0 else -((-x)//n)
        def magic(x,m,shift):
            high=(x*m)>>32
            quotient=high>>shift
            return quotient+int(quotient<0)
        samples=((-0x80000000,-200000001,-100000,-10001,-10000,-1600,
                 -1000,-999,-600,-599,-1,0,1,599,600,999,1000,
                 1600,9999,10000,10001,100000,0x7fffffff))
        for x in samples:
            with self.subTest(x=x):
                r=x-tc_div(x,1000)*1000
                self.assertEqual(magic(r,magic600,6),tc_div(r,600))
                self.assertEqual(magic(x,magic10000,12),tc_div(x,10000))
                self.assertEqual(_cell(x),tc_div(x,10000)+tc_div(r,600))

    def test_zero_one_and_longer_distances_and_integer_sqrt_truncation(self):
        for coords,expected in (
            ((0,0,0,0),(0,0,0)),
            ((10000,0,0,0),(1,0,1)),
            ((10600,0,0,0),(2,0,2)),
            ((30000,40000,0,0),(3,4,5)),
            ((-30000,-40000,0,0),(3,4,5)),
            ((30000,30000,0,0),(3,3,4)),
        ):
            x,y,u,v=coords
            with self.subTest(coords=coords):
                got=distance(**source(x,y,u,v))
                self.assertEqual((*got.source_absolute_coordinate_differences,
                                  got.original_668350_truncated_fsqrtdistance),expected)
                self.assertEqual(got.original_integer_squares_sum,sum(a*a for a in expected[:2]))
                self.assertFalse(got.original_native_math_executed)
                self.assertFalse(got.match_result_written)

    def test_original_distance_gate_5112f0_and_1point2_1point5_constants(self):
        zero=distance(**source())
        one=distance(**source(10000,0))
        long=distance(**source(30000,40000))
        self.assertEqual(factor(original_grid_distance=zero,
                        original_5112f0_al_nonzero_if_reached=None).source_first_fpu_multiplier,1.5)
        self.assertEqual(factor(original_grid_distance=one,
                        original_5112f0_al_nonzero_if_reached=False).source_first_fpu_multiplier,1.2)
        self.assertEqual(factor(original_grid_distance=one,
                        original_5112f0_al_nonzero_if_reached=True).source_first_fpu_multiplier,1.5)
        self.assertEqual(factor(original_grid_distance=long,
                        original_5112f0_al_nonzero_if_reached=False).source_first_fpu_multiplier,1.)
        self.assertEqual(factor(original_grid_distance=long,
                        original_5112f0_al_nonzero_if_reached=True).source_second_fpu_multiplier,1.5)
        for bad_r,val in ((zero,False),(one,None),(long,1),(long,0)):
            with self.subTest(distance=bad_r.original_668350_truncated_fsqrtdistance,al=val),self.assertRaises(OriginalMatchGridDistanceSourceError):
                factor(original_grid_distance=bad_r,
                       original_5112f0_al_nonzero_if_reached=val)

    def test_incomplete_source_pointer_mismatch_and_signed_squared_overflow_rejected(self):
        ok=source()
        bads=[
            dict(original_first_team_pointer=0),
            dict(original_opponent_from_5da30a_pointer=0x1000),
            dict(original_opponent_reached_esp44_pointer_at_5da7fb=0x2001),
            dict(original_first_team_record=bytes(0x24)),
            dict(original_first_team_record=bytearray(0x28)),
            dict(original_opponent_team_record=b''),
            dict(original_opponent_from_5da30a_pointer=True),
            dict(original_first_team_record=record(0x7fffffff,0)),
            dict(original_first_team_record=record(-0x80000000,0)),
        ]
        for change in bads:
            with self.subTest(change=change.keys()),self.assertRaises(OriginalMatchGridDistanceSourceError):
                distance(**(ok|change))

    def test_original_private_pe_grid_distance_division_sqrt_and_668350_truncation(self):
        path=environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('private original PE unavailable')
        raw=Path(path).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
            4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x5da785:'8b 46 20 8b 4f 20 99',
            0x5da796:'f7 ff b8 b5 81 4e 1b',
            0x5da79d:'f7 ea c1 fa 06',
            0x5da7c1:'b8 ad 8b db 68',
            0x5da7f4:'8b 46 24',
            0x5da7fb:'8b 54 24 44',
            0x5da86a:'0f af d0',
            0x5da86f:'0f af c1',
            0x5da878:'db 44 24 10 d9 fa',
            0x5da87e:'e8 cd da 08 00',
            0x5da885:'85 ff 74 2e',
            0x5da88c:'e8 5f 6a f3 ff',
            0x5da895:'83 ff 01',
            0x5da89e:'dc 0d 78 d6 7b 00',
            0x5da8bb:'dc 0d f8 d8 7b 00',
            0x66835f:'80 cc 0c',
            0x668369:'df 7d f4',
        }
        for addr,h in sites.items():
            with self.subTest(addr=hex(addr)):
                sig=bytes.fromhex(h)
                self.assertEqual(raw[addr-0x400000:addr-0x400000+len(sig)],sig)
        for loc,target in ((0x5da87e,0x668350),(0x5da88c,0x5112f0)):
            self.assertEqual(loc+5+unpack_from('<i',raw,loc-0x400000+1)[0],target)
        self.assertEqual((unpack_from('<d',raw,0x7bd678-0x400000)[0],
                          unpack_from('<d',raw,0x7bd8f8-0x400000)[0]),(1.2,1.5))
