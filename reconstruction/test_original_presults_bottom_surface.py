"""PResults native bottom three .444 sprites and event-only progress clipping."""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from ea444_decoder import EA444DecodedImage
from original_presults_child_inventory import OriginalPResultsSourceError
from original_presults_bottom_surface import (
    OriginalPResultsBottomArt,
    source_original_presults_bottom_surface,
    load_verified_original_presults_bottom_art,
)
from original_presults_native_event_work import (
    OriginalPResultsDatedEventReceipt, OriginalPResultsSourceCallback,
)


def _image(width, height, mark):
    return EA444DecodedImage(width,height,bytes((mark, mark, mark, 255)) * (width*height),
                             consumed_bits=0,transparent_pixels=0)


def _original_art():
    return OriginalPResultsBottomArt(
        _image(800,87,11), _image(800,14,22), _image(800,10,33))


class OriginalPResultsBottomSurfaceTests(TestCase):
    def test_original_bottom_static_layers_are_correct_even_with_no_events(self):
        v=source_original_presults_bottom_surface(_original_art())
        self.assertEqual(tuple(layer.source_role for layer in v.source_layers),
                         ('waiting_back_2','loading_back'))
        self.assertEqual(tuple(layer.native_rect for layer in v.source_layers),
                         ((0,513,800,87),(0,579,800,14)))
        self.assertFalse(v.original_native_progress_eligible)
        self.assertFalse(v.full_original_presults_screen)
        self.assertFalse(v.original_return_control_proven)
        self.assertFalse(v.normal_gameplay_result_committed)

    def test_original_event_reachability_controls_fill_width_and_pixels(self):
        callbacks=OriginalPResultsDatedEventReceipt((
            OriginalPResultsSourceCallback(0x8000,1,0x10,0x4a71f0),
            OriginalPResultsSourceCallback(0x8100,2,0x10,0x4a71f0)),True)
        v=source_original_presults_bottom_surface(
            _original_art(), original_dated_event_receipt=callbacks,
            original_source_event_total=4,original_processed_before_callbacks=0)
        self.assertEqual(tuple(layer.source_role for layer in v.source_layers),
                         ('waiting_back_2','loading_back','loading_fill'))
        fill=v.source_layers[-1]
        self.assertEqual(fill.native_rect,(0,581,400,10))
        self.assertEqual(len(fill.rgba),400*10*4)
        self.assertEqual(fill.rgba,bytes((33,33,33,255))*4000)
        self.assertTrue(v.original_native_progress_eligible)
        self.assertFalse(v.normal_gameplay_result_committed)

    def test_full_width_and_empty_original_receipt_are_not_fake_animation(self):
        art=_original_art()
        empty=OriginalPResultsDatedEventReceipt((),False)
        v=source_original_presults_bottom_surface(art,
            original_dated_event_receipt=empty,
            original_source_event_total=0,original_processed_before_callbacks=0)
        self.assertEqual(len(v.source_layers),2)
        full=OriginalPResultsDatedEventReceipt((
            OriginalPResultsSourceCallback(0x8000,1,0x10,0x4a71f0),),True)
        p=source_original_presults_bottom_surface(art,
            original_dated_event_receipt=full,
            original_source_event_total=1,original_processed_before_callbacks=0)
        self.assertEqual(p.source_layers[-1].native_rect,(0,581,800,10))
        self.assertEqual(p.source_layers[-1].rgba,art.original_progress_fill.rgba)

    def test_false_or_unqualified_original_timing_cannot_produce_fill(self):
        for opts in (
           {'original_source_event_total':1},
           {'original_processed_before_callbacks':0},
           {'original_dated_event_receipt':(0x8000,),
            'original_source_event_total':1,
            'original_processed_before_callbacks':0},
           {'original_dated_event_receipt':OriginalPResultsDatedEventReceipt((
                OriginalPResultsSourceCallback(0x8000,1,0x10,0x4a71f0),),True),
            'original_source_event_total':False,
            'original_processed_before_callbacks':0},
           {'original_dated_event_receipt':OriginalPResultsDatedEventReceipt((
                OriginalPResultsSourceCallback(0x8000,1,0x10,0x4a71f0),),True),
            'original_source_event_total':0,
            'original_processed_before_callbacks':0},
        ):
            with self.subTest(opts=str(opts)), self.assertRaises(OriginalPResultsSourceError):
                source_original_presults_bottom_surface(_original_art(),**opts)

    def test_wrong_render_art_and_no_fake_native_return(self):
        with self.assertRaises(OriginalPResultsSourceError):
            OriginalPResultsBottomArt(_image(799,87,1), _image(800,14,2),_image(800,10,3))
        with self.assertRaises(OriginalPResultsSourceError):
            source_original_presults_bottom_surface(SimpleNamespace())
        self.assertFalse(source_original_presults_bottom_surface(_original_art()).original_return_control_proven)

    def test_exact_imported_source_assets_validate_hashes_and_geometry(self):
        source=Path(__file__).resolve().parent.parent/'original_assets'/'source'
        from original_presults_child_inventory import (
            ORIGINAL_WAITING_BACK_2_SOURCE,ORIGINAL_LOADING_BACK_SOURCE,
            ORIGINAL_LOADING_FILL_SOURCE,
        )
        expected=(('waiting_back_2',ORIGINAL_WAITING_BACK_2_SOURCE,46448,
             '289b692919b3048bbe932eaf83083c622089fe4367d8124cd26a8bbf566899e5',(800,87)),
            ('loading_back',ORIGINAL_LOADING_BACK_SOURCE,25944,
             '397e6a91e041575a897605274c6cc6d0711d462ef15bedfe7d9d383f370e37d2',(800,14)),
            ('loading_fill',ORIGINAL_LOADING_FILL_SOURCE,17204,
             '9ba312d886fbb1898ad1f63b5e3c985972c22da09b7915b13d06a374e8c32070',(800,10)))
        for name,rel,size,digest,wh in expected:
            with self.subTest(name=name):
                b=(source/rel).read_bytes()
                self.assertEqual((len(b),sha256(b).hexdigest()),(size,digest))
                self.assertEqual((int.from_bytes(b[0:2],'little'),
                                  int.from_bytes(b[2:4],'little')),wh)

    def test_source_loader_decodes_three_real_assets_from_pinned_original_executable(self):
        # The Windows distribution supplies the canonical PE tables at runtime,
        # whereas the public source checkout does not contain the private EXE.
        from os import environ
        orig=environ.get('FM2001_ORIGINAL_EXE')
        if not orig:self.skipTest('private source original exe unavailable')
        source=Path(__file__).resolve().parent.parent/'original_assets'/'source'
        art=load_verified_original_presults_bottom_art(source,orig)
        self.assertEqual(tuple((i.width,i.height) for i in
                         (art.original_waiting,art.original_progress_back,
                          art.original_progress_fill)),((800,87),(800,14),(800,10)))
        self.assertEqual(len(source_original_presults_bottom_surface(art).source_layers),2)
