from datetime import date
from hashlib import sha256
from pathlib import Path
import struct
from types import SimpleNamespace
import unittest

from original_management_background import (
    ASSET_HASHES, MONTH_VARIANTS, ManagementBackgroundError,
    OriginalManagementBackground, background_candidates, header_variant,
    native_art_component,
)


class ManagementBackgroundTests(unittest.TestCase):
    def test_exact_calendar_and_fan_base_boundaries(self):
        self.assertEqual(MONTH_VARIANTS, (2, 2, 3, 3, 0, 0, 0, 0, 1, 1, 1, 2))
        for month, variant in enumerate(MONTH_VARIANTS, 1):
            for fans, generic in ((0, 2), (8, 2), (9, 1), (20, 1), (21, 0)):
                paths = background_candidates('England', 'Aston Villa', month, fans)
                self.assertTrue(paths[0].endswith(f'/Aston_Villa_background{variant}.444'))
                self.assertTrue(paths[1].endswith('/Aston_Villa_background.444'))
                self.assertTrue(paths[2].endswith(f'/generic{generic}_background{variant}.444'))
                self.assertTrue(paths[3].endswith('/generic.444'))
        for month in (0, 13, True):
            with self.assertRaises(ManagementBackgroundError):
                background_candidates('England', 'Arsenal', month, 22)

    def test_exact_translation_not_display_name_slug(self):
        self.assertEqual(native_art_component("Üü Öö Ââ A.B'C"), 'Uu_Oo_Aa_A_B_C')
        self.assertEqual(native_art_component('Éé-Arsenal'), 'Éé-Arsenal')
        for value in ('', '../arsenal', 'a\\b', 'a\x00b'):
            with self.assertRaises(ManagementBackgroundError):
                native_art_component(value)

    def test_competition_not_country_header_switch(self):
        self.assertEqual([header_variant(i) for i in (0, 21, 22, 50, 51, 26)],
                         ['Premiership', 'Bundesliga', 'Bundesliga', 'LNF', 'LNF', 'generic'])

    def test_all_selected_assets_hash_and_native_geometry(self):
        root = Path(__file__).resolve().parents[1] / 'original_assets/source'
        self.assertEqual(len(ASSET_HASHES), 97)
        for path, digest in ASSET_HASHES.items():
            raw = (root / path).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), digest, path)
            expected = (385, 95) if '/Background_buttons/' in path else (800, 600)
            self.assertEqual(struct.unpack_from('<HH', raw), expected, path)

    def test_live_domain_does_not_fall_back_for_unstaged_original(self):
        renderer = object.__new__(OriginalManagementBackground)
        renderer.paths = {p.casefold(): p for p in ASSET_HASHES}
        renderer._image = lambda path, rect: (path, rect)
        club = SimpleNamespace(graphics_directory='England', graphics_basename='Arsenal',
                               current_date=date(2000, 8, 1), fan_base_index=22, competition_id=0)
        images = renderer.images(club)
        self.assertTrue(images[0][0].endswith('/arsenal_background0.444'))
        self.assertEqual(images[0][1], (0, 0, 800, 600))
        self.assertEqual(images[1][1], (171, 0, 385, 95))
        club.graphics_basename = 'Unstaged club'
        with self.assertRaises(ManagementBackgroundError):
            renderer.images(club)


if __name__ == '__main__':
    unittest.main()
