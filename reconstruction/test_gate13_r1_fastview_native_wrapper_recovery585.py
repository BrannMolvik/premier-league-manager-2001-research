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



    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_nested_fastview_two_real_event_dispatchers_and_native_jump_table(self):
        """Full 68-entry source dispatch classification, not guessed control names."""
        import struct
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        self.assertEqual(struct.unpack("<I", pe.read(0x7CAD0C, 4))[0], 0x52E3F0)
        self.assertEqual(struct.unpack("<I", pe.read(0x7CB224, 4))[0], 0x5302A0)
        # Original 0x52E3F0 accepts event IDs 1 through 68.
        self.assertEqual(pe.read(0x52E428, 3), bytes.fromhex("83 f8 43"))
        cases = pe.read(0x52ECF0, 68)
        targets = struct.unpack("<14I", pe.read(0x52ECB8, 14 * 4))
        self.assertEqual(targets, (
            0x52E854, 0x52E8D2, 0x52E8DF, 0x52E947,
            0x52E928, 0x52E440, 0x52E4AE, 0x52E51D,
            0x52E593, 0x52E606, 0x52E69B, 0x52E72D,
            0x52E7C2, 0x52E975))
        expected = {1: 0, 2: 1, 3: 2, 59: 3, 60: 4,
                    61: 5, 62: 6, 63: 7, 64: 8, 65: 9,
                    66: 10, 67: 11, 68: 12}
        self.assertEqual(
            {i + 1: k for i, k in enumerate(cases) if k != 13}, expected)
        self.assertEqual([i + 1 for i, k in enumerate(cases) if k == 13],
                         list(range(4, 59)))
        # Final actual nested class keyboard slots differ from inherited base.
        self.assertEqual(struct.unpack("<I", pe.read(0x7CAC98, 4))[0], 0x52D350)
        self.assertEqual(struct.unpack("<I", pe.read(0x7CAD30, 4))[0], 0x428AE0)
        self.assertEqual(struct.unpack("<I", pe.read(0x7CB248, 4))[0], 0x428AE0)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_nested_fastview_one_branch_may_post_bool_result(self):
        """Only source-bounded accepted/cancel event return, no UI semantic labels."""
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        guards = (
            (0x52E8D2, "55 8b ce e8 16 51 12 00"),  # event2 posts EBP=0
            (0x52E8F5, "e8 76 42 10 00"),           # event3 return-source check
            (0x52E903, "8b 8e 90 00 00 00"),       # only success path runs extra action
            (0x52E911, "e8 9a 33 19 00"),          # conditional original side effect
            (0x52E919, "66 33 d2"),                 # zero DWORD before source BOOL
            (0x52E91E, "8a d3"),                    # BOOL copied to exit wParam
            (0x52E921, "e8 ca 50 12 00"),          # event3 posts BOOL exit
            (0x5302A8, "8b 40 20 48 75 07"),       # alternate event 1 check
            (0x5302AE, "6a 00"),                    # alternate event1 posts zero
            (0x5302B0, "e8 3b 37 12 00"),          # native result delivery
        )
        for address, code in guards:
            with self.subTest(address=hex(address)):
                want = bytes.fromhex(code)
                self.assertEqual(pe.read(address, len(want)), want)



    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_mode2_70_dword_side_buffers_confirm_and_live_prepare(self):
        """Separate 280-byte per-side state from the 80-byte player snapshot."""
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites = (
            (0x52D3C3, "89 86 90 00 00 00"),      # screen receives selected side
            (0x533203, "e8 e8 ea 18 00"),        # reset two side flags
            (0x6C1C26, "8b 04 8d f0 45 a1 00"), # side flag selector
            (0x6C1C3E, "b9 46 00 00 00"),       # 70 DWORD alternate read
            (0x6C1C46, "8d 34 c5 f8 45 a1 00"),# +side*280 alternate buffer
            (0x6C1C4D, "f3 a5"),                 # alternate copy
            (0x6C1C5B, "8d 34 cd 98 48 a1 00"),# +side*280 default buffer
            (0x6C1C62, "b9 46 00 00 00"),
            (0x6C1C67, "f3 a5"),                 # default copy
            (0x6C1C81, "b9 46 00 00 00"),      # 70 DWORD alternate write
            (0x6C1C8B, "8d 3c c5 f8 45 a1 00"),
            (0x6C1C92, "f3 a5"),
            (0x6C1C95, "c7 04 95 f0 45 a1 00 01 00 00 00"), # flag 1
            (0x6C1CC1, "b9 46 00 00 00"),      # 70 DWORD commit from screen
            (0x6C1CCB, "8d 3c c5 98 48 a1 00"),
            (0x6C1CD2, "f3 a5"),
            (0x6C1CD5, "c7 04 95 f0 45 a1 00 00 00 00 00"), # flag 0
            (0x6C1CF2, "a3 f0 45 a1 00"),      # mode2 first side reset
            (0x6C1CF7, "a3 f4 45 a1 00"),      # mode2 second side reset
            (0x6C1D15, "b9 85 01 00 00"),      # 389 DWORD side producer
            (0x6C1D1A, "8d 3c 95 d0 4a a1 00"),
            (0x6C1D21, "f3 a5"),
            (0x6C1D5B, "b9 46 00 00 00"),      # producer-to-default 70 DWORDs
            (0x6C1D64, "8d 1c c5 98 48 a1 00"),
            (0x6C1D6F, "f3 a5"),
            (0x52E911, "e8 9a 33 19 00"),     # conditional native commit
            (0x52E919, "66 33 d2"),           # native result from BOOL
            (0x52E921, "e8 ca 50 12 00"),
        )
        for address, code in sites:
            with self.subTest(address=hex(address)):
                want = bytes.fromhex(code)
                self.assertEqual(pe.read(address, len(want)), want)



    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_nested_tactics_classes_are_gated_by_actual_registered_human_club(self):
        """PE RTTI and original membership lookup, not presumed generic FastView."""
        import struct
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for vtable, expected in (
            (0x7CACFC, b".?AVFastViewTactics@@"),
            (0x7CB214, b".?AVFastViewCPUTactics@@"),
        ):
            with self.subTest(vtable=hex(vtable)):
                col, = struct.unpack("<I", pe.read(vtable - 4, 4))
                type_descriptor, = struct.unpack("<I", pe.read(col + 12, 4))
                self.assertEqual(pe.read(type_descriptor + 8, len(expected)), expected)
        guards = (
            (0x4037B1, "b9 10 4c 87 00"),       # global user owner
            (0x4037B6, "e8 25 02 01 00"),      # source linked-user check
            (0x403853, "e8 58 ff ff ff"),       # selected club registration precondition
            (0x403858, "3c 01"),                # guard exactly true
            (0x40385C, "8b 46 04"),            # club ID
            (0x40385F, "b9 10 4c 87 00"),
            (0x403865, "e8 d6 02 01 00"),      # registered user lookup
            (0x40386C, "33 c0"),               # no human -> null
            (0x4139E0, "8b 44 24 04"),
            (0x4139E8, "e8 03 00 00 00"),
            (0x4139F0, "8b 81 cc 09 00 00"),  # user list head
            (0x413A12, "32 c0"),               # no managed club
            (0x413A17, "b0 01"),               # managed club found
            (0x413B40, "8b 81 cc 09 00 00"),
            (0x413B5C, "39 4a 04"),            # club ID match
            (0x413B68, "33 c0"),               # unmatched -> null
            (0x413B6D, "8b 00"),               # return linked user
            (0x52D3C3, "89 86 90 00 00 00"),  # nested selected side
        )
        for address, code in guards:
            with self.subTest(address=hex(address)):
                want = bytes.fromhex(code)
                self.assertEqual(pe.read(address, len(want)), want)



    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "Original private executable not mounted")
    def test_human_fastview_tactics_four_native_cycling_settings_and_source_keys(self):
        """Exact native selector values and original string keys, not guessed labels."""
        import struct
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        source_tables = (
            (0x8498C8, ("NOT_USED", "PlayAttack", "PlayNormal", "PlayDefend")),
            (0x8498D8, ("WithBallNormal", "WithBallShortPass",
                        "WithBallLongBall", "WithBallCounter")),
            (0x8498E8, ("WithoutBallNormal", "WithoutBallContain",
                        "WithoutBallPress", "WithoutBallOffsideTrap")),
            (0x8498F8, ("AggressionLow", "AggressionMedium", "AggressionHigh")),
        )
        for table_address, keys in source_tables:
            with self.subTest(table=hex(table_address)):
                addresses = struct.unpack("<" + str(len(keys)) + "I",
                                          pe.read(table_address, 4 * len(keys)))
                for addr, key in zip(addresses, keys):
                    self.assertEqual(pe.read(addr, len(key) + 1),
                                     key.encode("ascii") + b"\\0")
        guards = (
            (0x52E440, "8b 86 58 0a 00 00"), # event 61 decrease Play
            (0x52E44F, "c7 86 58 0a 00 00 03 00 00 00"), # Play wraps to 3
            (0x52E4AE, "8b 8e 58 0a 00 00"), # event62 increase Play
            (0x52E4BD, "83 f8 04"),           # Play upper bound
            (0x52E51D, "8b 8e 5c 0a 00 00"), # event63 decrease WithBall
            (0x52E530, "c7 86 5c 0a 00 00 03 00 00 00"),
            (0x52E593, "8b 8e 5c 0a 00 00"), # event64 increase WithBall
            (0x52E5A2, "83 f8 04"),
            (0x52E606, "8b 8e 60 0a 00 00"), # event65 decrease WithoutBall
            (0x52E619, "c7 86 60 0a 00 00 03 00 00 00"),
            (0x52E69B, "8b 8e 60 0a 00 00"), # event66 increase WithoutBall
            (0x52E6AA, "83 f8 04"),
            (0x52E72D, "8b 8e 64 0a 00 00"), # event67 decrease Aggression
            (0x52E740, "c7 86 64 0a 00 00 02 00 00 00"),
            (0x52E7C2, "8b 8e 64 0a 00 00"), # event68 increase Aggression
            (0x52E7D1, "83 f8 03"),           # Aggression upper bound
        )
        for address, code in guards:
            with self.subTest(address=hex(address)):
                want = bytes.fromhex(code)
                self.assertEqual(pe.read(address, len(want)), want)


if __name__ == "__main__":
    unittest.main()
