import unittest

from ea444_decoder import EA444DecodedImage
from original_management_header import (
    HEADER_CAPTION_GLOBAL_VA,
    HEADER_CAPTION_RECT,
    HEADER_CAPTION_STYLE,
    HEADER_COMPOUND_RECT,
    HEADER_FONT_OBJECT_VA,
    HEADER_FONT_SOURCE_PATH,
    HEADER_LEFT_RECT,
    HEADER_LEFT_RESOURCE,
    HEADER_RIGHT_RECT,
    HEADER_RIGHT_RESOURCE,
    OriginalManagementHeaderError,
    OriginalManagementHeaderFrame,
    OriginalManagementHeaderResources,
    management_header_overlays,
)


class OriginalManagementHeaderTests(unittest.TestCase):
    def test_fixed_source_geometry_and_resource_identity(self):
        self.assertEqual(HEADER_COMPOUND_RECT, (599, 0, 100, 95))
        self.assertEqual(HEADER_LEFT_RECT, (599, 0, 30, 95))
        self.assertEqual(HEADER_RIGHT_RECT, (629, 0, 70, 95))
        self.assertEqual(HEADER_CAPTION_RECT, (631, 62, 70, 30))
        self.assertEqual(HEADER_CAPTION_STYLE, 10)
        self.assertEqual(HEADER_LEFT_RESOURCE.frame_count, 51)
        self.assertEqual(HEADER_RIGHT_RESOURCE.frame_count, 4)
        self.assertEqual(
            HEADER_LEFT_RESOURCE.sha256,
            "867abd21e89b21c878d20777547524e8ea4a00fcc9b49524f8356b631a665f69",
        )
        self.assertEqual(
            HEADER_RIGHT_RESOURCE.sha256,
            "710016aa4f9c2d5a04580ba48e2449882040482d231b875726203836b8cb42bb",
        )
        self.assertEqual(HEADER_FONT_SOURCE_PATH, "Fonts/Zurich_XCn_BT_24pixel.fnt")
        self.assertEqual(HEADER_FONT_OBJECT_VA, 0x8B0760)
        self.assertEqual(HEADER_CAPTION_GLOBAL_VA, 0x9820F4)

    def test_frame_contract_rejects_unqualified_out_of_atlas_rows(self):
        for left, right in ((-1, 0), (51, 0), (0, -1), (0, 4)):
            with self.assertRaises(OriginalManagementHeaderError):
                OriginalManagementHeaderFrame(left, right)
        self.assertEqual(
            OriginalManagementHeaderFrame(50, 3),
            OriginalManagementHeaderFrame(left_source_row=50, right_source_row=3),
        )

    def test_overlay_crop_uses_exact_95px_physical_atlas_rows(self):
        left_rgba = bytearray(30 * 4845 * 4)
        right_rgba = bytearray(70 * 380 * 4)
        # Mark one pixel in the requested physical source rows so this test
        # proves crop selection rather than only output dimensions.
        left_offset = (17 * 95 * 30) * 4
        right_offset = (2 * 95 * 70) * 4
        left_rgba[left_offset:left_offset + 4] = b"\x01\x02\x03\x04"
        right_rgba[right_offset:right_offset + 4] = b"\x05\x06\x07\x08"

        resources = OriginalManagementHeaderResources(
            EA444DecodedImage(30, 4845, bytes(left_rgba), 0, 0),
            EA444DecodedImage(70, 380, bytes(right_rgba), 0, 0),
            object(),
        )
        overlays = management_header_overlays(
            resources,
            OriginalManagementHeaderFrame(17, 2),
        )
        self.assertEqual(
            [(item.role, item.source_row, (item.x, item.y, item.width, item.height))
             for item in overlays],
            [
                ("left_anim", 17, HEADER_LEFT_RECT),
                ("right_state", 2, HEADER_RIGHT_RECT),
            ],
        )
        self.assertEqual(overlays[0].rgba[:4], b"\x01\x02\x03\x04")
        self.assertEqual(overlays[1].rgba[:4], b"\x05\x06\x07\x08")
        self.assertEqual(len(overlays[0].rgba), 30 * 95 * 4)
        self.assertEqual(len(overlays[1].rgba), 70 * 95 * 4)


if __name__ == "__main__":
    unittest.main()
