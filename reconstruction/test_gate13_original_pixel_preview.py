"""Check diagnostic exports preserve original RGBA and do not invent states."""
from hashlib import sha256
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from ea444_decoder import EA444DecodedImage
from gate13_original_pixel_preview import (
    OriginalPreviewError,
    _require_private_directory,
    encode_alpha_pgm,
    encode_rgba_png,
    export_first_screen_source_pixels,
)
from original_pstartmenu_resources import (
    COMPOSED_BACKGROUND_RGBA_SHA256,
    assemble_original_pstartmenu_inputs,
    load_verified_english_pstartmenu_inputs,
)
from original_teamselect_hierarchy_art import (
    HIERARCHY_ANIM_SPEC, HIERARCHY_BARS_SPEC,
    OriginalTeamSelectHierarchyArt, split_hierarchy_source_strip,
)
from original_teamselect_resources import (
    TEAMSELECT_COMPOSED_BACKGROUND_RGBA_SHA256,
    assemble_original_teamselect_inputs,
    load_verified_original_teamselect_inputs,
)
from test_original_pstartmenu_resources import fixture as menu_fixture
from test_original_teamselect_resources import fixture as team_fixture


def read_png_rgba(path: Path) -> tuple[int, int, bytes]:
    """Decode only filter-0 RGBA PNGs written by this diagnostic encoder."""
    raw = path.read_bytes()
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise AssertionError("Not a PNG")
    pos = 8
    payload = bytearray()
    width = height = None
    while pos < len(raw):
        size = struct.unpack_from(">I", raw, pos)[0]
        kind = raw[pos + 4:pos + 8]
        data = raw[pos + 8:pos + 8 + size]
        crc = struct.unpack_from(">I", raw, pos + 8 + size)[0]
        assert crc == zlib.crc32(kind + data) & 0xFFFFFFFF
        pos += size + 12
        if kind == b"IHDR":
            width, height, depth, color, *_ = struct.unpack(">IIBBBBB", data)
            assert (depth, color) == (8, 6)
        if kind == b"IDAT":
            payload.extend(data)
        if kind == b"IEND":
            break
    assert width is not None and height is not None
    pixels = zlib.decompress(bytes(payload))
    stride = width * 4
    rows = []
    for y in range(height):
        row = pixels[y * (stride + 1):(y + 1) * (stride + 1)]
        assert row[:1] == b"\x00"
        rows.append(row[1:])
    return width, height, b"".join(rows)


def solid(w, h, color):
    return EA444DecodedImage(w, h, bytes(color) * (w * h), 0, 0)


def synthetic_resources(with_hierarchy=False):
    menu = assemble_original_pstartmenu_inputs(*menu_fixture())
    base, layer, buttons = team_fixture()
    if with_hierarchy:
        a, b = HIERARCHY_ANIM_SPEC, HIERARCHY_BARS_SPEC
        art = OriginalTeamSelectHierarchyArt(
            split_hierarchy_source_strip(
                solid(a.frame_width, a.frame_height, (41, 42, 43, 255)), a
            ),
            split_hierarchy_source_strip(
                solid(b.frame_width, b.frame_height, (51, 52, 53, 255)), b
            ),
        )
        team = assemble_original_teamselect_inputs(base, layer, buttons, art)
    else:
        team = assemble_original_teamselect_inputs(base, layer, buttons)
    return menu, team


