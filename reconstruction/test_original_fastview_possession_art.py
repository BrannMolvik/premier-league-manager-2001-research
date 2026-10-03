import unittest

from ea444_decoder import EA444DecodedImage
from original_fastview_possession_art import (
    OriginalFastViewPossessionArtError,
    build_fastview_possession_art,
)
from original_fastview_possession_resources import (
    FASTVIEW_POSSESSION_DIAGRAM_RESOURCES,
)


def decoded(width: int, height: int, value: int) -> EA444DecodedImage:
    return EA444DecodedImage(
        width=width,
        height=height,
        rgba=bytes([value]) * (width * height * 4),
        consumed_bits=0,
        transparent_pixels=0,
    )


class OriginalFastViewPossessionArtTests(unittest.TestCase):
    def setUp(self):
        self.art = {
            resource.name: decoded(
                resource.size[0],
                resource.size[1],
                index + 1,
            )
            for index, resource in enumerate(
                FASTVIEW_POSSESSION_DIAGRAM_RESOURCES
            )
        }

    def test_builds_only_source_proven_base_and_active_overlay(self):
        frame = build_fastview_possession_art(self.art, 2)

        self.assertEqual(frame.state, 2)
        self.assertEqual(
            [
                (item.role, item.resource_name, item.rect)
                for item in frame.placements
            ],
            [
                ("base_pitch", "pitch_normal", (253, 139, 547, 217)),
                ("active_overlay", "pitch_right", (422, 139, 547, 217)),
            ],
        )
        self.assertEqual(
            frame.placements[0].rgba,
            self.art["pitch_normal"].rgba,
        )
        self.assertEqual(
            frame.placements[1].rgba,
            self.art["pitch_right"].rgba,
        )

    def test_frame_does_not_claim_unrecovered_surrounding_pixels_or_semantics(self):
        frame = build_fastview_possession_art(self.art, 1)

        self.assertFalse(frame.surrounding_fastview_background_recovered)
        self.assertFalse(frame.possession_text_typography_recovered)
        self.assertFalse(frame.human_side_orientation_recovered)
        self.assertFalse(frame.complete_fastview_frame_available)

    def test_missing_or_wrong_geometry_fails_closed(self):
        missing = dict(self.art)
        del missing["pitch_normal"]
        with self.assertRaisesRegex(
            OriginalFastViewPossessionArtError,
            "Missing decoded",
        ):
            build_fastview_possession_art(missing, 0)

        wrong = dict(self.art)
        wrong["pitch_left"] = decoded(124, 78, 7)
        with self.assertRaisesRegex(
            OriginalFastViewPossessionArtError,
            "geometry mismatch",
        ):
            build_fastview_possession_art(wrong, 0)

    def test_invalid_state_fails_closed(self):
        with self.assertRaises(OriginalFastViewPossessionArtError):
            build_fastview_possession_art(self.art, 3)


if __name__ == "__main__":
    unittest.main()
