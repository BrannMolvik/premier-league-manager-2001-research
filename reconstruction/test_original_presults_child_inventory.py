"""Original PResults initial child factory/geometry, no guessed click-to-return."""
from hashlib import sha256
from os import environ
from pathlib import Path
from unittest import TestCase

from original_presults_child_inventory import (
    ORIGINAL_WAITING_BACK_2_RECT, OriginalPResultsSourceError,
    source_original_presults_initial_children,
)


class OriginalPResultsChildrenTests(TestCase):
    def test_all_five_native_initial_children_and_exact_original_slots(self):
        r=source_original_presults_initial_children()
        self.assertEqual(r.original_child_array_count,5)
        self.assertEqual(tuple(x.original_child_array_index for x in r.registered_children),tuple(range(5)))
        self.assertEqual(tuple(x.original_object_offset for x in r.registered_children),
                         (0x16c,0x1a0,0x1e0,0x220,0x270))
        self.assertEqual(tuple(x.original_initial_control_id for x in r.registered_children),(0,)*5)
        self.assertEqual(tuple(x.original_initial_xy for x in r.registered_children),
                         ((0,513),(0,518),(0,556),(0,579),(0,581)))
        self.assertEqual(tuple(x.original_initial_wh for x in r.registered_children),
                         ((800,87),(800,38),(800,18),None,None))
        self.assertEqual(tuple(x.original_factory_call for x in r.registered_children),
                         (0x651ba0,0x6503f0,0x6503f0,0x64f380,0x64f380))
        self.assertEqual(r.original_shared_progress_owner_offset,0x250)
        self.assertFalse(r.original_return_input_proven)
        self.assertFalse(r.original_live_game_view_rendered)
        self.assertTrue(all(not c.original_interactive_return_proven for c in r.registered_children))

    def test_real_waiting_graphic_only_with_exact_sha_identity(self):
        path=environ.get('FM2001_ORIGINAL_WAITING_BACK_2')
        if not path:self.skipTest('private authorized original artwork unavailable in hosted CI')
        b=Path(path).read_bytes()
        r=source_original_presults_initial_children(waiting_back_2_raw=b)
        self.assertTrue(r.original_bitmap_validated)
        self.assertEqual(ORIGINAL_WAITING_BACK_2_RECT,(0,513,800,87))
        for changed in (b[:-1],b[:-1]+bytes((b[-1]^1,))):
            with self.assertRaises(OriginalPResultsSourceError):
                source_original_presults_initial_children(waiting_back_2_raw=changed)
        with self.assertRaises(OriginalPResultsSourceError):
            source_original_presults_initial_children(waiting_back_2_raw=bytearray(b))

    def test_original_exe_ctor_child_offset_geometry_and_zero_id_sites(self):
        path=environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('private original PE unavailable in hosted CI')
        raw=Path(path).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
          0x4a6e61:'6a 14',
          0x4a6e6b:'8d be 6c 01 00 00',
          0x4a6e74:'c7 46 38 05 00 00 00',
          0x4a6e8d:'89 38',
          0x4a6e91:'56 55 8b cf ff 50 08',
          0x4a6e98:'55 68 30 66 94 00 68 01 02 00 00 55',
          0x4a6eae:'8d be a0 01 00 00',
          0x4a6ece:'6a 26 68 20 03 00 00 68 06 02 00 00',
          0x4a6ee5:'8d be e0 01 00 00',
          0x4a6f08:'6a 12 68 20 03 00 00 68 2c 02 00 00',
          0x4a6f1f:'8d be 20 02 00 00',
          0x4a6f44:'68 43 02 00 00',
          0x4a6f63:'8d 9e 50 02 00 00',
          0x4a6f69:'55 68 20 03 00 00 68 d0 65 94 00',
          0x4a6f7e:'8d be 70 02 00 00',
          0x4a6f9e:'68 45 02 00 00',
          0x4a6fa6:'89 5f 2c',
        }
        for va,s in sites.items():
            with self.subTest(va=hex(va)):
                sig=bytes.fromhex(s)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(sig)],sig)
