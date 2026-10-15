"""Original 66951C/64D540 match-score RNG, actual per-thread TLS seed owner."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase

from original_match_64d540_tls_score_rng import (
    OriginalNative64D540SourceError,
    SOURCE_NATIVE_CRT_TLS_RNG_OFFSET,
    source_original_64d540_bounded_tls_match_rng as source,
)


def receipt(*,site=0x5dabed,seed=0,bound=32768,ptr=0x9000):
    r=bytearray(b'\xa5'*0x74)
    pack_into("<I",r,0x14,seed)
    return dict(original_reached_score_call_site=site,
        original_66d553_tls_record_pointer=ptr,
        original_66d553_tls_record_before_66951c=bytes(r),
        original_64d540_reached_positive_bound=bound)


class OriginalMatchTLSNativeRngTests(TestCase):
    def test_source_lcg_fixed_crt_seed_rand15_and_projection_are_exact(self):
        known={
           0:(0x00269ec3,38),
           1:(0x0029e2c0,41),
           0xffffffff:(0x00235ac6,35),
        }
        for seed,(next_seed,rand) in known.items():
            v=receipt(seed=seed)
            r=source(**v)
            self.assertEqual((r.original_seed_before,r.original_seed_after,
                              r.original_66951c_rand15),
                             (seed,next_seed,rand))
            self.assertEqual(r.original_64d540_return_eax,rand)
            self.assertEqual(unpack_from('<I',r.projected_tls_record_after,0x14)[0],next_seed)
            self.assertEqual(r.projected_tls_record_after[:0x14],
                             v['original_66d553_tls_record_before_66951c'][:0x14])
            self.assertEqual(r.projected_tls_record_after[0x18:],
                             v['original_66d553_tls_record_before_66951c'][0x18:])
            self.assertFalse(r.original_native_tls_callback_executed)
            self.assertFalse(r.original_rng_state_committed)
            self.assertFalse(r.original_game_state_modified)

    def test_both_score_rng_call_sites_preserve_independent_tls_ownership(self):
        first=source(**receipt(site=0x5dabed,seed=0,bound=500))
        second=source(**receipt(site=0x5dae68,seed=1,bound=700,ptr=0xA000))
        self.assertEqual(first.original_64d540_return_eax,38*500//32768)
        self.assertEqual(second.original_64d540_return_eax,41*700//32768)
        self.assertNotEqual(first.original_tls_record_pointer,second.original_tls_record_pointer)
        self.assertNotEqual(first.original_seed_after,second.original_seed_after)

    def test_original_fimul_rand_result_positive_bound_and_trunc_no_round_nearest(self):
        for seed in (0,1,0x75bcd15,0xffffffff):
            for bound in (1,2,500,32767,32768,999999,0x7fffffff):
                with self.subTest(seed=seed,bound=bound):
                    r=source(**receipt(seed=seed,bound=bound))
                    self.assertEqual(r.original_64d540_return_eax,
                                     (r.original_66951c_rand15*bound)//32768)
                    self.assertGreaterEqual(r.original_64d540_return_eax,0)
                    self.assertLess(r.original_64d540_return_eax,bound)

    def test_projected_tls_state_can_be_used_only_when_next_66d553_read_confirms_it(self):
        begin=receipt(seed=0,bound=32768)
        one=source(**begin)
        # Explicitly supplied second actual per-thread snapshot is required;
        # this test demonstrates only a source-compatible consecutive draw.
        two=source(**(begin|{
             'original_66d553_tls_record_before_66951c':one.projected_tls_record_after}))
        self.assertEqual((one.original_66951c_rand15,two.original_66951c_rand15),(38,7719))
        self.assertEqual(two.original_seed_after,0x1e276b7a)
        self.assertFalse(two.original_rng_state_committed)

    def test_reject_wrong_native_call_owner_and_unsourced_or_unclamped_bound(self):
        valid=receipt()
        cases=(
           {'original_reached_score_call_site':0x5dab07},
           {'original_reached_score_call_site':0},
           {'original_reached_score_call_site':True},
           {'original_66d553_tls_record_pointer':None},
           {'original_66d553_tls_record_pointer':False},
           {'original_66d553_tls_record_before_66951c':b'\x00'*0x17},
           {'original_66d553_tls_record_before_66951c':bytearray(0x74)},
           {'original_64d540_reached_positive_bound':0},
           {'original_64d540_reached_positive_bound':-1},
           {'original_64d540_reached_positive_bound':0x80000000},
           {'original_64d540_reached_positive_bound':1.},
           {'original_64d540_reached_positive_bound':True},
        )
        for changed in cases:
            with self.subTest(changed=changed),self.assertRaises(OriginalNative64D540SourceError):
                source(**(valid|changed))

    def test_original_private_pe_tls_rand_and_score_rng_sites_and_binary_scale(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('canonical private original exe unavailable in CI')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
             4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x66951c:'e8 32 40 00 00',
            0x669521:'8b 48 14',
            0x669524:'69 c9 fd 43 03 00',
            0x66952a:'81 c1 c3 9e 26 00',
            0x669530:'89 48 14',
            0x669533:'8b c1 c1 e8 10',
            0x669538:'25 ff 7f 00 00',
            0x64d540:'51 e8 d6 bf 01 00',
            0x64d54a:'db 44 24 00',
            0x64d54e:'da 4c 24 08',
            0x64d552:'dc 0d 60 80 7d 00',
            0x64d558:'e8 f3 ad 01 00',
            0x5dabed:'e8 4e 29 07 00',
            0x5dae68:'e8 d3 26 07 00',
            0x66d555:'ff 15 e4 d0 7b 00',
        }
        for va,h in sites.items():
            with self.subTest(va=hex(va)):
                b=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
        for call,target in ((0x66951c,0x66d553),(0x64d541,0x66951c),
                            (0x64d558,0x668350),(0x5dabed,0x64d540),
                            (0x5dae68,0x64d540)):
            signed=unpack_from('<i',raw,call-0x400000+1)[0]
            self.assertEqual(call+5+signed,target)
        from struct import unpack_from as read
        self.assertEqual(read('<d',raw,0x7d8060-0x400000)[0],1/32768)
