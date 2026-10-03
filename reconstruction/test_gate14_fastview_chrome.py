from pathlib import Path
import unittest

from gate14_fastview_chrome import (
    FASTVIEW_CHROME_RESOURCES,
    SOURCE_IMAGE_CONTROL_CONSTRUCTOR_VA,
    SOURCE_TICKER_CONTROL_CALL_VA,
    SOURCE_TICKER_PATH_SETUP_VA,
    SOURCE_TOP_BAR_CONTROL_CALL_VA,
    SOURCE_TOP_BAR_PATH_SETUP_VA,
    TICKER,
    TOP_BAR,
    validate_imported_fastview_chrome,
)


class FastViewChromeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent

    def test_direct_owned_source_geometry(self):
        self.assertEqual(SOURCE_IMAGE_CONTROL_CONSTRUCTOR_VA, 0x527730)
        self.assertEqual(SOURCE_TOP_BAR_PATH_SETUP_VA, 0x51FD63)
        self.assertEqual(SOURCE_TICKER_PATH_SETUP_VA, 0x51FDF0)
        self.assertEqual(SOURCE_TOP_BAR_CONTROL_CALL_VA, 0x51FDA3)
        self.assertEqual(SOURCE_TICKER_CONTROL_CALL_VA, 0x51FE31)
        self.assertEqual(TOP_BAR.rect, (0, 0, 800, 95))
        self.assertEqual(TICKER.rect, (0, 557, 800, 590))
        self.assertEqual(
            [resource.name for resource in FASTVIEW_CHROME_RESOURCES],
            ["top_bar.444", "ticker.444"],
        )

    def test_imported_source_assets_are_byte_exact(self):
        validate_imported_fastview_chrome(self.repo_root)


if __name__ == "__main__":
    unittest.main()
