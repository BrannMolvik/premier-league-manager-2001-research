"""Evidence-backed tests: use the actual tiny licensed original PNG in Git.

No graphical display or recreated original graphic is needed.
"""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from original_menu_assets import (
    FRAME_COUNT,
    OriginalMenuAssetError,
    load_tk_button_frames,
    repo_source_path,
    SOURCE_SHA256,
    validate_original_menu_button_strip,
)


class FakePhoto:
    created = []

    def __init__(self, *, master=None, file=None, width=None, height=None):
        self.master = master
        self.file = file
        self.width = width
        self.height = height
        self.tk = Mock()
        self.name = f"fakephoto{len(FakePhoto.created)}"
        FakePhoto.created.append(self)

    def __str__(self):
        return self.name


class OriginalMenuAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = repo_source_path(Path(__file__).resolve().parent.parent)

    def test_actual_committed_original_asset_matches_disc_evidence(self):
        strip = validate_original_menu_button_strip(self.original)
        self.assertEqual(strip.sha256, SOURCE_SHA256)
        self.assertEqual((strip.width, strip.height), (136, 19))
        self.assertEqual(strip.frame_count, FRAME_COUNT)
        self.assertEqual(strip.frame_rectangles, (
            (0, 0, 34, 19),
            (34, 0, 68, 19),
            (68, 0, 102, 19),
            (102, 0, 136, 19),
        ))

    def test_refuses_missing_and_mutated_original_assets(self):
        with tempfile.TemporaryDirectory() as temp_name:
            path = Path(temp_name) / "original.png"
            with self.assertRaises(FileNotFoundError):
                validate_original_menu_button_strip(path)
            data = bytearray(self.original.read_bytes())
            data[-5] ^= 1
            path.write_bytes(data)
            with self.assertRaisesRegex(OriginalMenuAssetError, "checksum/size"):
                validate_original_menu_button_strip(path)

    def test_tk_adapter_copies_exact_four_original_cells_without_new_design(self):
        strip = validate_original_menu_button_strip(self.original)
        FakePhoto.created = []
        owner = object()

        frames = load_tk_button_frames(
            strip, master=owner, photo_factory=FakePhoto
        )

        self.assertEqual(len(frames.frames), 4)
        self.assertIs(frames.source, FakePhoto.created[0])
        self.assertEqual(frames.source.file, str(self.original))
        self.assertTrue(all(x.master is owner for x in FakePhoto.created))
        for cell, rect in zip(frames.frames, strip.frame_rectangles):
            self.assertEqual((cell.width, cell.height), (34, 19))
            cell.tk.call.assert_called_once_with(
                str(cell), "copy", str(frames.source),
                "-from", *rect, "-to", 0, 0,
            )


if __name__ == "__main__":
    unittest.main()
