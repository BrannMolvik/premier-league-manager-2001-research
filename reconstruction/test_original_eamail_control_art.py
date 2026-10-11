"""Original-game EAMail pixels/source bytes, not synthetic GUI output."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main

from ea444_header import parse_ea444_header
from original_eamail_control_art import (
    ORIGINAL_EAMAIL_ART_FOLDER,
    ORIGINAL_EAMAIL_CONTROL_ART,
    OriginalEAMailArtSourceError,
    validate_original_eamail_control_art,
)
from original_eamail_source_contract import (
    ORIGINAL_EAMAIL_GRID_RESOURCES,
    validate_original_eamail_grid_resources,
)


SOURCE_ROOT = Path(__file__).resolve().parent.parent / "original_assets" / "source"


class OriginalEAMailFullSourceArtTests(TestCase):
    def test_all_exact_four_row_strips_and_fourteen_control_assets(self):
        rows = validate_original_eamail_grid_resources(SOURCE_ROOT)
        more = validate_original_eamail_control_art(SOURCE_ROOT)
        self.assertEqual(len(rows), 4)
        self.assertEqual(len(more), 14)
        self.assertEqual(len({row.name for row in rows}), 4)
        self.assertEqual(len({item.name for item in more}), 14)
        self.assertEqual(
            next(item.dimensions for item in more
                 if item.name == "mail_reply_popup.444"), (710, 420),
        )
        self.assertEqual(
            next(item.dimensions for item in more
                 if item.name == "preview_panel.444"), (532, 187),
        )
        self.assertEqual(
            next(item.dimensions for item in more
                 if item.name == "read_mail_icon.444"), (18, 12),
        )
        self.assertEqual(
            next(item.dimensions for item in more
                 if item.name == "unread_mail_icon.444"), (18, 12),
        )
        for source in more:
            raw = (SOURCE_ROOT / ORIGINAL_EAMAIL_ART_FOLDER / source.name).read_bytes()
            self.assertEqual(len(raw), source.byte_size)
            self.assertEqual(sha256(raw).hexdigest(), source.sha256)
            header = parse_ea444_header(raw)
            self.assertEqual((header.width, header.height), source.dimensions)

    def test_missing_or_modified_original_control_art_never_substitutes(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaisesRegex(OriginalEAMailArtSourceError, "Missing"):
                validate_original_eamail_control_art(root)
            target = root / ORIGINAL_EAMAIL_ART_FOLDER
            target.mkdir(parents=True)
            original = (SOURCE_ROOT / ORIGINAL_EAMAIL_ART_FOLDER
                        / "del_mail_button.444").read_bytes()
            altered = original[:-1] + bytes((original[-1] ^ 0x01,))
            (target / "del_mail_button.444").write_bytes(altered)
            with self.assertRaisesRegex(OriginalEAMailArtSourceError, "bytes differ"):
                validate_original_eamail_control_art(root)


if __name__ == "__main__":
    main()
