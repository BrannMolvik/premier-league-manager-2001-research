from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ea444_decoder import EA444DecodedImage
from original_league_tables_art import (
    LEAGUE_TABLES_HEADER_RESOURCE,
    OriginalLeagueTablesArtError,
    _read_verified_header_resource,
    build_league_tables_header_art,
    load_verified_league_tables_header_art,
)
from original_league_tables_resources import LEAGUE_TABLES_BAR_RECT


REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = REPO_ROOT / "original_assets" / "source"


def image(width: int, height: int, marker: int = 7) -> EA444DecodedImage:
    return EA444DecodedImage(
        width,
        height,
        bytes((marker, marker + 1, marker + 2, 255)) * (width * height),
        consumed_bits=0,
        transparent_pixels=0,
    )


class OriginalLeagueTablesArtTests(unittest.TestCase):
    def test_imported_league_bar_matches_source_proven_size_hash_and_geometry(self):
        data = _read_verified_header_resource(SOURCE_ROOT)

        self.assertEqual(len(data), LEAGUE_TABLES_HEADER_RESOURCE.byte_size)
        self.assertEqual(LEAGUE_TABLES_HEADER_RESOURCE.size, (475, 19))
        self.assertEqual(LEAGUE_TABLES_BAR_RECT, (270, 152, 475, 19))

    def test_decoded_header_binds_only_to_exact_source_rectangle(self):
        art = build_league_tables_header_art(image(475, 19))

        self.assertEqual(art.resource_name, "league_bar")
        self.assertEqual(
            art.source_path,
            "FM2001_Art/Generic/league_tables/league_bar.444",
        )
        self.assertEqual(art.rect, (270, 152, 475, 19))
        self.assertEqual(len(art.rgba), 475 * 19 * 4)

    def test_decoded_header_geometry_and_type_fail_closed(self):
        with self.assertRaisesRegex(
            OriginalLeagueTablesArtError,
            "decoded EA444 image",
        ):
            build_league_tables_header_art(object())

        with self.assertRaisesRegex(
            OriginalLeagueTablesArtError,
            "geometry",
        ):
            build_league_tables_header_art(image(474, 19))

    def test_loader_uses_original_executable_codec_and_exact_header_resource(self):
        decoded = image(475, 19, 23)
        tables = object()
        quant = object()

        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            exe_path = root / "FOOTBAL.EXE"
            exe_path.write_bytes(b"canonical-executable-placeholder")
            with patch(
                "original_league_tables_art.tables_from_original_executable",
                return_value=tables,
            ) as table_loader, patch(
                "original_league_tables_art.quantization_from_verified_executable",
                return_value=quant,
            ) as quant_loader, patch(
                "original_league_tables_art._read_verified_header_resource",
                return_value=b"league-bar-source",
            ) as read_resource, patch(
                "original_league_tables_art.decode_ea444",
                return_value=decoded,
            ) as decoder:
                art = load_verified_league_tables_header_art(root, exe_path)

        table_loader.assert_called_once_with(b"canonical-executable-placeholder")
        quant_loader.assert_called_once_with(b"canonical-executable-placeholder")
        read_resource.assert_called_once_with(root)
        decoder.assert_called_once_with(
            b"league-bar-source",
            tables=tables,
            quant=quant,
        )
        self.assertEqual(art.rect, LEAGUE_TABLES_BAR_RECT)

    def test_loader_missing_executable_fails_before_decode(self):
        with tempfile.TemporaryDirectory() as temp_name:
            missing = Path(temp_name) / "FOOTBAL.EXE"
            with self.assertRaisesRegex(
                OriginalLeagueTablesArtError,
                "Missing original executable",
            ):
                load_verified_league_tables_header_art(
                    SOURCE_ROOT,
                    missing,
                )


if __name__ == "__main__":
    unittest.main()
