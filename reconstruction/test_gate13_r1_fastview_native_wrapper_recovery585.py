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


if __name__ == "__main__":
    unittest.main()
