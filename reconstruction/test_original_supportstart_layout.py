"""Original source SupportStart viewport screen placement, NOT hit testing."""
import unittest
from original_supportstart_layout import (
    SOURCE_SUPPORTSTART_NATIVE_SIZE,
    original_supportstart_native_modal_origin,
    original_supportstart_row_native_screen_rect,
    original_supportstart_action_native_screen_rect,
)

class OriginalSupportStartNativePlacementTests(unittest.TestCase):
    def test_source_800_by_600_viewport(self):
        self.assertEqual(SOURCE_SUPPORTSTART_NATIVE_SIZE, (760, 500))
        self.assertEqual(original_supportstart_native_modal_origin(
            viewport_size=(800,600)), (40,100))
        self.assertEqual(original_supportstart_row_native_screen_rect(
            0, viewport_size=(800,600)), (431,281,326,37))
        self.assertEqual(original_supportstart_row_native_screen_rect(
            6, viewport_size=(800,600)), (431,521,326,37))
        self.assertEqual(original_supportstart_action_native_screen_rect(
            1, viewport_size=(800,600)), (769,101,30,30))
        self.assertEqual(original_supportstart_action_native_screen_rect(
            2, viewport_size=(800,600)), (737,101,30,30))

    def test_exact_source_clamp_thresholds(self):
        expected = {
            (19,49):(19,49), (20,50):(20,50), (779,549):(20,50),
            (780,550):(20,50), (700,500):(20,50), (900,700):(140,200),
        }
        for viewport, origin in expected.items():
            with self.subTest(viewport=viewport):
                self.assertEqual(original_supportstart_native_modal_origin(
                    viewport_size=viewport), origin)
                self.assertEqual(original_supportstart_row_native_screen_rect(
                    2, viewport_size=viewport),
                    (origin[0]+391,origin[1]+261,326,37))

    def test_fail_closed_on_invalid_viewport_or_event_identity(self):
        for viewport in (None, [], (), (800,), (800,600,1),
                         (True,600), (800,0), (-1,600), (800,0x80000000)):
            with self.subTest(viewport=viewport), self.assertRaises(ValueError):
                original_supportstart_native_modal_origin(viewport_size=viewport)
        for index in (-1, 7, True, None):
            with self.subTest(index=index), self.assertRaises(ValueError):
                original_supportstart_row_native_screen_rect(
                    index, viewport_size=(800,600))
        for event in (0,3,True,None):
            with self.subTest(event=event), self.assertRaises(ValueError):
                original_supportstart_action_native_screen_rect(
                    event, viewport_size=(800,600))

if __name__ == "__main__":
    unittest.main()
