"""Native 512D80 fallback score writes and 516040–516070 order."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase
from original_native_66d553_tls_initial_state import source_original_66d553_reached_crt_tls_record
from original_match_512d80_fallback_scores import (
    Original512D80SourceError,Original512D80SpecialGate as Gate,
    source_original_512d80_fallback_random_scores as project,
)


def tls(seed=1):
    raw=bytearray(0x74);pack_into('<I',raw,0x14,seed)
    return source_original_66d553_reached_crt_tls_record(
        original_tls_slot_dword_84ad40=9,
        original_tlsgvalue_return_pointer=0x7000,
        original_existing_tls_record_if_reached=bytes(raw),
        original_calloc_return_pointer_if_fresh=None,
        original_calloc_zero_record_if_fresh=None,
        original_tlssetvalue_return_eax_if_fresh=None,
        original_thread_id_callback_return_eax_if_fresh=None)


def no_gates():
    return tuple(Gate(va,False,None,None,None)
                 for va in (0x516040,0x516050,0x516060,0x516070))


def inputs():
    record=bytearray(0xd54)
    pack_into('<I',record,0,0x4000);pack_into('<I',record,0x5b0,0x5000)
    return dict(original_v34_at_5130c2_returned_false=False,
                original_context_pointer=0x9000,
                original_context_record_before_512d80=bytes(record),
                original_tls_record_source=tls(),
                original_first_team_407770_eax_nonzero=True,
                original_second_team_407770_eax_nonzero=True,
                original_four_special_gates=no_gates())


class Original512D80FallbackTests(TestCase):
    def test_two_immediate_native_crt_rand6_calls_and_full_source_context_scores(self):
        x=project(**inputs())
        self.assertEqual((x.first_64d540_six.original_seed_before,
                          x.first_64d540_six.original_seed_after,
                          x.first_64d540_six.source_scaled_truncate_result),
                         (1,0x29e2c0,0))
        self.assertEqual((x.second_64d540_six.original_seed_before,
                          x.second_64d540_six.source_scaled_truncate_result),
                         (0x29e2c0,3))
        self.assertEqual((x.original_first_score_context_d4c,x.original_second_score_context_d50),(0,3))
        self.assertTrue(x.original_global_8774c4_write_one)
        self.assertFalse(x.live_game_state_updated)
        self.assertFalse(x.native_v38_v3c_executed)
        self.assertFalse(x.native_original_rng_executed)

    def test_two_407770_eligibility_checks_zero_scores_but_do_not_refund_rng(self):
        c=inputs()
        x=project(**(c|{'original_first_team_407770_eax_nonzero':False,
                        'original_second_team_407770_eax_nonzero':False}))
        self.assertEqual((x.original_first_score_context_d4c,x.original_second_score_context_d50),(0,0))
        self.assertEqual(x.second_64d540_six.original_seed_before,0x29e2c0)
        second=project(**(c|{'original_first_team_407770_eax_nonzero':False}))
        self.assertEqual((second.original_first_score_context_d4c,
                          second.original_second_score_context_d50),(0,3))

    def test_native_four_special_condition_overrides_in_actual_reached_order(self):
        src=inputs()
        gates=list(no_gates())
        gates[0]=Gate(0x516040,True,True,None,None)
        x=project(**(src|{'original_four_special_gates':tuple(gates)}))
        self.assertEqual((x.original_first_score_context_d4c,x.original_second_score_context_d50),(1,0))
        self.assertEqual(x.original_override_path_sites,(0x512ded,))
        gates[1]=Gate(0x516050,True,True,None,None)
        x=project(**(src|{'original_four_special_gates':tuple(gates)}))
        self.assertEqual((x.original_first_score_context_d4c,x.original_second_score_context_d50),(0,1))
        self.assertEqual(x.original_override_path_sites,(0x512ded,0x512e2a))
        gates[2]=Gate(0x516060,True,None,None,0x5000)
        x=project(**(src|{'original_four_special_gates':tuple(gates)}))
        self.assertEqual((x.original_first_score_context_d4c,x.original_second_score_context_d50),(0,1))
        gates[3]=Gate(0x516070,True,None,None,0x5000)
        x=project(**(src|{'original_four_special_gates':tuple(gates)}))
        self.assertEqual((x.original_first_score_context_d4c,x.original_second_score_context_d50),(1,0))
        self.assertEqual(x.original_override_path_sites[-1],0x512f03)

    def test_nonfirst_human_team_reached_only_after_false_first_human_gate(self):
        g=list(no_gates())
        g[0]=Gate(0x516040,True,False,True,None)
        r=project(**(inputs()|{'original_four_special_gates':tuple(g)}))
        self.assertEqual((r.original_first_score_context_d4c,r.original_second_score_context_d50),(0,1))
        g[1]=Gate(0x516050,True,False,True,None)
        r=project(**(inputs()|{'original_four_special_gates':tuple(g)}))
        self.assertEqual((r.original_first_score_context_d4c,r.original_second_score_context_d50),(1,0))

    def test_source_field_and_sibling_unreached_flags_fail_closed(self):
        x=inputs()
        invalid=(
            {'original_v34_at_5130c2_returned_false':True},
            {'original_v34_at_5130c2_returned_false':0},
            {'original_context_pointer':0},
            {'original_context_record_before_512d80':bytes(0xd54)},
            {'original_context_record_before_512d80':bytes(4)},
            {'original_context_record_before_512d80':bytearray(0xd54)},
            {'original_tls_record_source':None},
            {'original_first_team_407770_eax_nonzero':1},
            {'original_four_special_gates':no_gates()[:-1]},
            {'original_four_special_gates':list(no_gates())},
            {'original_four_special_gates':(Gate(0x516050,False,None,None,None),)+no_gates()[1:]},
            {'original_four_special_gates':(Gate(0x516040,False,True,None,None),)+no_gates()[1:]},
            {'original_four_special_gates':(Gate(0x516040,True,True,False,None),)+no_gates()[1:]},
            {'original_four_special_gates':(Gate(0x516040,True,False,None,None),)+no_gates()[1:]},
            {'original_four_special_gates':no_gates()[:2]+(Gate(0x516060,True,None,None,False),)+no_gates()[3:]},
        )
        for change in invalid:
            with self.subTest(change=change),self.assertRaises(Original512D80SourceError):
                project(**(x|change))

    def test_actual_private_original_pe_proves_random6_source_score_stores_and_overrides(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original canonical PE unavailable')
        b=Path(p).read_bytes()
        self.assertEqual((len(b),sha256(b).hexdigest()),(4714541,
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x512d87:'bb 01 00 00 00',
            0x512d8c:'6a 06',
            0x512d94:'e8 a7 a7 13 00',
            0x512d99:'6a 06',
            0x512d9b:'89 86 4c 0d 00 00',
            0x512da1:'e8 9a a7 13 00',
            0x512dad:'89 86 50 0d 00 00',
            0x512db3:'57',
            0x512db4:'e8 b7 49 ef ff',
            0x512dbd:'89 be 4c 0d 00 00',
            0x512dca:'e8 a1 49 ef ff',
            0x512dd3:'89 be 50 0d 00 00',
            0x512dd9:'e8 62 32 00 00',
            0x512ded:'89 9e 4c 0d 00 00',
            0x512df3:'89 be 50 0d 00 00',
            0x512e0a:'89 be 4c 0d 00 00',
            0x512e10:'89 9e 50 0d 00 00',
            0x512e16:'e8 35 32 00 00',
            0x512e2a:'89 be 4c 0d 00 00',
            0x512e30:'89 9e 50 0d 00 00',
            0x512e53:'e8 08 32 00 00',
            0x512e77:'89 9e 4c 0d 00 00',
            0x512e7d:'89 be 50 0d 00 00',
            0x512ea4:'89 be 4c 0d 00 00',
            0x512eaa:'89 9e 50 0d 00 00',
            0x512eb0:'e8 bb 31 00 00',
            0x512ed4:'89 be 4c 0d 00 00',
            0x512eda:'89 9e 50 0d 00 00',
            0x512f03:'89 9e 4c 0d 00 00',
            0x512f09:'89 be 50 0d 00 00',
        }
        for va,h in sites.items():
            with self.subTest(va=hex(va)):
                sig=bytes.fromhex(h)
                self.assertEqual(b[va-0x400000:va-0x400000+len(sig)],sig)
