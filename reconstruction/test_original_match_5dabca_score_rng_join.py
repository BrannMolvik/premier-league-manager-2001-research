"""Original 5DABCA and 5DAE45 int32 clamp to thread-local score RNG."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase

from original_match_5dabca_score_rng_join import (
    OriginalScoreBoundSourceError,
    source_original_5dabca_5dae45_score_rng_from_reached_bound as join,
)


def inputs(side=1,value=1,seed=0):
    record=bytearray(0x74)
    pack_into('<I',record,0x14,seed)
    return dict(original_source_scored_side=side,
        original_first_668350_reached_eax_signed=value,
        original_66d553_tls_record_pointer=0x8000,
        original_66d553_tls_record_before_66951c=bytes(record))


class OriginalStageBoundedScoreRngTests(TestCase):
    def test_first_and_second_original_score_rng_share_native_clamp_and_tls_step(self):
        for side,site,truncate in ((1,0x5dabed,0x5dabca),
                                   (2,0x5dae68,0x5dae45)):
            for val in (-0x80000000,-3,0,1,2,100,0x7fffffff):
                with self.subTest(side=side,val=val):
                    r=join(**inputs(side,val))
                    self.assertEqual(r.original_positive_clamped_edi_bound,max(1,val))
                    self.assertEqual(r.original_first_truncate_call_va,truncate)
                    self.assertEqual(r.original_score_rng_source.original_call_site,site)
                    self.assertEqual(r.original_score_rng_source.original_64d540_bound,max(1,val))
                    self.assertEqual(r.original_score_rng_source.original_66951c_rand15,38)
                    self.assertEqual(r.original_score_rng_source.original_64d540_return_eax,
                                     (38*max(1,val))//32768)
                    self.assertFalse(r.original_64d540_executed)
                    self.assertFalse(r.saved_match_world_modified)

    def test_original_rng_results_are_not_inferred_from_same_seed_on_two_teams(self):
        a=join(**inputs(1,500,seed=0))
        b=join(**inputs(2,700,seed=1))
        self.assertEqual(a.original_score_rng_source.original_seed_after,0x269ec3)
        self.assertEqual(b.original_score_rng_source.original_seed_after,0x29e2c0)
        self.assertNotEqual(a.original_score_rng_source.original_64d540_return_eax,
                            b.original_score_rng_source.original_64d540_return_eax)
        self.assertFalse(a.original_score_rng_source.original_rng_state_committed)
        self.assertFalse(b.original_score_rng_source.original_rng_state_committed)

    def test_requires_actual_original_first_668350_return_and_real_tls_record(self):
        good=inputs()
        cases=(
            {'original_source_scored_side':0},
            {'original_source_scored_side':True},
            {'original_first_668350_reached_eax_signed':True},
            {'original_first_668350_reached_eax_signed':float(4)},
            {'original_first_668350_reached_eax_signed':0x80000000},
            {'original_first_668350_reached_eax_signed':-0x80000001},
        )
        for invalid in cases:
            with self.subTest(case=invalid),self.assertRaises(OriginalScoreBoundSourceError):
                join(**(good|invalid))
        from original_match_64d540_tls_score_rng import OriginalNative64D540SourceError
        for invalid in (
            {'original_66d553_tls_record_pointer':0},
            {'original_66d553_tls_record_before_66951c':None},
            {'original_66d553_tls_record_before_66951c':b'\0'*0x15},
        ):
            with self.subTest(case=invalid),self.assertRaises(OriginalNative64D540SourceError):
                join(**(good|invalid))

    def test_canonical_private_original_both_668350_clamps_and_rng_calls(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('owner-private original game PE not in hosted CI')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        source={
            0x5dabca:'e8 81 d7 08 00',
            0x5dabcf:'8b f8 83 ff 01',
            0x5dabd4:'7d 05',
            0x5dabd6:'bf 01 00 00 00',
            0x5dabe4:'57',
            0x5dabed:'e8 4e 29 07 00',
            0x5dae45:'e8 06 d5 08 00',
            0x5dae4a:'8b f8 83 ff 01',
            0x5dae4f:'7d 05',
            0x5dae51:'bf 01 00 00 00',
            0x5dae5f:'57',
            0x5dae68:'e8 d3 26 07 00',
        }
        for va,h in source.items():
            with self.subTest(va=hex(va)):
                b=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
        for site,target in ((0x5dabca,0x668350),(0x5dabed,0x64d540),
                            (0x5dae45,0x668350),(0x5dae68,0x64d540)):
            self.assertEqual(site+5+unpack_from('<i',raw,site-0x400000+1)[0],target)
