"""Native 5DA250 alternate x87 branches, no invented computed float."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack
from unittest import TestCase
from original_native_5da250_fpu_branch_source import (
    Original5DA250BranchSourceError,source_original_5da250_reached_x87_branch,
    source_original_5da250_finite_prethreshold_path,
)

BASE=dict(original_esp4_qword=pack('<d',1.25),original_espc_qword=pack('<d',2.5))
def attempt(statuses):
    d=dict(zip(('original_5da25a_ah','original_5da26b_ah_if_reached','original_5da29c_ah_if_reached',
                'original_5da2bb_ah_if_reached','original_5da280_ah_if_reached'),statuses))
    return source_original_5da250_reached_x87_branch(**(BASE|d))

class Original5DA250SourceBranchTests(TestCase):
    def test_early_zero_comparison_and_last_constant_branch(self):
        a=attempt((0,None,None,None,None))
        b=attempt((0x41,0x41,0,0,None))
        self.assertEqual((a.original_native_path,a.original_literal_return_qword_if_exact),
                         ('5da25f-direct-literal-0p1',pack('<d',0.1)))
        self.assertEqual((b.original_native_path,b.original_literal_return_qword_if_exact),
                         ('5da2d6-direct-literal-2p0',pack('<d',2.0)))
        self.assertFalse(a.original_native_5da250_executed)

    def test_three_possible_numeric_paths_have_bounded_source_outcomes(self):
        for status,path in (
            ((0x41,0, None,None,0),'5da274-ratio'),
            ((0x41,0x41,1,None,0),'5da2a3-negative-half-ratio'),
            ((0x41,0x41,0,1,0),'5da2c2-weighted-negative-ratio'),
        ):
            with self.subTest(route=path):
                out=attempt(status)
                self.assertEqual(out.original_native_path,path+'-x87-computed')
                self.assertTrue(out.original_computed_x87_value_unresolved)
                self.assertIsNone(out.original_literal_return_qword_if_exact)
                clamped=attempt(status[:-1]+(1,))
                self.assertEqual(clamped.original_native_path,path+'-clamped-to-0p1')
                self.assertEqual(clamped.original_literal_return_qword_if_exact,pack('<d',0.1))

    def test_wrong_unreached_status_or_source_argument_fails_closed(self):
        for statuses in (
            (0x41,None,None,None,None),
            (0,1,None,None,None),
            (0x41,0,1,None,0),
            (0x41,0x41,0,0,0),
        ):
            with self.subTest(statuses=statuses):
                with self.assertRaises(Original5DA250BranchSourceError):attempt(statuses)
        d=dict(original_5da25a_ah=0,original_5da26b_ah_if_reached=None,
               original_5da29c_ah_if_reached=None,original_5da2bb_ah_if_reached=None,
               original_5da280_ah_if_reached=None)
        with self.assertRaises(Original5DA250BranchSourceError):
            source_original_5da250_reached_x87_branch(**(BASE|d|{'original_espc_qword':b''}))

    def test_finite_prethreshold_source_paths_and_boundaries(self):
        examples=(
            ((2.0,1.0),'5da25f-direct-literal-0p1'),
            ((1.0,2.0),'5da274-ratio'),
            ((2.0,2.0),'5da274-ratio'),
            ((-1.0,4.0),'5da2a3-negative-half-ratio'),
            ((-3.0,4.0),'5da2c2-weighted-negative-ratio'),
            ((-5.0,4.0),'5da2d6-direct-literal-2p0'),
            ((0.0,0.0),'5da2d6-direct-literal-2p0'),
            ((0.0,5e-324),'5da2a3-negative-half-ratio'),
            ((-1.0,2.0),'5da2c2-weighted-negative-ratio'),
        )
        for (a,b),expected in examples:
            with self.subTest(a=a,b=b):
                self.assertEqual(source_original_5da250_finite_prethreshold_path(
                    original_esp4_qword=pack('<d',a),original_espc_qword=pack('<d',b)), expected)

    def test_finite_branch_rejects_unproven_nan_infinities_and_missing_bytes(self):
        for a,b in ((float('nan'),1.0),(1.0,float('inf')),(-float('inf'),1.0)):
            with self.subTest(a=a,b=b):
                with self.assertRaises(Original5DA250BranchSourceError):
                    source_original_5da250_finite_prethreshold_path(
                        original_esp4_qword=pack('<d',a),original_espc_qword=pack('<d',b))
        with self.assertRaises(Original5DA250BranchSourceError):
            source_original_5da250_finite_prethreshold_path(
                original_esp4_qword=b'\x00',original_espc_qword=pack('<d',1.0))

    def test_private_original_5da250_static_branch_opcodes(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original absent in CI')
        original=Path(p).read_bytes()
        self.assertEqual((len(original),sha256(original).hexdigest()),(4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sig={0x5da250:'dd 44 24 0c',0x5da254:'dd 44 24 04',0x5da25a:'df e0',0x5da25c:'f6 c4 41',
             0x5da25f:'74 26',0x5da26b:'df e0',0x5da26d:'f6 c4 41',0x5da272:'75 1e',
             0x5da27a:'dc 15 78 db 7b 00',0x5da280:'df e0',0x5da282:'f6 c4 01',
             0x5da285:'74 08',0x5da29c:'df e0',0x5da29e:'f6 c4 01',
             0x5da2bb:'df e0',0x5da2bd:'f6 c4 01',0x5da2d8:'dd 05 a8 dc 7b 00'}
        for va,val in ((0x7bd5f8,0.0),(0x7bdb78,0.1),(0x7d73d0,-0.5),
                       (0x7bd6b0,1.0),(0x7bfca8,4.0),(0x7bd8f8,1.5),(0x7bdca8,2.0)):
            self.assertEqual(original[va-0x400000:va-0x400000+8],pack('<d',val))
        for va,bytestr in sig.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(bytestr)
                self.assertEqual(original[va-0x400000:va-0x400000+len(expected)],expected)
