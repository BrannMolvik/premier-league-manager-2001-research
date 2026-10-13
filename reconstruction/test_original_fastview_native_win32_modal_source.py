"""Native original FM2001 FastView WM_USER/pump source acceptance tests."""
import os
from pathlib import Path
import unittest
from original_fastview_native_win32_modal_source import (
    OriginalFastViewMessageSourceError,
    OriginalFastViewPumpAction,
    OriginalFastViewWin32MessageObservation as Obs,
    source_fastview_original_post_wm_user_6539f0,
    source_fastview_original_modal_step_532b80,
    source_fastview_original_nested_modal_trace_532b80,
)


class OriginalFastViewWin32EventLoopTests(unittest.TestCase):
    def test_real_native_app_close_sender_masks_wparam_to_16bit(self):
        evt=source_fastview_original_post_wm_user_6539f0(
            original_hwnd_from_view_plus64=0xCAFEBABE,
            original_event_dword=0x12AB34CD)
        self.assertEqual((evt.original_hwnd,evt.message,evt.wparam,evt.lparam),
                         (0xCAFEBABE,0x400,0x34CD,0))
        self.assertEqual(source_fastview_original_post_wm_user_6539f0(
            original_hwnd_from_view_plus64=1,original_event_dword=0x10000).wparam,0)
        self.assertEqual(source_fastview_original_post_wm_user_6539f0(
            original_hwnd_from_view_plus64=1,original_event_dword=0xFFFFFFFF).wparam,65535)
        for kwargs in (
                {"original_hwnd_from_view_plus64":0},
                {"original_hwnd_from_view_plus64":True},
                {"original_hwnd_from_view_plus64":0x100000000},
                {"original_event_dword":-1},
                {"original_event_dword":True},
                {"original_event_dword":0x100000000}):
            with self.subTest(kwargs=repr(kwargs)),self.assertRaises(OriginalFastViewMessageSourceError):
                source_fastview_original_post_wm_user_6539f0(**(
                    dict(original_hwnd_from_view_plus64=1,original_event_dword=2)|kwargs))

    def test_original_653a10_close_request_is_conditional_wm_user_post(self):
        from original_fastview_native_win32_modal_source import source_fastview_original_conditional_view_close_653a10
        self.assertIsNone(source_fastview_original_conditional_view_close_653a10(
            original_close_request_is_nonzero=False,
            original_view_owner_event_word_plus68=None,
            original_nested_window_hwnd=None))
        msg=source_fastview_original_conditional_view_close_653a10(
            original_close_request_is_nonzero=True,
            original_view_owner_event_word_plus68=0xAFFE,
            original_nested_window_hwnd=0x54321)
        self.assertEqual((msg.original_hwnd,msg.message,msg.wparam,msg.lparam),
                         (0x54321,0x400,0xAFFE,0))
        for change in (
            {'original_close_request_is_nonzero':0},
            {'original_close_request_is_nonzero':False},
            {'original_view_owner_event_word_plus68':0x10000},
            {'original_view_owner_event_word_plus68':None},
            {'original_nested_window_hwnd':0},
            {'original_nested_window_hwnd':None},
        ):
            args=dict(original_close_request_is_nonzero=True,
                      original_view_owner_event_word_plus68=0x55,
                      original_nested_window_hwnd=5)|change
            with self.subTest(args=repr(args)),self.assertRaises(OriginalFastViewMessageSourceError):
                source_fastview_original_conditional_view_close_653a10(**args)

    def test_empty_peek_uses_active_view_update_or_waitmessage_not_automatic_exit(self):
        for depth,action in ((0,OriginalFastViewPumpAction.WAIT_FOR_MESSAGE),
                             (1,OriginalFastViewPumpAction.UPDATE_NESTED_VIEW),
                             (2,OriginalFastViewPumpAction.UPDATE_NESTED_VIEW)):
            step=source_fastview_original_modal_step_532b80(Obs(False,depth))
            self.assertIs(step.action,action)
            self.assertIsNone(step.exit_wparam)
        with self.assertRaises(OriginalFastViewMessageSourceError):
            source_fastview_original_nested_modal_trace_532b80(
                native_source_messages=(Obs(False,1),Obs(False,0)))

    def test_source_original_nonexit_win32_dispatch_then_wm_user_exit(self):
        observed=(Obs(False,1),Obs(True,1,1,0x201,0xAAAA),
                  Obs(False,1),Obs(True,1,1,0x400,0x12345678))
        result=source_fastview_original_nested_modal_trace_532b80(
            native_source_messages=observed)
        self.assertEqual(result.native_exit_message,0x400)
        self.assertEqual(result.native_exit_wparam,0x12345678)
        self.assertEqual(result.number_of_pump_observations,4)
        self.assertEqual(result.number_of_view_updates,2)
        self.assertEqual(result.dispatched_message_types,(0x201,))
        self.assertIs(source_fastview_original_modal_step_532b80(
            Obs(True,1,1,0x202,0)).action,OriginalFastViewPumpAction.TRANSLATE_DISPATCH)

    def test_zero_getmessage_wmquit_exits_even_if_type_is_not_wm_user(self):
        source=source_fastview_original_nested_modal_trace_532b80(
            native_source_messages=(Obs(True,1,0,0x12,1234),))
        self.assertEqual((source.native_exit_message,source.native_exit_wparam),(0x12,1234))
        self.assertEqual(source.dispatched_message_types,())
        # Native 0x532B80 does NOT treat other message values as exit.
        self.assertIs(source_fastview_original_modal_step_532b80(
            Obs(True,1,1,0x12,5)).action,OriginalFastViewPumpAction.TRANSLATE_DISPATCH)

    def test_original_getmessage_error_and_unvisited_fields_fail_closed(self):
        cases=(Obs(True,1,-1,0x400,3),Obs(True,1,None,0x400,3),
               Obs(True,1,2,0x400,3),Obs(True,1,True,0x400,3),
               Obs(True,1,1,None,3),Obs(True,1,1,0x400,None),
               Obs(True,1,1,0x400,True),
               Obs(False,1,1,0x400,3),Obs(False,1,None,None,0),
               Obs(False,False),Obs(False,-1),Obs(True,0,1,0x100000000,2))
        for observation in cases:
            with self.subTest(o=repr(observation)),self.assertRaises(OriginalFastViewMessageSourceError):
                source_fastview_original_modal_step_532b80(observation)
        for history in ((),[Obs(True,0,1,0x400,0)],
                        (Obs(True,0,1,0x400,0),Obs(False,0)),):
            with self.subTest(history=repr(history)),self.assertRaises(OriginalFastViewMessageSourceError):
                source_fastview_original_nested_modal_trace_532b80(
                    native_source_messages=history)

    def test_source_modal_receipt_does_not_imply_calculator_result(self):
        receipt=source_fastview_original_nested_modal_trace_532b80(
            native_source_messages=(Obs(False,1),Obs(True,1,1,0x400,7)))
        self.assertFalse(hasattr(receipt,"match_score"))
        self.assertFalse(hasattr(receipt,"PResults"))
        self.assertEqual(receipt.native_exit_wparam,7)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "private original PE intentionally absent in GitHub CI")
    def test_original_shipped_pe_view_ctor_win32_imports_and_modal_exit_opcode(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x5331dc:"6a 00",0x5331de:"b9 60 79 87 00",
            0x5331fd:"56",0x5331fe:"e8 6d 00 00 00",
            0x533209:"e8 e2 09 00 00",
            0x533218:"6a 00",0x53321a:"e8 71 c2 fe ff",
            0x533226:"b9 60 79 87 00",0x533236:"e8 15 f4 ff ff",
            0x53323c:"e8 5f 0a 00 00",0x533253:"e8 78 c4 fe ff",
            0x53262f:"c7 07 94 b2 7c 00",
            0x7CB294:"80 2b 53 00",
            0x53265a:"e8 e1 88 fa ff",
            0x53266a:"8d 4e 18",
            0x53266d:"e8 9e 1b 12 00",
            0x654221:"56",0x654225:"e8 86 00 00 00",
            0x654258:"8b 07",0x65425c:"ff 10",
            0x654264:"3b c5",0x654294:"8b cb",
            0x654296:"e8 c5 00 00 00",
            0x532b99:"8b f1",0x532ba8:"ff d7",
            0x532bb9:"ff d3",0x532bbf:"81 7c 24 14 00 04 00 00",
            0x532bc9:"8d 54 24 10",0x532bce:"ff d5",
            0x532bd5:"ff 15 ac d2 7b 00",
            0x532bdd:"8b 46 08",0x532be4:"6a 00",
            0x532bea:"e8 e1 fd ff ff",
            0x532bf1:"ff 15 b0 d2 7b 00",
            0x532bf9:"8b 44 24 18",
            0x6539f7:"25 ff ff 00 00",
            0x653a10:"8b 44 24 04",
            0x653a14:"85 c0",
            0x653a18:"66 8b 41 68",
            0x653a1c:"8b 49 08",
            0x653a20:"50",
            0x653a23:"e8 c8 ff ff ff",
            0x6539ff:"68 00 04 00 00",
            0x653a04:"e8 47 5c 00 00",
            0x659663:"ff 15 d8 d2 7b 00",
        }
        for va,hx in sites.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))
