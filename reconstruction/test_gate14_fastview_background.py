import unittest

from gate14_fastview_background import (
    BACKGROUND_BINDING_STATUS,
    BACKGROUND_BYTE_SIZE,
    BACKGROUND_DIMENSIONS,
    BACKGROUND_PATH_LITERAL_VA,
    BACKGROUND_SHA256,
    BACKGROUND_SOURCE_PATH,
    DIRECT_FASTVIEW_PANEL_DRAW_OWNERSHIP,
    SOURCE_FASTVIEW_PANEL_CONSTRUCTOR_VA,
    SOURCE_FASTVIEW_PANEL_DIMENSIONS,
    SOURCE_GENERIC_PANEL_CONSTRUCTOR_VA,
    SOURCE_STATIC_STRING_INIT_VA,
    SOURCE_STATIC_STRING_OBJECT_VA,
    SOURCE_STATIC_STRING_RUNTIME_REFERENCE_COUNT,
    SOURCE_STRING_CONSTRUCTOR_VA,
    SOURCE_STRING_DESTRUCTOR_VA,
    background_is_source_bound_to_fastview_panel,
)


class FastViewBackgroundBoundaryTests(unittest.TestCase):
    def test_authenticated_asset_identity_is_recorded_without_draw_claim(self):
        self.assertEqual(
            BACKGROUND_SOURCE_PATH,
            "FM2001_Art/FastView/background.444",
        )
        self.assertEqual(BACKGROUND_PATH_LITERAL_VA, 0x8294E8)
        self.assertEqual(BACKGROUND_BYTE_SIZE, 205984)
        self.assertEqual(BACKGROUND_DIMENSIONS, (800, 600))
        self.assertEqual(
            BACKGROUND_SHA256,
            "499e930fe0a328d969096b8d2cdb8c817169f02812adcc78acf111dc666d95c0",
        )
        self.assertFalse(DIRECT_FASTVIEW_PANEL_DRAW_OWNERSHIP)
        self.assertFalse(background_is_source_bound_to_fastview_panel())
        self.assertEqual(
            BACKGROUND_BINDING_STATUS,
            "unbound_static_path_string_fail_closed",
        )

    def test_source_only_constructs_and_destroys_static_path_string(self):
        self.assertEqual(SOURCE_STATIC_STRING_INIT_VA, 0x51F2F0)
        self.assertEqual(SOURCE_STATIC_STRING_OBJECT_VA, 0x877758)
        self.assertEqual(SOURCE_STRING_CONSTRUCTOR_VA, 0x684620)
        self.assertEqual(SOURCE_STRING_DESTRUCTOR_VA, 0x68467F)
        self.assertEqual(SOURCE_STATIC_STRING_RUNTIME_REFERENCE_COUNT, 2)

    def test_panel_size_does_not_promote_background_binding(self):
        self.assertEqual(SOURCE_FASTVIEW_PANEL_CONSTRUCTOR_VA, 0x51F490)
        self.assertEqual(SOURCE_GENERIC_PANEL_CONSTRUCTOR_VA, 0x527350)
        self.assertEqual(SOURCE_FASTVIEW_PANEL_DIMENSIONS, (800, 600))
        self.assertFalse(background_is_source_bound_to_fastview_panel())


if __name__ == "__main__":
    unittest.main()
