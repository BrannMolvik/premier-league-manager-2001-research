"""Static original Resource.res directory checks; not a runtime image alias."""
import os
from pathlib import Path
import unittest

from original_resource_res_index import (
    OriginalResourceResIndexError, original_resource_res_entries,
    ORIGINAL_RESOURCE_RES_DIRECTORY_COUNT,
)


class OriginalResourceResIndexTests(unittest.TestCase):
    def test_absent_or_mutated_bytes_are_not_original(self):
        for raw in (None, b"", b"Resource.res", bytearray(b"\x00")):
            with self.subTest(raw=raw), self.assertRaises(OriginalResourceResIndexError):
                original_resource_res_entries(raw)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_RESOURCE_RES"),
                         "Original private Resource.res not mounted")
    def test_original_pack_has_28_entries_and_no_inbox_sprite_alias(self):
        raw = Path(os.environ["FM2001_ORIGINAL_RESOURCE_RES"]).read_bytes()
        entries = original_resource_res_entries(raw)
        names = tuple(x.name for x in entries)
        self.assertEqual(len(names), ORIGINAL_RESOURCE_RES_DIRECTORY_COUNT)
        self.assertEqual(names[0], "PLAYER4.MSH")
        self.assertEqual(names[-1], "FONT16X16.BMP")
        self.assertEqual(names.count("PLAYER0.FMP"), 1)
        self.assertIn("WWW SELECTED.BMP", names)
        self.assertIn("KIT.MSH", names)
        self.assertFalse(any(name.lower().endswith(".444") for name in names))
        self.assertNotIn("boost_type_11.444", (s.lower() for s in names))
        self.assertNotIn("button_type_11.444", (s.lower() for s in names))
        self.assertEqual(entries[-1].data_offset + entries[-1].data_length,
                         0x20411A)


if __name__ == "__main__":
    unittest.main()
