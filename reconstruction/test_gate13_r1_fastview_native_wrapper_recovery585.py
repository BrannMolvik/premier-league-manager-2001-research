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


if __name__ == "__main__":
    unittest.main()
