"""Ordinary original Tk host source-only PResults owner and graph transaction tests."""
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock
from ea444_decoder import EA444DecodedImage
from original_game_host import OriginalGameTkHost, OriginalGameHostError
from original_presults_bottom_surface import OriginalPResultsBottomArt
from original_presults_native_event_work import (
    OriginalPResultsDatedEventReceipt, OriginalPResultsSourceCallback,
)


def _image(w,h,b):
    return EA444DecodedImage(w,h,bytes((b,b,b,255))*(w*h),0,0)


def _art():
    return OriginalPResultsBottomArt(_image(800,87,12),_image(800,14,23),_image(800,10,34))


class _Canvas:
    def __init__(self):
        self.deletes=[]
        self.images=[]
    def delete(self,what):
        self.deletes.append(what)


class _Root:
    def __init__(self):
        self.after_calls=[]
    def configure(self,**kw):
        pass
    def after(self,delay,callback):
        self.after_calls.append((delay,callback))
        return len(self.after_calls)


class _Thread:
    def __init__(self,target,daemon):
        self.target=target
    def start(self):
        self.target()


class _Gameplay:
    def __init__(self):
        self.state=SimpleNamespace(calendar=SimpleNamespace(current_date='source-day'))
        self.calls=0
    def advance_original_management(self):
        self.calls+=1
        return SimpleNamespace(results_progress=None,pending_primary_entry=None)


def _host():
    host=object.__new__(OriginalGameTkHost)
    host.canvas=_Canvas()
    host.root=_Root()
    host.tk=SimpleNamespace(NW="nw")
    host._photos=[]
    host._presults_bottom_art=_art()
    host._presults_source_progress=None
    host._rgba_photo=lambda w,h,rgba:(w,h,rgba)
    host._create_native_image=lambda x,y,**kw:host.canvas.images.append((x,y,kw))
    host._management_turn_thread=object()
    host._management_turn_poll=None
    host._management_turn_queue=None
    host.last_status=''
    host.last_results_progress=None
    host.management_next_flags=2
    host._squad_drag_source=None
    host.presenter=SimpleNamespace(
        session=SimpleNamespace(gameplay=_Gameplay()))
    host.error_reporter=Mock()
    return host


class OriginalPResultsHostSurfaceTests(TestCase):
    def test_results_owner_draws_exact_original_bottom_only_not_fake_complete_frame(self):
        h=_host()
        h._draw_original_presults_partial()
        self.assertEqual(h.canvas.deletes,['all'])
        self.assertEqual([(x,y,img["image"][:2]) for x,y,img in h.canvas.images],
                         [(0,513,(800,87)),(0,579,(800,14))])
        self.assertEqual(tuple(img["image"][2][:4] for _,_,img in h.canvas.images),
                         (bytes((12,12,12,255)),bytes((23,23,23,255))))
        self.assertIn('incomplete',h.last_status)

    def test_genuine_source_events_draw_exact_quantized_fill_via_results_owner(self):
        h=_host()
        h.redraw=lambda:h._draw_original_presults_partial()
        callbacks=OriginalPResultsDatedEventReceipt((
            OriginalPResultsSourceCallback(0x8000,1,0x10,0x4a71f0),
            OriginalPResultsSourceCallback(0x8100,2,0x10,0x4a71f0)),True)
        h.apply_source_original_presults_dated_callbacks(
            original_dated_event_receipt=callbacks,
            original_source_event_total=4,original_processed_before_callbacks=0)
        self.assertEqual(h.canvas.images[-1][:2],(0,581))
        self.assertEqual(h.canvas.images[-1][2]["image"][:2],(400,10))
        self.assertEqual(len(h.canvas.images[-1][2]["image"][2]),400*10*4)

    def test_unqualified_ticks_rollback_without_mutating_visible_or_gameplay_state(self):
        h=_host()
        h.redraw=Mock()
        old=h._presults_source_progress
        initial=h.presenter.session.gameplay
        with self.assertRaises(ValueError):
            h.apply_source_original_presults_dated_callbacks(
                original_dated_event_receipt=((0x8000,0x4a71f0),),
                original_source_event_total=4,original_processed_before_callbacks=0)
        self.assertIs(h._presults_source_progress,old)
        self.assertIs(h.presenter.session.gameplay,initial)
        h.redraw.assert_not_called()
        h._management_turn_thread=None
        with self.assertRaises(OriginalGameHostError):
            h.apply_source_original_presults_dated_callbacks(
                original_dated_event_receipt=OriginalPResultsDatedEventReceipt((),False),
                original_source_event_total=0,original_processed_before_callbacks=0)

    def test_normal_next_worker_publishes_source_sprite_before_committing_turn(self):
        h=_host()
        h._presults_bottom_art=None
        h._presults_source_progress={'stale_prior_match':'do-not-reuse'}
        h._management_turn_thread=None
        h.presults_resource_loader=_art
        h.management_thread_factory=_Thread
        original=h.presenter.session.gameplay
        def redraw():
            if h._original_match_input_owner()=='results' and h._presults_bottom_art is not None:
                h._draw_original_presults_partial()
        h.redraw=redraw
        h._begin_original_management_turn()
        self.assertIsNone(h._presults_source_progress)
        # First worker receipt has only decoded original art, no game commit.
        self.assertEqual(original.calls,0)
        self.assertEqual(len(h.canvas.images),0)
        h._poll_original_management_turn()
        self.assertEqual(len(h.canvas.images),2)
        self.assertEqual(original.calls,0)
        self.assertIsNotNone(h._management_turn_thread)
        # Second receipt commits the staged gameplay only after all work.
        h._poll_original_management_turn()
        self.assertEqual(original.calls,1)
        self.assertIsNone(h._management_turn_thread)
        self.assertEqual(h.error_reporter.call_count,0)

    def test_resource_failure_does_not_commit_or_fake_any_original_pixels(self):
        h=_host()
        h._management_turn_thread=None
        h._presults_bottom_art=None
        def fail():
            raise ValueError("source sprite bad")
        h.presults_resource_loader=fail
        h.management_thread_factory=_Thread
        h.redraw=lambda:None
        old=h.presenter.session.gameplay
        h._begin_original_management_turn()
        h._poll_original_management_turn()
        self.assertIs(h.presenter.session.gameplay,old)
        self.assertEqual(old.calls,0)
        self.assertEqual(h.canvas.images,[])
        h.error_reporter.assert_called_once()
