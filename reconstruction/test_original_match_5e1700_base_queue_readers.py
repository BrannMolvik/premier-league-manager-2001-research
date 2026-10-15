"""Original 5E1700 registered current-user dual 0x65 / 0x66 queue readers."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import unpack_from
from unittest import TestCase
from test_original_match_451021_indexed_owner import source_case
from original_match_5e1700_base_queue_readers import (
    Original5E1700SourceError,source_original_5e1700_current_user_base_queue,
)


def source_inputs(index=0,**kwargs):
    p=source_case(current_manager_index=index,**kwargs)
    queue=(0x9010,0x9020)[index] if index<2 else 0
    return dict(original_874c10_global_record=p['original_874c10_global_at_comparison'],
        original_registered_manager_links=p['original_complete_registered_manager_links'],
        original_reached_4139d0_user_pointer_at_5e170a=p['original_reader_reached_4139d0_user_pointer'],
        original_reached_queue_pointer_at_5e1756=queue,
        original_reached_queue_pointer_at_5e17d1=queue)


class Original5E1700BaseQueueSourceTests(TestCase):
    def test_current_first_registered_user_both_numeric_readers_share_base_slot(self):
        r=source_original_5e1700_current_user_base_queue(**source_inputs())
        self.assertEqual((r.original_registered_current_user_ordinal,
                          r.original_registered_current_user_pointer,
                          r.original_user_base_670_queue_pointer),(0,0x2000,0x9010))
        self.assertEqual((r.original_first_5dc890_selector,r.original_second_5dc890_selector),
                         (0x65,0x66))
        self.assertEqual((r.original_first_call,r.original_second_call),
                         (0x5e178c,0x5e1814))
        self.assertTrue(r.source_same_base_queue_pointer_both_reads)
        self.assertFalse(r.original_match_writer_user_identity_proven)
        self.assertFalse(r.game_state_updated)

    def test_second_registered_user_source_global_ordinal_not_club_key(self):
        r=source_original_5e1700_current_user_base_queue(**source_inputs(index=1,writer_key=42))
        self.assertEqual((r.original_registered_current_user_ordinal,
                          r.original_registered_current_user_pointer,
                          r.original_user_base_670_queue_pointer),(1,0x2900,0x9020))
        self.assertFalse(r.original_match_writer_user_identity_proven)

    def test_real_source_pointer_mismatch_chain_gap_and_null_are_rejected(self):
        good=source_inputs()
        bad=[
           good|{'original_reached_4139d0_user_pointer_at_5e170a':0x2900},
           good|{'original_reached_queue_pointer_at_5e1756':0x9020},
           good|{'original_reached_queue_pointer_at_5e17d1':0x9100},
           good|{'original_reached_queue_pointer_at_5e17d1':False},
           good|{'original_registered_manager_links':good['original_registered_manager_links'][:1]},
           good|{'original_874c10_global_record':bytes(0x9d0)},
           source_inputs(index=2),
           source_inputs(bases=(0,0x9020)),
        ]
        for p in bad:
            with self.subTest(bad=str(p)[:100]),self.assertRaises(Original5E1700SourceError):
                source_original_5e1700_current_user_base_queue(**p)

    def test_canonical_pe_proves_two_base_slot_loads_through_temporary_stack(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('canonical private original PE unavailable')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
            4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x5E1700:'b9 10 4c 87 00',
            0x5E1705:'e8 c6 22 e3 ff',
            0x5E170A:'8b e8',
            0x5E1756:'8b 95 70 06 00 00',
            0x5E175F:'89 54 24 1c',
            0x5E1765:'83 ec 0c',
            0x5E177A:'6a 65',
            0x5E177E:'8b 4c 24 2c',
            0x5E178C:'e8 ff b0 ff ff',
            0x5E17D1:'8b 8d 70 06 00 00',
            0x5E17D7:'89 4c 24 1c',
            0x5E17E7:'83 ec 0c',
            0x5E1804:'6a 66',
            0x5E1810:'8b 4c 24 2c',
            0x5E1814:'e8 77 b0 ff ff',
        }
        for va,h in sites.items():
            with self.subTest(site=hex(va)):
                sig=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(sig)],sig)
        for site,target in ((0x5E1705,0x4139D0),(0x5E178C,0x5DC890),
                            (0x5E1814,0x5DC890)):
            pos=site-0x400000
            self.assertEqual(raw[pos],0xe8)
            self.assertEqual(site+5+unpack_from('<i',raw,pos+1)[0],target)
