import tempfile
import unittest
from pathlib import Path

from gate14_fastview_chrome import (
    FASTVIEW_DIRECT_CHROME_RESOURCES,
    REJECTED_UNBOUND_BACKGROUND_PATH,
    SOURCE_PICTURE_CONTROL_CONSTRUCTOR_VA,
    SOURCE_PICTURE_CONTROL_RTTI,
    SOURCE_PICTURE_CONTROL_VFTABLE,
    TICKER,
    TOP_BAR,
    FastViewChromeError,
    validate_imported_fastview_chrome,
)


class FastViewChromeTests(unittest.TestCase):
    def test_direct_picture_control_identity_and_exact_rectangles(self):
        self.assertEqual(SOURCE_PICTURE_CONTROL_CONSTRUCTOR_VA, 0x527730)
        self.assertEqual(SOURCE_PICTURE_CONTROL_VFTABLE, 0x7CAA5C)
        self.assertEqual(SOURCE_PICTURE_CONTROL_RTTI, ".?AVPictureControl@@")
        self.assertEqual(TOP_BAR.path_literal_va, 0x829734)
        self.assertEqual(TOP_BAR.string_init_va, 0x51FD63)
        self.assertEqual(TOP_BAR.picture_control_call_va, 0x51FDA3)
        self.assertEqual(TOP_BAR.rect, (0, 0, 800, 95))
        self.assertEqual(TICKER.path_literal_va, 0x829714)
        self.assertEqual(TICKER.string_init_va, 0x51FDF0)
        self.assertEqual(TICKER.picture_control_call_va, 0x51FE31)
        self.assertEqual(TICKER.rect, (0, 557, 800, 590))

    def test_source_identities_are_locked_and_background_is_excluded(self):
        self.assertEqual(
            [(x.name, x.byte_size, x.size, x.sha256) for x in FASTVIEW_DIRECT_CHROME_RESOURCES],
            [
                (
                    "top_bar",
                    19268,
                    (800, 95),
                    "f7410cf85900846ee1b276fa309bca4e560580286d5641092f2f98d20afa379a",
                ),
                (
                    "ticker",
                    6352,
                    (800, 33),
                    "b0fe2d8266ae157b7821e8c1de310e89bbc37ae859f666e64f59731c78e68257",
                ),
            ],
        )
        paths = {x.source_path for x in FASTVIEW_DIRECT_CHROME_RESOURCES}
        self.assertNotIn(REJECTED_UNBOUND_BACKGROUND_PATH, paths)

    def test_validator_fails_closed_when_staged_bytes_are_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(FastViewChromeError, "Missing staged"):
                validate_imported_fastview_chrome(Path(tmp))


if __name__ == "__main__":
    unittest.main()
