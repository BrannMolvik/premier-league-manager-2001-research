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
                         ((800,87),(800,38),(800,18),(800,14),(0,10)))
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
        from original_presults_child_inventory import ORIGINAL_LOADING_BACK_RECT,ORIGINAL_LOADING_FILL_INITIAL_RECT
        self.assertEqual(ORIGINAL_LOADING_BACK_RECT,(0,579,800,14))
        self.assertEqual(ORIGINAL_LOADING_FILL_INITIAL_RECT,(0,581,0,10))
        for changed in (b[:-1],b[:-1]+bytes((b[-1]^1,))):
            with self.assertRaises(OriginalPResultsSourceError):
                source_original_presults_initial_children(waiting_back_2_raw=changed)
        with self.assertRaises(OriginalPResultsSourceError):
            source_original_presults_initial_children(waiting_back_2_raw=bytearray(b))

    def test_original_back_and_fill_source_bytes_and_reject_tampering(self):
        from original_presults_child_inventory import source_original_presults_initial_children
        p=environ.get('FM2001_ORIGINAL_WAITING_FOLDER')
        if not p:self.skipTest('private original loading back/fill not provided')
        root=Path(p)
        b=(root/'loading_back.444.bin').read_bytes()
        f=(root/'loading_fill.444.bin').read_bytes()
        v=source_original_presults_initial_children(loading_back_raw=b,loading_fill_raw=f)
        self.assertTrue(v.original_loading_back_validated)
        self.assertTrue(v.original_loading_fill_validated)
        for name,raw in (('loading_back_raw',b),('loading_fill_raw',f)):
            for corrupt in (raw[:-1],raw[:-1]+bytes([raw[-1]^1]),bytearray(raw)):
                with self.subTest(name=name,len=len(corrupt)),self.assertRaises(OriginalPResultsSourceError):
                    source_original_presults_initial_children(**{name:corrupt})

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
          0x4a6f31:'a1 08 66 94 00 8b 0d 04 66 94 00',
          0x4a6f44:'68 43 02 00 00',
          0x4a6f58:'68 00 01 00 00 55 6a 01 6a 0a 55',
          0x4a6f63:'8d 9e 50 02 00 00',
          0x4a6f69:'55 68 20 03 00 00 68 d0 65 94 00',
          0x4a6f7e:'8d be 70 02 00 00',
          0x4a6f90:'8b 43 18 8b 4b 14 55 68 10 bf 87 00 50 51',
          0x4a6f9e:'68 45 02 00 00',
          0x4a6fa6:'89 5f 2c',
          0x5f4420:'68 00 01 00 00 6a 00 6a 01 6a 0e 68 20 03 00 00',
          0x5f4439:'b9 f0 65 94 00',
          0x5f4448:'e8 b3 a0 05 00',
          0x5f4464:'68 ac 59 83 00',
          0x64e58f:'89 5e 14 89 6e 18',
        }
        for va,s in sites.items():
            with self.subTest(va=hex(va)):
                sig=bytes.fromhex(s)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(sig)],sig)


class OriginalPResultsRealEventProgressTests(TestCase):
    def test_native_two_pass_callbacks_drive_source_bar_position_and_width(self):
        from original_presults_child_inventory import source_original_presults_bar_rects_from_dated_callbacks
        from original_presults_native_event_work import (OriginalPResultsDatedEventReceipt,
                                                          OriginalPResultsSourceCallback)
        callbacks=(OriginalPResultsSourceCallback(0x8000,1,0x10,0x4a71f0),
                   OriginalPResultsSourceCallback(0x8100,2,0x10,0x4a71f0))
        r=OriginalPResultsDatedEventReceipt(callbacks,True)
        steps=source_original_presults_bar_rects_from_dated_callbacks(
            original_6168c0_receipt=r,original_source_total_4a7210=4,
            original_processed_before_callbacks=1)
        self.assertEqual(tuple(s.original_bar_rect_xywh for s in steps),
                         ((0,581,400,10),(0,581,600,10)))
        self.assertEqual(tuple(s.original_processed_count_after_tick for s in steps),(2,3))
        self.assertEqual(tuple(s.original_callback_pass for s in steps),(1,2))
        self.assertTrue(all(not s.actual_original_event_executed and
                            not s.original_screen_rendered for s in steps))

    def test_progress_requires_original_events_not_synthetic_timers_or_scores(self):
        from original_presults_child_inventory import source_original_presults_bar_rects_from_dated_callbacks
        from original_presults_native_event_work import (OriginalPResultsDatedEventReceipt,
                                                          OriginalPResultsSourceCallback)
        good=OriginalPResultsDatedEventReceipt((OriginalPResultsSourceCallback(
            0x8000,2,0x10,0x4a71f0),),True)
        kwargs=dict(original_6168c0_receipt=good,original_source_total_4a7210=4,
                    original_processed_before_callbacks=0)
        bad=[kwargs|{'original_6168c0_receipt':None},
             kwargs|{'original_6168c0_receipt':(0x8000,)},
             kwargs|{'original_source_total_4a7210':0},
             kwargs|{'original_source_total_4a7210':False},
             kwargs|{'original_processed_before_callbacks':4},
             kwargs|{'original_processed_before_callbacks':-1},
             kwargs|{'original_6168c0_receipt':OriginalPResultsDatedEventReceipt((
                 OriginalPResultsSourceCallback(0x8000,1,0x08,0x4a71f0),),False)},
             kwargs|{'original_6168c0_receipt':OriginalPResultsDatedEventReceipt((
                 OriginalPResultsSourceCallback(0x8000,1,0x10,0x4a7190),),False)},
             kwargs|{'original_6168c0_receipt':OriginalPResultsDatedEventReceipt((
                 OriginalPResultsSourceCallback(0,1,0x10,0x4a71f0),),False)}]
        for case in bad:
            with self.subTest(case=str(case)[:125]), self.assertRaises(OriginalPResultsSourceError):
                source_original_presults_bar_rects_from_dated_callbacks(**case)
        empty=OriginalPResultsDatedEventReceipt((),False)
        self.assertEqual(source_original_presults_bar_rects_from_dated_callbacks(
            original_6168c0_receipt=empty,original_source_total_4a7210=0,
            original_processed_before_callbacks=0),())
