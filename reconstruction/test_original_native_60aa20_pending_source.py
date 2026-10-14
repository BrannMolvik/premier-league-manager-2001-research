"""Deterministic original 0x60AA20 source projection/counterexample tests."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
from struct import pack_into, unpack_from
import hashlib
import os
import unittest

from original_native_60aa20_pending_source import (
    Original60AA20Reached, Original60AA20PendingIdentity,
    Original60AA20SourceError, source_original_60aa20_project,
)


def reached(status=0, delta=1, base=4, human=False, source77=10, day=100):
    p = bytearray(0x250)
    pack_into('<H', p, 4, 123)
    pack_into('<I', p, 0x14, 0x100)
    p[0x22], p[0x77] = 253, source77
    pack_into('<I', p, 0x24c, 0x50000)
    d = bytearray(12)
    pack_into('<I', d, 0, 0xffffffff)
    d[4], d[5] = 1, status
    pack_into('<I', d, 8, 123)
    return Original60AA20Reached(123, bytes(p), bytes(d), 0x50000,
                                 (123,)*(8 if human else 6),
                                 delta, base, day, 1 if human else 0)


class Original60AA20ProjectionTests(unittest.TestCase):
    def test_nonhuman_short_source_writes_event_and_serializes_identity(self):
        x = source_original_60aa20_project(reached())
        self.assertEqual(x.original_duration_after_mitigation, 1)
        self.assertEqual(x.original_rng5_draw_count, 0)
        self.assertEqual(unpack_from('<I', x.original_player_after_source, 0x14)[0], 0x101)
        self.assertEqual(x.original_player_after_source[0x77], 6)
        self.assertEqual(x.original_player_after_source[0x22], 254)
        self.assertEqual(unpack_from('<I', x.original_descriptor_after_source, 0)[0], 107)
        event = x.original_pending_identity
        self.assertEqual(event.to_portable(), dict(queue=0x947aa8, vtable=0x7d7760,
                         type=1, date_raw_u32=107, player_id_u16=123, status=0))
        self.assertEqual(Original60AA20PendingIdentity.from_portable(event.to_portable()), event)
        self.assertFalse(x.original_native_callback_executed)
        self.assertFalse(x.original_event_allocated)
        self.assertFalse(x.original_queue_inserted)
        self.assertFalse(x.original_mail_delivered)
        self.assertFalse(x.live_game_state_updated)

    def test_medium_long_byte_modulo_clamp_and_date_wrap(self):
        for status, delta, expected22 in ((1, 3, 1), (2, 11, 5), (3, 14, 5)):
            with self.subTest(status=status):
                x = source_original_60aa20_project(reached(status, delta, base=10,
                                                        source77=10, day=0x7fffffff))
                self.assertEqual(x.original_player_after_source[0x77], 1)
                self.assertEqual(x.original_player_after_source[0x22], expected22)
                self.assertEqual(x.original_pending_identity.original_status_byte, status)
                self.assertEqual(x.original_pending_identity.original_date_raw_u32,
                                 (0x7fffffff + 7*delta)&0xffffffff)
                self.assertEqual(x.original_player_after_source[0x23:], reached(status,delta,base=10,source77=10,day=0x7fffffff).player_before[0x23:0x77]+bytes([1])+reached(status,delta,base=10,source77=10,day=0x7fffffff).player_before[0x78:])
        x = source_original_60aa20_project(reached(0, 1, base=4, source77=5, day=0xfffffffe))
        self.assertEqual(x.original_pending_identity.original_date_raw_u32,5)
        x = source_original_60aa20_project(reached(0, 1, base=-2, source77=5))
        self.assertEqual(x.original_player_after_source[0x77], 7)  # signed compare, subtract low byte

    def test_human_rng5_loop_ceil_length_threshold_and_floor(self):
        q = replace(reached(3, 14, human=True),
                    native_4d1190_result_nonnull=True,
                    native_v40_threshold=3, rng5_results=(0, 4, 2, 1))
        x = source_original_60aa20_project(q)
        self.assertEqual((x.original_duration_after_mitigation,x.original_rng5_draw_count),(11,4))
        self.assertEqual(x.original_pending_identity.original_date_raw_u32,177)
        q = replace(reached(0,1,human=True), native_4d1190_result_nonnull=True,
                    native_v40_threshold=5, rng5_results=(0,))
        self.assertEqual(source_original_60aa20_project(q).original_duration_after_mitigation,1)
        q = replace(reached(1,3,human=True), native_4d1190_result_nonnull=False)
        self.assertEqual(source_original_60aa20_project(q).original_rng5_draw_count,0)

    def test_source_callback_owner_and_rng_fail_closed(self):
        good = reached()
        wrong = bytearray(good.player_before)
        pack_into('<H', wrong, 4, 456)
        edits = [
            replace(good,player_before=bytes(wrong)),
            replace(good,resolver_player_ids=(123,)*5),
            replace(good,resolver_player_ids=(123,123,123,456,123,123)),
            replace(good,descriptor_pointer=0),
            replace(good,descriptor_pointer=0x50004),
            replace(good,registered_417340_al=True),
            replace(good,rng5_results=(0,)),
            replace(good,native_v40_threshold=2),
            replace(good,duration_delta_arg=3),
            replace(good,player77_decrement_base_arg=0x80000000),
            replace(good,current_date_9847fc=0x100000000),
            replace(good,descriptor_before=good.descriptor_before[:-1]),
        ]
        for x in edits:
            with self.subTest(reached=x):
                with self.assertRaises(Original60AA20SourceError):
                    source_original_60aa20_project(x)
        human=reached(1,3,human=True)
        for bad in [human,replace(human,native_4d1190_result_nonnull=True,
                       native_v40_threshold=3,rng5_results=()),
                    replace(human,native_4d1190_result_nonnull=True,
                       native_v40_threshold=3,rng5_results=(5,)),
                    replace(human,native_4d1190_result_nonnull=False,rng5_results=(0,))]:
            with self.assertRaises(Original60AA20SourceError):
                source_original_60aa20_project(bad)
        event=source_original_60aa20_project(good).original_pending_identity
        for tampered in (dict(event.to_portable(),type=True),
                         dict(event.to_portable(),queue=0x947aa0),
                         dict(event.to_portable(),date_raw_u32=-1),
                         dict(event.to_portable(),status=4),
                         {k:v for k,v in event.to_portable().items() if k!='status'}):
            with self.assertRaises(Original60AA20SourceError):
                Original60AA20PendingIdentity.from_portable(tampered)

    def test_exact_original_pe_opcodes_if_private_source_available(self):
        path=os.environ.get('FM2001_ORIGINAL_EXE')
        if not path:
            self.skipTest('original PE private; source opcode check outside CI')
        data=Path(path).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3')
        signatures={
            0x60aa20:'51 53 8b d9',
            0x60aa3c:'e8 ff c8 e0 ff',
            0x60aa9d:'6a 05 e8 9c 2a 04 00',
            0x60aad8:'56 e8 82 fd e0 ff',
            0x60aae0:'fc 47 98 00',
            0x60ab0f:'83 c0 77 2a cb 88 08',
            0x60ab25:'33 c0 8a 43 05',
            0x60ab77:'6a 14 e8 c2 d5 05 00',
            0x60ab9b:'c7 00 60 77 7d 00',
            0x60aba9:'c7 46 08 01 00 00 00',
            0x60abd5:'b9 a8 7a 94 00',
            0x60abdd:'e8 de 92 00 00',
        }
        for va,hexes in signatures.items():
            with self.subTest(va=hex(va)):
                raw=bytes.fromhex(hexes)
                self.assertEqual(data[va-0x400000:va-0x400000+len(raw)],raw)

if __name__ == '__main__':
    unittest.main()
