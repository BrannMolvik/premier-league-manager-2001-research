import unittest
from original_window_viewport import window_fit_scale


class WindowViewportTests(unittest.TestCase):
    def test_normal_and_sub_native_clients_fit_without_cropping(self):
        for width, height, expected in ((800, 600, (1, 1)), (1920, 1080, (9, 5)),
                (2560, 1440, (12, 5)), (640, 480, (4, 5)), (400, 300, (1, 2))):
            with self.subTest(client=(width, height)):
                self.assertEqual(window_fit_scale(width, height), expected)

    def test_odd_client_sizes_never_exceed_parent(self):
        for width in range(320, 2100, 37):
            for height in range(240, 1200, 41):
                n, d = window_fit_scale(width, height)
                self.assertGreater(n, 0)
                self.assertLessEqual(d, 16)
                self.assertLessEqual((800*n+d-1)//d, width)
                self.assertLessEqual((600*n+d-1)//d, height)

    def test_invalid_clients_rejected(self):
        for size in ((0, 600), (800, 0), (True, 600), (800.0, 600), (1, 1)):
            with self.assertRaises(ValueError):
                window_fit_scale(*size)
