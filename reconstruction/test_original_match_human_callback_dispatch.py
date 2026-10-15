"""Source-original human match callback route and native 5DC510 event layout."""
from hashlib import sha256
from os import environ
from pathlib import Path
from unittest import TestCase
from original_match_human_callback_dispatch import (
    OriginalHumanCallbackDispatchError,source_original_5db37c_human_callback_dispatch as dispatch,
)
from original_match_5dc510_event_payload import (
    Original5DC510EventPayloadError,source_original_5dc510_event_payload_layout,
)


class OriginalHumanCallbackDispatchTests(TestCase):
    def test_flag_zero_nohuman_and_direct_human_bonus(self):
        self.assertEqual(dispatch(original_first_4037b0_at_5db3b2=False,original_flag_at_5db3b9=0).original_callback_callsites,())
        r=dispatch(original_first_4037b0_at_5db3b2=True,original_flag_at_5db3b9=0)
        self.assertEqual(r.original_callback_callsites,(0x5DB456,0x5DB4B9))
        self.assertTrue(r.original_694_dword0_ebx_bonus_reached)
        self.assertFalse(r.original_native_callbacks_executed)

    def test_alternate_may_call_first_then_second_and_never_add_bonus(self):
        first=dict(original_first_4037b0_at_5db3b2=True,original_flag_at_5db3b9=1,
                   original_first_4037b0_at_5db4d7=True,original_first_4037b0_at_5db4f3=True)
        a=dispatch(**first,original_second_4037b0_at_5db5f5=True)
        self.assertEqual(a.original_callback_callsites,(0x5DB58D,0x5DB5F0,0x5DB692,0x5DB6F5))
        self.assertFalse(a.original_694_dword0_ebx_bonus_reached)
        b=dispatch(**(first|{'original_first_4037b0_at_5db4f3':False}),original_second_4037b0_at_5db5f5=False)
        self.assertEqual(b.original_callback_callsites,())

    def test_alternate_second_only_or_nohuman_early(self):
        x=dict(original_first_4037b0_at_5db3b2=False,original_flag_at_5db3b9=255,
               original_first_4037b0_at_5db4d7=False,original_second_4037b0_at_5db4e2=True,
               original_first_4037b0_at_5db4f3=False,original_second_4037b0_at_5db5f5=True)
        self.assertEqual(dispatch(**x).original_callback_callsites,(0x5DB692,0x5DB6F5))
        early=dispatch(**{k:v for k,v in x.items() if k not in ('original_first_4037b0_at_5db4f3','original_second_4037b0_at_5db5f5')}|{'original_second_4037b0_at_5db4e2':False})
        self.assertEqual(early.original_callback_callsites,())

    def test_reject_unreached_guessed_owner_and_recheck_inputs(self):
        common=dict(original_first_4037b0_at_5db3b2=False,original_flag_at_5db3b9=0)
        invalid=[common|{'original_second_4037b0_at_5db5f5':True},
                 common|{'original_flag_at_5db3b9':False},
                 common|{'original_first_4037b0_at_5db3b2':1},
                 common|{'original_flag_at_5db3b9':256},
                 common|{'original_flag_at_5db3b9':1},
                 common|{'original_flag_at_5db3b9':1,'original_first_4037b0_at_5db4d7':False},
                 common|{'original_flag_at_5db3b9':1,'original_first_4037b0_at_5db4d7':True,
                         'original_second_4037b0_at_5db4e2':True}]
        for v in invalid:
            with self.subTest(v=v),self.assertRaises(OriginalHumanCallbackDispatchError):dispatch(**v)

    def test_native_original_branch_sites_and_four_callback_targets(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE unavailable')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        expected={
          0x5DB3BD:'0f 84 0c 01 00 00',0x5DB3C3:'84 c0 0f 85 0c 01 00 00',
          0x5DB4CF:'84 c0 0f 84 23 02 00 00',
          0x5DB4D7:'8b ce e8 d2 82 e2 ff 84 c0 75 11',
          0x5DB4E2:'8b 4c 24 44 e8 c5 82 e2 ff 84 c0 0f 84 07 02 00 00',
          0x5DB4F3:'8b ce e8 b6 82 e2 ff 84 c0',
          0x5DB5F5:'8b 4c 24 44 e8 b2 81 e2 ff 84 c0',
          0x5DB456:'e8 b5 10 00 00',0x5DB4B9:'e8 52 10 00 00',
          0x5DB58D:'e8 7e 0f 00 00',0x5DB5F0:'e8 1b 0f 00 00',
          0x5DB692:'e8 79 0e 00 00',0x5DB6F5:'e8 16 0e 00 00',
        }
        for va,h in expected.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(raw[va-0x400000:va-0x400000+len(bytes.fromhex(h))],bytes.fromhex(h))


