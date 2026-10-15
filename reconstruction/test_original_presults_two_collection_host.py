"""Original PResults dual-date-calendar source receipts -> genuine partial Tk pixel UI.

The original first 947AD8 AL must be returned, while second 947AF0
callback ticks still count. These tests never invent source GameState
events, total counts or original Win11 GUI acceptance.
"""
from unittest import TestCase
from unittest.mock import Mock

from original_presults_bottom_surface import (
    source_original_presults_bottom_surface,OriginalPResultsSourceError)
from original_presults_native_event_work import (
    OriginalPResultsDatedEventReceipt as Dated,
    OriginalPResultsSourceCallback as Tick,
    OriginalPResultsEventSourceError,
)
from original_presults_two_collection_dispatch import (
    source_original_4a8260_two_collection_date_callbacks as join,
)
from test_original_presults_host_surface import _host, _art


def cb(ptr,passid=1):
    return Tick(ptr,passid,0x10,0x4a71f0)


def receipt(primary=(),secondary=(),p_return=False,s_return=False):
    return join(original_primary_947ad8=Dated(tuple(primary),p_return),
                original_secondary_947af0=Dated(tuple(secondary),s_return))


class OriginalPResultsTwoCollectionTkTests(TestCase):
    def test_dual_registry_original_progress_draws_exact_native_source_pixels(self):
        r=receipt((cb(0x8000,1),cb(0x8000,2)),
                  (cb(0x9000,1),),True,False)
        self.assertTrue(r.original_4a8260_return_al_nonzero)
        s=source_original_presults_bottom_surface(_art(),
            original_two_collection_4a8260=r,
            original_source_event_total=4,
            original_processed_before_callbacks=0)
        self.assertEqual(tuple(layer.source_role for layer in s.source_layers),
                         ('waiting_back_2','loading_back','loading_fill'))
        self.assertEqual(s.source_layers[-1].native_rect,(0,581,600,10))
        self.assertEqual(s.source_layers[-1].rgba,
                         bytes((34,34,34,255))*6000)
        self.assertTrue(s.original_native_progress_eligible)
        self.assertFalse(s.normal_gameplay_result_committed)

    def test_secondary_source_events_count_but_do_not_replace_primary_return_al(self):
        r=receipt((),(cb(0x9000,1),),False,False)
        self.assertFalse(r.original_4a8260_return_al_nonzero)
        s=source_original_presults_bottom_surface(_art(),
            original_two_collection_4a8260=r,
            original_source_event_total=4,
            original_processed_before_callbacks=0)
        self.assertEqual(s.source_layers[-1].native_rect,(0,581,200,10))
        h=_host()
        h.redraw=lambda:h._draw_original_presults_partial()
        h.apply_source_original_presults_two_collection_callbacks(
            original_two_collection_receipt=r,
            original_source_event_total=4,
            original_processed_before_callbacks=0)
        self.assertEqual(h.canvas.images[-1][:2],(0,581))
        self.assertEqual(h.canvas.images[-1][2]['image'][:2],(200,10))
        self.assertFalse(r.original_4a8260_return_al_nonzero)

    def test_native_overshoot_refuses_fake_800px_clamp_or_partial_state_commit(self):
        r=receipt((cb(0x8000,1),),(cb(0x9000,2),),False,True)
        h=_host()
        h.redraw=Mock()
        old=h._presults_source_progress
        old_gameplay=h.presenter.session.gameplay
        with self.assertRaises(OriginalPResultsSourceError):
            h.apply_source_original_presults_two_collection_callbacks(
                original_two_collection_receipt=r,
                original_source_event_total=1,
                original_processed_before_callbacks=0)
        self.assertIs(h._presults_source_progress,old)
        self.assertIs(h.presenter.session.gameplay,old_gameplay)
        h.redraw.assert_not_called()
        self.assertEqual(h.canvas.images,[])
        # Counter-only source report still records real num>denom.
        from original_presults_two_collection_dispatch import (
            source_original_4a8260_native_progress_counter_receipts as counters)
        series=counters(original_two_collection_receipt=r,
            original_before_processed_64=0,
            original_first_collection_4a7210_total_68=1)
        self.assertEqual(series[-1].native_width,1600)

    def test_wrong_match_owner_and_unqualified_callback_cannot_fake_progress(self):
        r=receipt((cb(0x8000,1),),(),False,False)
        h=_host()
        h._management_turn_thread=None
        h.redraw=Mock()
        with self.assertRaises(Exception):
            h.apply_source_original_presults_two_collection_callbacks(
                original_two_collection_receipt=r,
                original_source_event_total=4,
                original_processed_before_callbacks=0)
        h.redraw.assert_not_called()
        h._management_turn_thread=object()
        cases=[
            {'original_two_collection_receipt':None},
            {'original_source_event_total':None},
            {'original_source_event_total':True},
            {'original_processed_before_callbacks':-1},
        ]
        for change in cases:
            opts=dict(original_two_collection_receipt=r,
                      original_source_event_total=4,
                      original_processed_before_callbacks=0)
            opts.update(change)
            with self.subTest(change=change),self.assertRaises(
                (OriginalPResultsSourceError,OriginalPResultsEventSourceError)
            ):
                h.apply_source_original_presults_two_collection_callbacks(**opts)
        h.redraw.assert_not_called()
        self.assertIsNone(h._presults_source_progress)

    def test_mixed_original_single_and_two_registry_receipts_fail_without_bitmap(self):
        r=receipt((),(cb(0x9000,1),),False,False)
        with self.assertRaises(OriginalPResultsSourceError):
            source_original_presults_bottom_surface(
                _art(),
                original_dated_event_receipt=Dated((),False),
                original_two_collection_4a8260=r,
                original_source_event_total=4,
                original_processed_before_callbacks=0)
