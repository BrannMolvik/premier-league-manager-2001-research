from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import struct
import tempfile
import unittest

from ea_language_strings import parse_language_pair
from gate13_button_source_trace import OriginalPETraceError
from gate13_management_header_source_trace import (
    HEADER_ART,
    HEADER_FONT_PATH,
    _optional_data_record,
    _resource_record,
    management_header_trace_report,
)


class FakePE:
    sha256 = "a" * 64
    image_base = 0x400000

    def section_for_va(self, va):
        name = ".text" if va < 0x800000 else ".data"
        return SimpleNamespace(name=name), 0

    def bounded_window(self, va, size):
        return bytes(((va + i) & 0xFF) for i in range(size))

    def pointer_byte_candidates(self, va):
        return ({
            "candidate_va": 0x401000 + (va & 0xFF),
            "section": ".text",
            "classification": "unaligned_raw_byte_candidate_only",
        },)


class MissingEnglishGlobalPE(FakePE):
    def section_for_va(self, va):
        if va == 0x9820F4:
            raise OriginalPETraceError("not file backed")
        return super().section_for_va(va)


class Gate13ManagementHeaderSourceTraceTests(unittest.TestCase):
    def test_fixed_header_scope_is_exact_and_does_not_invent_selectors(self):
        report = management_header_trace_report(FakePE())
        self.assertEqual(report["source_sha256"], "a" * 64)
        self.assertEqual(report["known_geometry"]["compound_rect"], [599, 0, 100, 95])
        self.assertEqual(report["known_geometry"]["left_child_local_rect"], [0, 0, 30, 95])
        self.assertEqual(report["known_geometry"]["right_child_local_rect"], [30, 0, 70, 95])
        self.assertEqual(report["known_geometry"]["caption_local_rect"], [32, 62, 70, 30])
        self.assertEqual(report["known_geometry"]["caption_style"], 10)
        self.assertEqual(len(report["windows"]), 17)
        self.assertEqual(len(report["data_objects"]), 4)
        self.assertEqual(len(report["pointer_candidates"]), 7)
        labels = {item["label"] for item in report["windows"]}
        self.assertTrue({
            "PLeagueTableRow visible text setup",
            "PSquadPlayerRow visible text setup",
            "PSCFRow visible text setup",
            "shared ordinary eCText setup",
            "management font wrapper binding family",
        }.issubset(labels))
        for value in report["conclusions_intentionally_not_promoted"].values():
            self.assertIsNone(value)
        self.assertIsNone(report["resources"])

    def test_runtime_only_english_global_is_allowed_to_remain_non_file_backed(self):
        report = management_header_trace_report(MissingEnglishGlobalPE())
        english = [item for item in report["data_objects"]
                   if item["label"] == "English caption global"][0]
        self.assertFalse(english["file_backed"])
        self.assertIn("not file backed", english["reason"])

    def test_raw_descriptor_words_are_reported_without_semantic_labels(self):
        record = _optional_data_record(FakePE(), "descriptor", 0x943A90, 16)
        self.assertTrue(record["file_backed"])
        self.assertEqual(record["classification"], "raw_descriptor_or_global_bytes_only")
        expected = [
            struct.unpack("<I", bytes(((0x943A90 + offset + i) & 0xFF)
                                      for i in range(4)))[0]
            for offset in range(0, 16, 4)
        ]
        self.assertEqual(record["u32_words"], expected)

    def test_resource_identity_helper_checks_hash_and_geometry(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            path = root / "asset.444"
            raw = struct.pack("<HH", 30, 95) + b"header-proof"
            path.write_bytes(raw)
            spec = {
                "role": "synthetic",
                "source_path": "asset.444",
                "sha256": sha256(raw).hexdigest(),
                "size": (30, 95),
                "destination_rect": (599, 0, 30, 95),
            }
            record = _resource_record(root, spec)
            self.assertTrue(record["verified"])
            self.assertEqual(record["dimensions"], [30, 95])
            spec["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                _resource_record(root, spec)

    def test_caption_candidate_2497_resolves_from_proven_original_language_pair(self):
        root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        strings, index = parse_language_pair(
            (root / "English.str").read_bytes(),
            (root / "English.idx").read_bytes(),
        )
        caption = index.resolve(strings, 2497)
        print(f"GATE13_HEADER_CAPTION_ENTRY_2497={caption!r}")
        self.assertIsInstance(caption, str)
        self.assertTrue(caption)

    def test_header_assets_are_pinned_to_only_the_two_handoff_resources(self):
        self.assertEqual(
            [(item["role"], item["source_path"], item["size"]) for item in HEADER_ART],
            [
                ("left_anim",
                 "FM2001_Art/Generic/Background_buttons/back_4_anim.444",
                 (30, 4845)),
                ("right_state",
                 "FM2001_Art/Generic/Background_buttons/back_4.444",
                 (70, 380)),
            ],
        )
        self.assertEqual(HEADER_FONT_PATH, "Fonts/Zurich_XCn_BT_24pixel.fnt")


if __name__ == "__main__":
    unittest.main()