class Original5DC510EventLayoutTests(TestCase):
    def test_record_copies_exact_native_fields_but_padding_unknown(self):
        args=bytes(range(0x24))
        r=source_original_5dc510_event_payload_layout(original_5dc510_byvalue_arguments=args)
        self.assertEqual(r.original_payload_first16,args[:16])
        self.assertEqual(r.original_payload_word10,0x1110)
        self.assertEqual(r.original_payload_tail14_1c,(0x17161514,0x1b1a1918,0x1f1e1d1c))
        self.assertTrue(r.original_uninitialized_padding_12_13)
        self.assertEqual((r.original_payload_allocated_bytes,r.original_wrapper_allocated_bytes),(32,12))
        self.assertFalse(r.live_queue_updated)

    def test_reject_missing_native_arguments(self):
        for v in (b'',bytes(35),bytearray(36),None):
            with self.subTest(v=v),self.assertRaises(Original5DC510EventPayloadError):
                source_original_5dc510_event_payload_layout(original_5dc510_byvalue_arguments=v)

    def test_original_pe_record_constructor_allocations_and_linker(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE unavailable')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        signatures={
           0x5DC5D4:'e8 77 00 00 00',0x5DC5D9:'6a 20 e8 60 bb 08 00',
           0x5DC5E7:'8b 5d 14 8b 4d 08 8b 55 0c 8b 7d 10',
           0x5DC5F9:'89 0b 8b 4c 24 2c 89 53 04',
           0x5DC602:'66 8b 55 18 66 89 50 10',
           0x5DC615:'8d 48 14 89 50 14 8b 55 20',
           0x5DC621:'8b 55 24 89 51 08',
           0x5DC629:'33 ff 6a 0c e8 0e bb 08 00',
           0x5DC632:'8b cc 89 38 89 01 8b ce e8 31 b7 03 00',
           0x5DC645:'c2 24 00',
        }
        for va,h in signatures.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(raw[va-0x400000:va-0x400000+len(bytes.fromhex(h))],bytes.fromhex(h))


    def test_original_5dd1f0_consumes_670_payload_word_and_filters_before_sum(self):
        """Native same owner+4 queue is read back by a conditional score query."""
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE unavailable')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        signatures={
           0x5DD1FB:'8b 71 04',  # original owner+4 head pointer
           0x5DD21D:'8b 0e 66 8b 45 08 66 39 41 10', # node+0 payload, payload+10 word
           0x5DD22D:'6a 00 e8 9c 76 00 00 dc 1d f8 d5 7b 00 df e0 f6 c4 01',
           0x5DD278:'e8 e3 fd 06 00 85 c0 74 47', # 64D060 filter
           0x5DD2AE:'e8 6d fd 06 00 85 c0 74 11', # 64D020 filter
           0x5DD2B7:'8b 0e 6a 00 e8 10 76 00 00 dc 44 24 10 dd 5c 24 10',
           0x5DD2C8:'8b 76 04 85 f6 0f 85 4a ff ff ff',
           0x5DD2D3:'dd 44 24 10 5f 5e 5b 8b e5 5d c2 1c 00',
           0x5DC910:'e8 db 08 00 00', # 5DC890 numeric dispatch calls this score query
        }
        for va,h in signatures.items():
            with self.subTest(native=hex(va)):
                b=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
        from struct import unpack_from
        for site,target in ((0x5DD22F,0x5E48D0),(0x5DD278,0x64D060),
                            (0x5DD2AE,0x64D020),(0x5DD2BB,0x5E48D0),
                            (0x5DC910,0x5DD1F0)):
            off=site-0x400000
            self.assertEqual(raw[off],0xE8)
            self.assertEqual(site+5+unpack_from('<i',raw,off+1)[0],target)