class OriginalPixelExportTests(unittest.TestCase):
    def test_lossless_rgba_png_and_uncolored_alpha_pgm(self):
        rgba = bytes((
            3, 2, 1, 0, 12, 34, 56, 128,
            99, 150, 200, 255, 7, 8, 9, 42,
        ))
        with tempfile.TemporaryDirectory() as directory:
            png = Path(directory) / "input.png"
            png.write_bytes(encode_rgba_png(2, 2, rgba))
            self.assertEqual(read_png_rgba(png), (2, 2, rgba))
            pgm = encode_alpha_pgm(2, 1, bytes((20, 245)))
            self.assertEqual(pgm, b"P5\n2 1\n255\n\x14\xf5")
        for width, height, data in ((0, 1, b""), (2, 1, b"wrong")):
            with self.assertRaises(OriginalPreviewError):
                encode_rgba_png(width, height, data)
        with self.assertRaises(OriginalPreviewError):
            encode_alpha_pgm(2, 2, bytes((1, 2, 3)))

    def test_export_both_exact_synthetic_pixel_backgrounds_and_source_atlases(self):
        menu, team = synthetic_resources()
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "private-preview"
            manifest = export_first_screen_source_pixels(
                menu, team, out, repository_root=Path(directory) / "repo"
            )
            self.assertEqual(manifest["source_verification"], "caller-supplied-debug-data")
            self.assertIsNone(manifest["native_control_frame_states_and_screen_timing"])
            self.assertIsNone(manifest["hierarchy_art"])
            self.assertEqual(
                read_png_rgba(out / "pstartmenu_background_only.png"),
                (800, 600, menu.background_rgba),
            )
            self.assertEqual(
                read_png_rgba(out / "teamselect_background_only.png"),
                (800, 600, team.background_rgba),
            )
            originals = manifest["button_atlases"]
            self.assertEqual(len(originals["pstartmenu"]["frames"]), 23)
            self.assertEqual(len(originals["teamselect"]["frames"]), 23)
            self.assertEqual(
                read_png_rgba(
                    out / originals["pstartmenu"]["frames"][0]["file"]
                )[2],
                menu.button_atlas.frame(0).rgba,
            )
            self.assertIsNone(
                originals["pstartmenu"]["frames"][0]["native_interaction_state"]
            )
            self.assertEqual(
                [record["event"] for record in manifest["menu_controls"]],
                [1, 2, 3, 4],
            )
            label = manifest["menu_controls"][0]
            self.assertEqual(
                (out / label["uncolored_source_glyph_alpha_file"]).read_bytes(),
                encode_alpha_pgm(
                    menu.captions[0].glyph_mask.width,
                    menu.captions[0].glyph_mask.height,
                    menu.captions[0].glyph_mask.alpha,
                ),
            )
            self.assertEqual(
                json.loads((out / "source_pixel_manifest.json").read_text()),
                manifest,
            )
            with self.assertRaisesRegex(OriginalPreviewError, "new output"):
                export_first_screen_source_pixels(
                    menu, team, out, repository_root=Path(directory) / "repo"
                )

    def test_original_hierarchy_art_remains_separate_source_strip_families(self):
        menu, team = synthetic_resources(with_hierarchy=True)
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "out"
            manifest = export_first_screen_source_pixels(
                menu, team, out, repository_root=Path(directory) / "repo"
            )
            art = manifest["hierarchy_art"]
            self.assertIsNotNone(art)
            for name, strip in (
                ("animation", team.hierarchy_art.animation),
                ("bars", team.hierarchy_art.bars),
            ):
                self.assertEqual(len(art[name]["frames"]), 1)
                self.assertEqual(
                    read_png_rgba(out / art[name]["frames"][0]["file"])[2],
                    strip.source_frame(0).rgba,
                )

    def test_refuses_repository_output_to_keep_original_art_private(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            with self.assertRaisesRegex(OriginalPreviewError, "outside"):
                _require_private_directory(
                    repo / "generated" / "pixel-preview", repository_root=repo
                )
            self.assertEqual(
                _require_private_directory(
                    Path(directory) / "private-preview", repository_root=repo
                ),
                Path(directory) / "private-preview",
            )

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE") and
        os.environ.get("FM2001_ORIGINAL_444_ROOT") and
        os.environ.get("FM2001_ORIGINAL_FONT_20") and
        os.environ.get("FM2001_ORIGINAL_LANGUAGE_DIR"),
        "Canonical licensed original bytes not distributed in hosted CI",
    )
    def test_opt_in_hash_verified_real_source_background_and_frame_exports(self):
        exe = Path(os.environ["FM2001_ORIGINAL_EXE"])
        art = Path(os.environ["FM2001_ORIGINAL_444_ROOT"])
        menu = load_verified_english_pstartmenu_inputs(
            original_art_dir=art,
            original_language_dir=Path(os.environ["FM2001_ORIGINAL_LANGUAGE_DIR"]),
            original_zurich_font20=Path(os.environ["FM2001_ORIGINAL_FONT_20"]),
            original_executable=exe,
        )
        team = load_verified_original_teamselect_inputs(
            original_art_dir=art, original_executable=exe
        )
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / "source-preview"
            report = export_first_screen_source_pixels(
                menu, team, dest,
                repository_root=Path(directory) / "repo",
                source_verification="canonical-loaders-verified",
            )
            self.assertEqual(
                report["proven_rgba_backgrounds"]["pstartmenu_background_only.png"],
                COMPOSED_BACKGROUND_RGBA_SHA256,
            )
            self.assertEqual(
                report["proven_rgba_backgrounds"]["teamselect_background_only.png"],
                TEAMSELECT_COMPOSED_BACKGROUND_RGBA_SHA256,
            )


if __name__ == "__main__":
    unittest.main()
