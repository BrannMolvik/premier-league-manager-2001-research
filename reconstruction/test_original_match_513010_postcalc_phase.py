"""Original 513010 source match calculator/presentation/tail branch correctness."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import unpack_from
from unittest import TestCase

from original_match_513010_postcalc_phase import (
    OriginalMatchSourcePipelineError,
    source_original_513010_calculator_presentation_and_tail as plan,
)


def data():
    return dict(original_5130c2_v34_al_nonzero=True,
                original_reached_516080_al_nonzero=False,
                original_match_flags44_after_preparation_at_513238=0x10,
                original_match_flags44_after_calculator_at_513257=0x10,
                original_reached_mode_877530_at_51325d=3)


class OriginalMatch513010PhasesTests(TestCase):
    def test_false_v34_still_reaches_original_v38_and_v3c_without_match_calculation(self):
        kw=dict.fromkeys(data())
        kw['original_5130c2_v34_al_nonzero']=False
        r=plan(**kw)
        self.assertTrue(r.original_512d80_cleanup_called)
        self.assertFalse(r.original_calculator_5da2f0_called)
        self.assertIsNone(r.original_presentation_wrapper_va)
        self.assertTrue(r.original_v38_callback_reached)
        self.assertTrue(r.original_v3c_callback_reached)

    def test_true_516080_does_not_skip_calculator_if_513238_bit5_clear(self):
        r=plan(**(data()|{'original_reached_516080_al_nonzero':True}))
        self.assertTrue(r.original_512d80_cleanup_called)
        self.assertTrue(r.original_calculator_5da2f0_called)
        self.assertIsNone(r.original_presentation_wrapper_va)
        self.assertFalse(r.original_calculation_executed)
        self.assertFalse(r.original_saved_game_state_written)

    def test_completed_bit5_at_513238_skips_calculator_and_postcalc_mode(self):
        v=data()
        v.update(original_match_flags44_after_preparation_at_513238=0x30,
                 original_match_flags44_after_calculator_at_513257=None,
                 original_reached_mode_877530_at_51325d=None)
        r=plan(**v)
        self.assertFalse(r.original_calculator_5da2f0_called)
        self.assertTrue(r.original_v38_callback_reached)
        self.assertTrue(r.original_v3c_callback_reached)
        for bad in ('original_match_flags44_after_calculator_at_513257',
                    'original_reached_mode_877530_at_51325d'):
            v2=dict(v)
            v2[bad]=0
            with self.assertRaises(OriginalMatchSourcePipelineError):
                plan(**v2)

    def test_source_all_four_modes_after_original_calc_and_distinct_presentation(self):
        expected=((0x533d80,0),(0x533d80,1),(0x5331c0,None),(None,None))
        for mode in range(4):
            with self.subTest(mode=mode):
                r=plan(**(data()|{'original_reached_mode_877530_at_51325d':mode}))
                self.assertTrue(r.original_calculator_5da2f0_called)
                self.assertEqual((r.original_presentation_wrapper_va,
                                  r.original_3d_wrapper_variant),expected[mode])
                self.assertTrue(r.original_v38_callback_reached)
                self.assertTrue(r.original_v3c_callback_reached)

    def test_flags_reloaded_after_calculation_can_remove_human_mode_presentation(self):
        v=data()
        v.update(original_match_flags44_after_calculator_at_513257=0,
                 original_reached_mode_877530_at_51325d=None)
        r=plan(**v)
        self.assertTrue(r.original_calculator_5da2f0_called)
        self.assertIsNone(r.original_presentation_wrapper_va)

    def test_missing_actual_reached_flags_or_fake_v34_mode_returns_fail_closed(self):
        valid=data()
        bads=(
            {'original_5130c2_v34_al_nonzero':1},
            {'original_reached_516080_al_nonzero':None},
            {'original_reached_516080_al_nonzero':0},
            {'original_match_flags44_after_preparation_at_513238':True},
            {'original_match_flags44_after_preparation_at_513238':None},
            {'original_match_flags44_after_preparation_at_513238':0x100000000},
            {'original_match_flags44_after_calculator_at_513257':None},
            {'original_match_flags44_after_calculator_at_513257':-1},
            {'original_reached_mode_877530_at_51325d':5},
            {'original_reached_mode_877530_at_51325d':True},
        )
        for changed in bads:
            with self.subTest(changed=changed),self.assertRaises(OriginalMatchSourcePipelineError):
                plan(**(valid|changed))

    def test_false_v34_skips_all_downstream_receipts(self):
        v=data()
        v['original_5130c2_v34_al_nonzero']=False
        for k in tuple(v):
            if k!='original_5130c2_v34_al_nonzero':
                copy=dict.fromkeys(v)
                copy.update({k:v[k]})
                copy['original_5130c2_v34_al_nonzero']=False
                with self.subTest(k=k),self.assertRaises(OriginalMatchSourcePipelineError):
                    plan(**copy)

    def test_original_private_executable_has_native_5130c2_513238_513252_and_v38_v3c(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('owner-private original executable not available')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,
                '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        source={
            0x5130c2:'ff 50 34 84 c0 75 12',
            0x5130ce:'e8 ad fc ff ff',
            0x5130d6:'e9 b9 01 00 00',
            0x5130dc:'e8 9f 2f 00 00',
            0x5130ef:'e9 41 01 00 00',
            0x513238:'8b 4e 44 5d c1 e9 05',
            0x51323f:'f6 c1 01 75 50',
            0x513252:'e8 99 70 0c 00',
            0x513257:'f6 46 44 10 74 37',
            0x513262:'83 e8 00 74 1e',
            0x51326a:'48 75 27',
            0x513272:'e8 49 ff 01 00',
            0x51328c:'e8 ef 0a 02 00',
            0x51329d:'ff 52 38',
            0x5132a9:'ff 52 3c',
        }
        for va,h in source.items():
            with self.subTest(va=hex(va)):
                b=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
        for call,dest in ((0x5130ce,0x512d80),(0x5130dc,0x516080),
                          (0x513252,0x5da2f0),(0x513272,0x5331c0),
                          (0x51328c,0x533d80)):
            self.assertEqual(call+5+unpack_from('<i',raw,call-0x400000+1)[0],dest)
