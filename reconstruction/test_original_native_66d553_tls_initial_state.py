"""Original CRT newly allocated TLS initial seed and existing-thread bypass."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase

from original_native_66d553_tls_initial_state import (
    OriginalCRTThreadInitSourceError,
    source_original_66d553_reached_crt_tls_record as source,
)
from original_match_64d540_tls_score_rng import (
    source_original_64d540_bounded_tls_match_rng,
)


def fresh():
    return dict(
        original_tls_slot_dword_84ad40=9,
        original_tlsgvalue_return_pointer=0,
        original_existing_tls_record_if_reached=None,
        original_calloc_return_pointer_if_fresh=0x7000,
        original_calloc_zero_record_if_fresh=bytes(0x74),
        original_tlssetvalue_return_eax_if_fresh=1,
        original_thread_id_callback_return_eax_if_fresh=142,
    )


def existing(seed=0xDEADBEEF):
    b=bytearray(0x74)
    pack_into('<I',b,0x14,seed)
    return dict(
        original_tls_slot_dword_84ad40=9,
        original_tlsgvalue_return_pointer=0x7010,
        original_existing_tls_record_if_reached=bytes(b),
        original_calloc_return_pointer_if_fresh=None,
        original_calloc_zero_record_if_fresh=None,
        original_tlssetvalue_return_eax_if_fresh=None,
        original_thread_id_callback_return_eax_if_fresh=None,
    )


class OriginalCRT66D553NativeSourceTests(TestCase):
    def test_reached_first_calloc_state_initializes_seed1_tid_and_caller_v50(self):
        r=source(**fresh())
        self.assertTrue(r.source_original_new_tls_initialized)
        self.assertEqual(r.original_tlsgvalue_pointer_before_init,0)
        self.assertEqual(r.original_source_initializer_va,0x66d540)
        self.assertEqual(r.original_tls_record_pointer,0x7000)
        self.assertEqual(r.original_seed_at_plus14,1)
        b=r.source_record_before_first_reached_66951c
        self.assertEqual(len(b),0x74)
        for off,expected in ((0,142),(4,0xffffffff),(0x14,1),(0x50,0x84d430)):
            self.assertEqual(unpack_from('<I',b,off)[0],expected)
        other=bytearray(b)
        for off in (0,4,0x14,0x50):other[off:off+4]=bytes(4)
        self.assertEqual(other,bytes(0x74))
        self.assertFalse(r.original_actual_system_tls_access_executed)
        self.assertFalse(r.original_66951c_rand_executed)
        self.assertFalse(r.original_game_state_mutated)

    def test_original_existing_tls_state_must_not_reset_any_reached_seed(self):
        for value in (0,1,0xFFFFFFFF,0xDEADBEEF):
            r=source(**existing(value))
            self.assertFalse(r.source_original_new_tls_initialized)
            self.assertEqual(r.original_seed_at_plus14,value)
            self.assertIsNone(r.original_source_initializer_va)
            self.assertEqual(r.source_record_before_first_reached_66951c,
                             existing(value)['original_existing_tls_record_if_reached'])

    def test_source_new_thread1_can_feed_exact_66951c_without_claiming_callbacks(self):
        r=source(**fresh())
        p=source_original_64d540_bounded_tls_match_rng(
            original_reached_score_call_site=0x5dabed,
            original_66d553_tls_record_pointer=r.original_tls_record_pointer,
            original_66d553_tls_record_before_66951c=r.source_record_before_first_reached_66951c,
            original_64d540_reached_positive_bound=32768)
        self.assertEqual((p.original_seed_before,p.original_seed_after,
                          p.original_66951c_rand15,p.original_64d540_return_eax),
                         (1,0x29e2c0,41,41))
        self.assertFalse(p.original_rng_state_committed)
        other=source(**existing(0))
        q=source_original_64d540_bounded_tls_match_rng(
            original_reached_score_call_site=0x5dae68,
            original_66d553_tls_record_pointer=other.original_tls_record_pointer,
            original_66d553_tls_record_before_66951c=other.source_record_before_first_reached_66951c,
            original_64d540_reached_positive_bound=32768)
        self.assertEqual((q.original_seed_before,q.original_66951c_rand15),(0,38))

    def test_wrong_tls_branch_owner_or_unsourced_allocation_cannot_claim_seed1(self):
        good=fresh()
        wrong=(
          {'original_tls_slot_dword_84ad40':0xffffffff},
          {'original_tls_slot_dword_84ad40':True},
          {'original_calloc_return_pointer_if_fresh':0},
          {'original_calloc_zero_record_if_fresh':bytes(0x73)},
          {'original_calloc_zero_record_if_fresh':bytes([1])+bytes(0x73)},
          {'original_tlssetvalue_return_eax_if_fresh':0},
          {'original_tlssetvalue_return_eax_if_fresh':None},
          {'original_tlssetvalue_return_eax_if_fresh':True},
          {'original_thread_id_callback_return_eax_if_fresh':None},
          {'original_existing_tls_record_if_reached':bytes(0x74)},
        )
        for changed in wrong:
            with self.subTest(change=changed),self.assertRaises(OriginalCRTThreadInitSourceError):
                source(**(good|changed))
        old=existing()
        for changed in (
          {'original_calloc_return_pointer_if_fresh':0x1000},
          {'original_existing_tls_record_if_reached':bytes(0x17)},
          {'original_existing_tls_record_if_reached':None},
          {'original_thread_id_callback_return_eax_if_fresh':142},
        ):
            with self.subTest(change=changed),self.assertRaises(OriginalCRTThreadInitSourceError):
                source(**(old|changed))

    def test_private_original_66d540_initial_seed1_and_66d553_tls_reuse_source(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private canonical original PE not present')
        b=Path(p).read_bytes()
        self.assertEqual((len(b),sha256(b).hexdigest()),(4714541,
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x66d540:'8b 44 24 04',
            0x66d544:'c7 40 50 30 d4 84 00',
            0x66d54b:'c7 40 14 01 00 00 00',
            0x66d563:'ff 15 c8 d1 7b 00',
            0x66d56b:'85 f6',
            0x66d56d:'75 3f',
            0x66d56f:'6a 74 6a 01',
            0x66d580:'56',
            0x66d591:'56 e8 a9 ff ff ff',
            0x66d598:'ff 15 bc d1 7b 00',
            0x66d59e:'83 4e 04 ff',
            0x66d5a2:'89 06',
            0x66d5ae:'57',
            0x66d5b5:'8b c6',
        }
        for va,h in sites.items():
            with self.subTest(va=hex(va)):
                sig=bytes.fromhex(h)
                self.assertEqual(b[va-0x400000:va-0x400000+len(sig)],sig)
        self.assertEqual(0x66d592+5+
            unpack_from('<i',b,0x66d592-0x400000+1)[0],0x66d540)
