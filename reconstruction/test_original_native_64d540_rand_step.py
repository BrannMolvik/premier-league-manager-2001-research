"""Native per-thread 66951C LCG and 64D540 scaled draw, static source."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase
from original_native_64d540_rand_step import (
    OriginalNative64D540SourceError,source_original_66951c_then_64d540_scaled_draw,
)

def fixture(seed=1,arg=100):
    b=bytearray(0x18)
    pack_into('<I',b,0x14,seed)
    return dict(original_66d553_rng_owner_pointer=0x20000,
                original_rng_owner_before_66951c=bytes(b),
                original_64d540_reached_signed_argument=arg)

class OriginalNative64D540DrawTests(TestCase):
    def test_original_state_and_signed_bound_then_next_draw(self):
        for seed in (0,1,0xffffffff,0x80000000):
            for arg in (-2147483648,-101,-1,0,1,123,2147483647):
                with self.subTest(seed=seed,arg=arg):
                    original=fixture(seed,arg)
                    res=source_original_66951c_then_64d540_scaled_draw(**original)
                    nextseed=(seed*0x343fd+0x269ec3)&0xffffffff
                    rng=(nextseed>>16)&0x7fff
                    signed=(rng*arg)
                    result=(-1 if signed<0 else 1)*(abs(signed)//32768)
                    self.assertEqual((res.original_seed_after,res.original_66951c_unsigned15_output,res.source_scaled_truncate_result),(nextseed,rng,result))
                    self.assertEqual(unpack_from('<I',res.original_owner_after_source_step,0x14)[0],nextseed)
                    self.assertEqual(unpack_from('<I',original['original_rng_owner_before_66951c'],0x14)[0],seed)
                    self.assertFalse(res.native_rng_executed)

    def test_zero_argument_still_consumes_native_rng_state(self):
        one=source_original_66951c_then_64d540_scaled_draw(**fixture(0,0))
        self.assertEqual(one.source_scaled_truncate_result,0)
        self.assertNotEqual(one.original_seed_after,one.original_seed_before)
        later=source_original_66951c_then_64d540_scaled_draw(**fixture(one.original_seed_after,0))
        self.assertNotEqual(one.original_seed_after,later.original_seed_after)

    def test_missing_owner_and_forged_native_arg_fail_closed(self):
        cases=({'original_66d553_rng_owner_pointer':0},
               {'original_66d553_rng_owner_pointer':True},
               {'original_rng_owner_before_66951c':b''},
               {'original_64d540_reached_signed_argument':True},
               {'original_64d540_reached_signed_argument':1<<31},
               {'original_64d540_reached_signed_argument':-(1<<31)-1})
        x=fixture()
        for c in cases:
            with self.subTest(c=c):
                with self.assertRaises(OriginalNative64D540SourceError):
                    source_original_66951c_then_64d540_scaled_draw(**(x|c))

    def test_private_pe_lcg_and_rand_opcode_chain(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('canonical private executable not shipped to hosted CI')
        pe=Path(p).read_bytes()
        self.assertEqual((len(pe),sha256(pe).hexdigest()),(4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sig={0x66951c:'e8 32 40 00 00',0x669521:'8b 48 14',0x669524:'69 c9 fd 43 03 00',0x66952a:'81 c1 c3 9e 26 00',0x669530:'89 48 14',0x669533:'8b c1',0x669535:'c1 e8 10',0x669538:'25 ff 7f 00 00',0x64d540:'51',0x64d541:'e8 d6 bf 01 00',0x64d54a:'db 44 24 00',0x64d54e:'da 4c 24 08',0x64d552:'dc 0d 60 80 7d 00',0x64d558:'e8 f3 ad 01 00'}
        for va,code in sig.items():
            with self.subTest(va=hex(va)):
                actual=bytes.fromhex(code)
                self.assertEqual(pe[va-0x400000:va-0x400000+len(actual)],actual)
