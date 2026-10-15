"""Source original 451021 4139D0 ordinal versus first human 5DB450 key owner."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase

from original_native_417340_registered_user_gate import Original417340ReachedUser
from original_match_451021_indexed_owner import (
    Original451021IndexedOwnerError,source_original_451021_reader_5db450_writer_snapshot,
)


def source_case(keys=(42,99), bases=(0x9010,0x9020),
                extras=(0x9100,0x9200), club_ordinal=0,
                writer_key=42, slot=0):
    links=[]
    for i,key in enumerate(keys):
        ptr=0x1000+i*0x30
        userptr=0x2000+i*0x900
        ctxptr=0x6000+i*0x30
        raw=bytearray(8)
        pack_into('<II',raw,0,userptr,0x1000+(i+1)*0x30 if i+1<len(keys) else 0)
        user=bytearray(0x678)
        pack_into('<I',user,0x5b4,ctxptr)
        pack_into('<II',user,0x670,bases[i],extras[i])
        ctx=bytearray(8)
        pack_into('<I',ctx,4,key)
        links.append(Original417340ReachedUser(
            ptr,bytes(raw),userptr,bytes(user),ctxptr,bytes(ctx)))
    root=bytearray(0x9d0)
    pack_into('<I',root,0x9cc,0x1000 if keys else 0)
    reader_club=bytearray(8)
    pack_into('<H',reader_club,4,club_ordinal)
    writer_club=bytearray(8)
    pack_into('<I',writer_club,4,writer_key)
    presenter=bytearray(0xe4)
    pack_into('<I',presenter,0xe0,slot)
    selected=next((x.original_user_pointer for x in links if
                  unpack_from('<I',x.original_user_context_record,4)[0]==(writer_key&0xffff)),0)
    return dict(original_874c10_global_at_comparison=bytes(root),
      original_complete_registered_manager_links=tuple(links),
      original_451005_club_d8_record=bytes(reader_club),
      original_451014_presenter_record=bytes(presenter),
      original_5db3ac_first_side_club_record=bytes(writer_club),
      original_reader_reached_4139d0_user_pointer=links[club_ordinal].original_user_pointer
        if club_ordinal<len(links) else 0,
      original_writer_reached_403850_user_pointer=selected)


class Original451021IndexedOwnerTests(TestCase):
    def test_zero_index_same_user_base_slot_is_only_snapshot_candidate(self):
        s=source_original_451021_reader_5db450_writer_snapshot(**source_case())
        self.assertEqual((s.original_reader_manager_ordinal_from_d8_word,
                          s.original_reader_plus_e0_queue_slot_index),(0,0))
        self.assertEqual((s.original_reader_user_pointer,s.original_writer_user_pointer),
                         (0x2000,0x2000))
        self.assertTrue(s.native_snapshot_user_pointers_equal)
        self.assertTrue(s.native_snapshot_queue_pointers_equal)
        self.assertFalse(s.native_intervening_mutations_excluded)
        self.assertFalse(s.live_original_match_owner_join_proven)
        self.assertFalse(s.game_state_updated)

    def test_same_user_different_indexed_queue_is_not_same_queue(self):
        s=source_original_451021_reader_5db450_writer_snapshot(**source_case(slot=1))
        self.assertTrue(s.native_snapshot_user_pointers_equal)
        self.assertFalse(s.native_snapshot_queue_pointers_equal)
        self.assertEqual((s.original_reader_queue_pointer,s.original_writer_base_queue_pointer),
                         (0x9100,0x9010))

    def test_ordinal_is_not_writer_club_key_lookup(self):
        s=source_original_451021_reader_5db450_writer_snapshot(**source_case(writer_key=99))
        self.assertEqual((s.original_reader_user_pointer,s.original_writer_user_pointer),
                         (0x2000,0x2900))
        self.assertFalse(s.native_snapshot_user_pointers_equal)
        self.assertFalse(s.native_snapshot_queue_pointers_equal)
        s=source_original_451021_reader_5db450_writer_snapshot(
            **source_case(writer_key=42,club_ordinal=1))
        self.assertEqual(s.original_reader_user_pointer,0x2900)
        self.assertFalse(s.native_snapshot_user_pointers_equal)

    def test_original_full_key_gate_may_select_earlier_low16_alias(self):
        s=source_original_451021_reader_5db450_writer_snapshot(
            **source_case(keys=(0x42,0x10042),writer_key=0x10042,club_ordinal=1))
        self.assertEqual((s.original_writer_full_club_key,s.original_writer_masked_club_key),
                         (0x10042,0x42))
        self.assertEqual((s.original_writer_user_pointer,s.original_reader_user_pointer),
                         (0x2000,0x2900))
        self.assertFalse(s.native_snapshot_user_pointers_equal)

    def test_distinct_users_can_share_queue_pointer_but_not_user_identity(self):
        s=source_original_451021_reader_5db450_writer_snapshot(**source_case(
            writer_key=99,bases=(0x9000,0x9000)))
        self.assertTrue(s.native_snapshot_queue_pointers_equal)
        self.assertFalse(s.native_snapshot_user_pointers_equal)

    def test_full_native_chain_required_and_reached_owner_cross_checked(self):
        good=source_case()
        bad=[
           good|{'original_reader_reached_4139d0_user_pointer':0x9999},
           good|{'original_writer_reached_403850_user_pointer':0x9999},
           good|{'original_complete_registered_manager_links':good['original_complete_registered_manager_links'][:1]},
           good|{'original_874c10_global_at_comparison':bytes(0x9d0)},
           good|{'original_451014_presenter_record':bytes(0xe0)},
           good|{'original_451005_club_d8_record':bytes(6)},
           good|{'original_reader_reached_4139d0_user_pointer':False},
           source_case(club_ordinal=2),
           source_case(writer_key=7),
           source_case(slot=4),
           source_case(bases=(0,1)),
           source_case(extras=(0,0),slot=1),
        ]
        for r in bad:
            with self.subTest(case=str(r)[:90]),self.assertRaises(Original451021IndexedOwnerError):
                source_original_451021_reader_5db450_writer_snapshot(**r)

    def test_original_pe_ordinal_vs_masked_key_and_indexed_queue_opcodes(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE not available')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(
            4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x4139D0:'8b 81 c4 09 00 00 50 e8 34 01 00 00 c3',
            0x413B10:'8b 81 cc 09 00 00 33 d2',
            0x413B20:'3b d1 74 0d 8b 40 04 42 85 c0 75 f4',
            0x413B31:'8b 00 c2 04 00',
            0x413B4E:'81 e1 ff ff 00 00',
            0x451005:'66 8b 51 04',
            0x451009:'b9 10 4c 87 00',
            0x451014:'8b 8e e0 00 00 00',
            0x45101A:'8b 8c 88 70 06 00 00',
            0x451021:'e8 6a b8 18 00',
            0x5DB450:'8b 8f 70 06 00 00',
        }
        for va,expected in sites.items():
            with self.subTest(va=hex(va)):
                sig=bytes.fromhex(expected)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(sig)],sig)
        for site,target in ((0x4139D7,0x413B10),(0x45100F,0x4139D0),
                            (0x451021,0x5DC890),(0x5DB456,0x5DC510)):
            off=site-0x400000
            self.assertEqual(raw[off],0xe8)
            self.assertEqual(site+5+unpack_from('<i',raw,off+1)[0],target)
