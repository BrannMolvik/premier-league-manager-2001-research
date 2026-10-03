"""Tests for verified-source FastView chrome loading."""
from pathlib import Path
import tempfile
import unittest

from ea444_decoder import EA444DecodedImage
from gate14_fastview_chrome import FASTVIEW_DIRECT_CHROME_RESOURCES, TOP_BAR
from original_fastview_chrome_art import (
    OriginalFastViewChromeArtError,
    _read_verified_fastview_chrome_resource,
    build_fastview_chrome_art,
    load_verified_fastview_chrome_art_from_source,
)


def image(width, height, value):
    return EA444DecodedImage(
        width=width,
        height=height,
        rgba=bytes([value]) * (width * height * 4),
        consumed_bits=0,
        transparent_pixels=0,
    )


class OriginalFastViewChromeSourceTests(unittest.TestCase):
    def test_existing_builder_preserves_exact_two_source_placements(self):
        decoded = {
            resource.name: image(*resource.size, index + 1)
            for index, resource in enumerate(FASTVIEW_DIRECT_CHROME_RESOURCES)
        }
        art = build_fastview_chrome_art(decoded)
        self.assertEqual(
            tuple(
                (item.resource_name, item.source_path, item.rect)
                for item in art.placements
            ),
            tuple(
                (resource.name, resource.source_path, resource.rect)
                for resource in FASTVIEW_DIRECT_CHROME_RESOURCES
            ),
        )

    def test_source_reader_fails_closed_on_missing_size_and_checksum(self):
        resource = TOP_BAR
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / resource.source_path
            path.parent.mkdir(parents=True, exist_ok=True)

            with self.assertRaisesRegex(
                OriginalFastViewChromeArtError,
                "Missing original FastView chrome",
            ):
                _read_verified_fastview_chrome_resource(root, resource)

            path.write_bytes(b"x")
            with self.assertRaisesRegex(
                OriginalFastViewChromeArtError,
                "byte-size mismatch",
            ):
                _read_verified_fastview_chrome_resource(root, resource)

            path.write_bytes(b"x" * resource.byte_size)
            with self.assertRaisesRegex(
                OriginalFastViewChromeArtError,
                "checksum mismatch",
            ):
                _read_verified_fastview_chrome_resource(root, resource)

    def test_loader_requires_canonical_executable_before_decode(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            missing_exe = root / "FOOTBAL.EXE"
            with self.assertRaisesRegex(
                OriginalFastViewChromeArtError,
                "Missing canonical original executable",
            ):
                load_verified_fastview_chrome_art_from_source(root, missing_exe)

    def test_source_family_remains_only_direct_picturecontrol_chrome(self):
        self.assertEqual(
            tuple(resource.name for resource in FASTVIEW_DIRECT_CHROME_RESOURCES),
            ("top_bar", "ticker"),
        )
        self.assertEqual(
            tuple(resource.rect for resource in FASTVIEW_DIRECT_CHROME_RESOURCES),
            ((0, 0, 800, 95), (0, 557, 800, 590)),
        )
        self.assertEqual(
            tuple(resource.size for resource in FASTVIEW_DIRECT_CHROME_RESOURCES),
            ((800, 95), (800, 33)),
        )


if __name__ == "__main__":
    unittest.main()
