import unittest

from startup_fmv_presentation import (
    CODED_SIZE,
    GAME_DISPLAY_BPP,
    HORIZONTAL_REPEAT,
    MOVIE_SURFACE_SIZE,
    ORDINARY_GAME_DISPLAY_SIZE,
    ORDINARY_MOVIE_OFFSET,
    ORIGINAL_STARTUP_FMV_PRESENTATION,
    STARTUP_DOUBLE_WIDTH_FLAG,
    StartupFmvPresentation,
    StartupFmvPresentationError,
)


class StartupFmvPresentationTests(unittest.TestCase):
    def test_source_proven_geometry_and_nearest_duplication_contract(self):
        p = ORIGINAL_STARTUP_FMV_PRESENTATION
        self.assertEqual(CODED_SIZE, (320, 480))
        self.assertEqual(MOVIE_SURFACE_SIZE, (640, 480))
        self.assertEqual(ORDINARY_GAME_DISPLAY_SIZE, (800, 600))
        self.assertEqual(ORDINARY_MOVIE_OFFSET, (80, 60))
        self.assertEqual(HORIZONTAL_REPEAT, 2)
        self.assertEqual(STARTUP_DOUBLE_WIDTH_FLAG, 0x40)
        self.assertEqual(GAME_DISPLAY_BPP, 16)
        self.assertEqual(p.ffmpeg_filter, "scale=640:480:flags=neighbor")
        self.assertEqual(p.source_rect, (0, 0, 640, 480))
        self.assertEqual(p.ordinary_destination_rect, (80, 60, 720, 540))

    def test_contract_rejects_aspect_fit_interpolation_or_vertical_scaling(self):
        for kwargs in (
            {"horizontal_repeat": 1, "movie_width": 320},
            {"movie_height": 960},
            {"display_bpp": 8},
            {"movie_x": 0},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(StartupFmvPresentationError):
                    StartupFmvPresentation(**kwargs)


if __name__ == "__main__":
    unittest.main()
