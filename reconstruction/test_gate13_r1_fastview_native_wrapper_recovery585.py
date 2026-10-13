"""Original mode2 FastView synchronous wrapper: private static source guard only."""
from pathlib import Path
import os
import unittest


class OriginalR1FastViewNativeWrapperRecovery585Tests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_mode2_pre_result_native_modal_and_post_view_callbacks(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        source = (
            (0x513272, "e8 49 ff 01 00"),  # mode2 -> 0x5331C0
            (0x5331DE, "b9 60 79 87 00"),  # original modal manager
            (0x5331E3, "e8 c8 f6 ff ff"),  # manager precondition
            (0x5331F1, "e8 da f7 ff ff"),  # manager initialization
            (0x5331FE, "e8 6d 00 00 00"),  # 0x533270
            (0x533208, "56 e8 e2 09 00 00"),  # 0x533BF0
            (0x53321A, "e8 71 c2 fe ff"),  # 0x51F490
            (0x533236, "e8 15 f4 ff ff"),  # original 0x532650
            (0x53323C, "e8 5f 0a 00 00"),  # 0x533CA0 cleanup
            (0x533253, "e8 78 c4 fe ff"),  # 0x51F6D0
            (0x51329D, "ff 52 38"),  # common post-view callback
            (0x5132A9, "ff 52 3c"),  # common post-view callback
        )
        for address, encoded in source:
            with self.subTest(address=hex(address)):
                expected = bytes.fromhex(encoded)
                self.assertEqual(pe.read(address, len(expected)), expected)


    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_live_modal_pump_and_source_match_state_writeback(self):
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        source = (
            (0x53266A, "8d 4e 18"),           # native manager child
            (0x53266D, "e8 9e 1b 12 00"),     # 0x654210 native activation
            (0x5332B9, "83 fe 02"),           # two-side setup
            (0x533421, "83 f9 08"),           # eight source entries
            (0x533413, "83 f8 0f"),           # original clamp upper bound
            (0x533CD1, "b9 14 00 00 00"),     # twenty source DWORDs
            (0x533CE0, "f3 a5"),              # state copy operation
        )
        for address, encoded in source:
            with self.subTest(address=hex(address)):
                expected = bytes.fromhex(encoded)
                self.assertEqual(pe.read(address, len(expected)), expected)


    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_after_modal_two_team_writeback_and_real_player_byte_mutations(self):
        """Native post-modal state mutations, not an inert screen shutdown."""
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        guards = (
            (0x533CAD, "85 d2"),                   # side0 initially
            (0x533CB5, "8b 0b"),                   # side0 owner pointer
            (0x533CD1, "b9 14 00 00 00"),          # 20 original DWORDs
            (0x533CD8, "8d b0 f4 7c 87 00"),       # source side-indexed globals
            (0x533CE0, "f3 a5"),                   # 80-byte copy
            (0x533D06, "66 8b 75 00"),             # player/record ID
            (0x533D29, "8b 0d 44 56 87 00"),       # global object lookup
            (0x533D34, "8b b0 48 02 00 00"),       # referenced target+0x248
            (0x533D43, "e8 e8 65 fb ff"),          # 0x4EA330 actual setter
            (0x533D51, "e8 fa 65 fb ff"),          # 0x4EA350 actual setter
            (0x533D69, "42 83 fa 01"),             # second-side iteration
            (0x533D71, "0f 86 36 ff ff ff"),       # side loop
            (0x4EA33D, "80 e2 1f"),                # setter low 5 bits
            (0x4EA342, "88 51 03"),                # writes target+3
            (0x4EA35D, "80 e2 0f"),                # setter low 4 bits
            (0x4EA362, "88 51 04"),                # writes target+4
            (0x5332B9, "83 fe 02"),                # 2 initial source sides
            (0x5333B1, "8d 8e b4 05 00 00"),       # alternate side row base
            (0x5333A3, "8d 7e 4c"),                # initial side row base
        )
        for address, hexdump in guards:
            with self.subTest(address=hex(address)):
                expected = bytes.fromhex(hexdump)
                self.assertEqual(pe.read(address, len(expected)), expected)


    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_native_pre_modal_snapshots_are_the_inverse_of_post_modal_writeback(self):
        """Read-only exact PE proof of two-side copy plus packed flag capture."""
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        guards = (
            (0x533C1D, "b9 14 00 00 00"),         # 20 dwords per source side
            (0x533C24, "8d b8 f4 7c 87 00"),      # global side buffer destination
            (0x533C2A, "f3 a5"),                  # team to view copy
            (0x533C2C, "8b ad 94 02 00 00"),      # record count
            (0x533C40, "66 8b 33"),               # source player ID word
            (0x533C48, "8b 88 48 02 00 00"),      # player packed record
            (0x533C4E, "e8 6d 67 fb ff"),         # get field+3 low 5
            (0x533C59, "89 87 b4 7b 87 00"),      # snapshot 0x877BB4
            (0x533C64, "8b 88 48 02 00 00"),      # get packed record again
            (0x533C6A, "e8 61 67 fb ff"),         # get field+4 low 4
            (0x533C6F, "25 ff 00 00 00"),         # source masks getter
            (0x533C77, "89 87 74 7a 87 00"),      # snapshot 0x877A74
            (0x533C88, "83 fa 01"),               # second side included
            (0x4EA3C0, "8a 41 03 83 e0 1f c3"),  # original low5 getter
            (0x4EA3D0, "8a 41 04 24 0f c3"),     # original low4 getter
        )
        for address, code in guards:
            with self.subTest(address=hex(address)):
                expected = bytes.fromhex(code)
                self.assertEqual(pe.read(address, len(expected)), expected)



    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_fastview_modal_key_actions_and_postmodal_record_callbacks(self):
        """Source-only guard: original ESC/Space, native pump, and record callbacks."""
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        guards = (
            (0x7CB294, "80 2b 53 00"),         # original global-view vtable[0] = 0x532B80
            (0x7CA5C0, "a0 1d 52 00"),         # FastView keyboard vtable+0x34 = 0x521DA0
            (0x51F4AF, "68 58 02 00 00"),     # original height 600
            (0x51F4B8, "68 20 03 00 00"),     # original width 800
            (0x654258, "8b 07 8b cf ff 10"),  # invoke registered modal owner vtable[0]
            (0x654294, "8b cb e8 c5 00 00 00"),  # restore/remove modal owner
            (0x532BBF, "81 7c 24 14 00 04 00 00"),  # WM_USER (0x400) exit
            (0x532BD5, "ff 15 ac d2 7b 00"), # imported DispatchMessageA
            (0x532BEA, "e8 e1 fd ff ff"),     # modal owner message-pump/redraw path
            (0x532BF1, "ff 15 b0 d2 7b 00"), # imported WaitMessage
            (0x521DA0, "8a 81 b6 02 00 00"), # native modal keyboard-input guard
            (0x521DAF, "66 3d 1b 00"),       # ESC
            (0x521DB5, "6a 00 e8 34 1c 13 00"), # 0x6539F0 modal end event
            (0x521DBF, "66 3d 20 00"),       # Space
            (0x521DC5, "8b 91 ac 02 00 00"),# view state +0x2AC
            (0x521DCE, "89 91 ac 02 00 00"),# increment on Space
            (0x521DD4, "83 f8 03"),          # three internal states (0,1,2)
            (0x521DD9, "c7 81 ac 02 00 00 00 00 00 00"), # wrap at 3
            (0x6539FF, "68 00 04 00 00"),   # post WM_USER
            (0x533D0A, "83 fb 0b"),          # different real-record callbacks at index 11
            (0x533D16, "e8 d5 45 ee ff"),    # 0x4182F0 for indices 0..10
            (0x533D24, "e8 97 45 ee ff"),    # 0x4182C0 for indices >=11
            (0x4182CD, "0c 20 89 46 14"),    # target +0x14 status bit 0x20
            (0x4182E4, "e8 87 20 0d 00"),    # additional target packed-object call
            (0x4182F3, "83 4e 14 10 e8 64 fe ff ff"), # status bit 0x10 + callbacks
            (0x418311, "84 c0 75 11"),       # conditional downstream callback
        )
        for address, encoded in guards:
            with self.subTest(address=hex(address)):
                self.assertEqual(pe.read(address, len(bytes.fromhex(encoded))),
                                 bytes.fromhex(encoded))



    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_fastview_source_pointer_event_sibling_controls(self):
        """No invented click effects: guard the actual two sibling event branches."""
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        guards = (
            (0x521E06, "38 9e b6 02 00 00"),  # modal input guard
            (0x521E12, "38 9e b7 02 00 00"),  # second event-acceptance guard
            (0x521E34, "3d 46 a9 0b 00"),     # source event 0xBA946
            (0x521E3B, "3d 47 a9 0b 00"),     # source event 0xBA947
            (0x521E5E, "e8 1d 04 00 00"),     # guarded nested 0x522280
            (0x521E6C, "2d 32 ad 0b 00"),     # source event 0xBAD32
            (0x521E7E, "8d 8e 78 04 00 00"), # 0xBAD33 child +0x478
            (0x521E84, "e8 f7 10 13 00"),    # native child 0x652F80 test
            (0x521F0A, "8d 8e 24 04 00 00"), # 0xBAD32 child +0x424
            (0x521F10, "e8 6b 10 13 00"),    # native child 0x652F80 test
            (0x5222A3, "c6 86 b5 02 00 00 01"), # nested owner transition
            (0x522328, "e8 a3 06 01 00"),    # global redraw/update before child
            (0x522396, "68 58 02 00 00"),    # nested child height 600
            (0x52239B, "68 20 03 00 00"),    # nested child width 800
            (0x5223AC, "e8 6f 0f 13 00"),    # source 0x653320 child setup
        )
        for address, encoded in guards:
            with self.subTest(address=hex(address)):
                self.assertEqual(pe.read(address, len(bytes.fromhex(encoded))),
                                 bytes.fromhex(encoded))



    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_nested_modal_screen_choice_result_and_restoration(self):
        """Guard native two-panel modal construction and conditional parent return."""
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites = (
            (0x5222A3, "c6 86 b5 02 00 00 01"), # parent busy on nested opening
            (0x5222BD, "ff 50 34"), (0x5222CE, "ff 52 34"),
            (0x5222DF, "ff 50 34"), (0x5222EE, "ff 52 34"), # four child transitions
            (0x522354, "e8 f7 14 ee ff"), (0x52235B, "74 5a"), # branch predicate
            (0x52235D, "68 b0 48 00 00"), (0x52237F, "e8 3c b3 00 00"), # class A
            (0x522396, "68 58 02 00 00"), (0x52239B, "68 20 03 00 00"),
            (0x5223AC, "e8 6f 0f 13 00"), # class A 800x600 host
            (0x5223B7, "68 4c 2d 00 00"), (0x5223DB, "e8 b0 d4 00 00"), # class B
            (0x5223F6, "68 58 02 00 00"), (0x5223FB, "68 20 03 00 00"),
            (0x52240C, "e8 0f 0f 13 00"), # class B 800x600 host
            (0x522423, "e8 28 02 01 00"), # nested synchronous modal
            (0x522428, "85 c0"), (0x522445, "e8 56 fb ff ff"), # conditional update
            (0x52244E, "c6 86 b5 02 00 00 00"), # clear busy flag
            (0x522455, "ff 52 30"), (0x52245D, "ff 50 30"),
            (0x522464, "ff 52 30"), (0x522473, "ff 50 30"), # restore children
            (0x52249F, "e8 ac 0e 13 00"), # parent redraw
            (0x5224B4, "ff 12"), # destroy nested owned child
        )
        for address, code in sites:
            with self.subTest(address=hex(address)):
                want = bytes.fromhex(code)
                self.assertEqual(pe.read(address, len(want)), want)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_original_modal_wm_user_wparam_return_and_escape(self):
        """Native Escape 0 versus nonzero nested result, not a generic close."""
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites = (
            (0x521DB5, "6a 00 e8 34 1c 13 00"), # Escape posts 0
            (0x6539F7, "25 ff ff 00 00"),       # original WORD mask
            (0x6539FC, "6a 00"), (0x6539FE, "50"),
            (0x6539FF, "68 00 04 00 00"),       # WM_USER
            (0x659663, "ff 15 d8 d2 7b 00"),    # original PostMessageA
            (0x532BBF, "81 7c 24 14 00 04 00 00"),
            (0x532BF9, "8b 44 24 18"),          # MSG.wParam returned
            (0x654258, "8b 07 8b cf ff 10"),    # modal owner callback
            (0x65429B, "8b c7"),                # return value relayed
            (0x522428, "85 c0"),                # conditional branch
            (0x522445, "e8 56 fb ff ff"),      # nonzero -> source 0x521fa0
            (0x521FC7, "e8 54 fc 19 00"),      # nested update downstream
            (0x522052, "e8 19 60 ff ff"),      # nested update downstream
        )
        for address, code in sites:
            with self.subTest(address=hex(address)):
                want = bytes.fromhex(code)
                self.assertEqual(pe.read(address, len(want)), want)


if __name__ == "__main__":
    unittest.main()
