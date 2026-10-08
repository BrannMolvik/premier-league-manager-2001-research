"""Synthetic, asset-free regression tests for the read-only font-global leads."""
from hashlib import sha256
import struct
import unittest

from gate13_button_source_trace import OriginalPE32
from gate14_fastview_font_global_source_trace import (
    Gate14FontGlobalTraceError,
    font_global_candidate_report,
)


def _synthetic_pe() -> OriginalPE32:
    blob = bytearray(0x800)
    blob[:2] = b"MZ"
    struct.pack_into("<I", blob, 0x3C, 0x80)
    blob[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<HH", blob, 0x84, 0x14C, 2)
    struct.pack_into("<H", blob, 0x80 + 20, 0xE0)
    option = 0x80 + 24
    struct.pack_into("<H", blob, option, 0x10B)
    struct.pack_into("<I", blob, option + 28, 0x400000)
    sections = option + 0xE0
    blob[sections:sections + 8] = b".text\x00\x00\x00"
    struct.pack_into("<IIII", blob, sections + 8, 0x300, 0x1000, 0x300, 0x200)
    second = sections + 40
    blob[second:second + 8] = b".data\x00\x00\x00"
    struct.pack_into("<IIII", blob, second + 8, 0x100, 0x2000, 0x100, 0x600)
    # Two code-section raw byte candidates, plus one non-code decoy.
    struct.pack_into("<I", blob, 0x220, 0x87BEA0)
    struct.pack_into("<I", blob, 0x244, 0x87BEA0)
    struct.pack_into("<I", blob, 0x250, 0x87BE90)
    struct.pack_into("<I", blob, 0x610, 0x87BEA0)
    return OriginalPE32.parse(
        bytes(blob), expected_sha256=sha256(blob).hexdigest()
    )


class FontGlobalCandidateTraceTests(unittest.TestCase):
    def test_preserves_raw_candidate_status_and_sections(self):
        report = font_global_candidate_report(
            _synthetic_pe(),
            targets=((0, 0x87BEA0), (1, 0x87BE90)),
            callsites=(("synthetic row", 0x401024),),
            context_radius=12,
        )
        self.assertEqual(len(report["font_wrapper_raw_candidates"]), 2)
        first = report["font_wrapper_raw_candidates"][0]
        self.assertEqual(first["selector_index"], 0)
        self.assertEqual(
            tuple(x["candidate_va"] for x in first["candidates"]),
            (0x401020, 0x401044, 0x402010),
        )
        self.assertEqual(
            tuple(x["candidate_section"] for x in first["candidates"]),
            (".text", ".text", ".data"),
        )
        self.assertFalse(first["candidate_limit_reached"])
        self.assertFalse(first["reference_or_initializer_proven"])
        self.assertFalse(first["font_file_identity_proven_by_this_trace"])
        self.assertIn("a0be8700", first["candidates"][0]["context"]["raw_hex"])
        self.assertEqual(
            report["text_constructor_caller_contexts"][0]["source_known_callsite_va"],
            0x401024,
        )
        self.assertFalse(report["league_table_text_producers_resolved"])
        self.assertFalse(report["selector_zero_font_object_and_filename_resolved"])
        self.assertFalse(report["gate14_complete"])

    def test_limit_is_explicit_without_suppressing_other_targets(self):
        report = font_global_candidate_report(
            _synthetic_pe(), targets=((0, 0x87BEA0), (1, 0x87BE90)),
            callsites=(), max_candidates_per_target=2,
        )
        first, second = report["font_wrapper_raw_candidates"]
        self.assertEqual(len(first["candidates"]), 2)
        self.assertTrue(first["candidate_limit_reached"])
        self.assertEqual(len(second["candidates"]), 1)
        self.assertFalse(second["candidate_limit_reached"])

    def test_rejects_invalid_inputs_and_data_callsites(self):
        pe = _synthetic_pe()
        for kwargs in (
            {"max_candidates_per_target": 0},
            {"context_radius": -1},
            {"targets": ((0, 0x87BEA0), (0, 0x87BE90))},
            {"targets": ((5, 0x87BEA0),)},
            {"targets": ((0, -1),)},
            {"callsites": (("not code", 0x402010),)},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(Gate14FontGlobalTraceError):
                    font_global_candidate_report(pe, **kwargs)


if __name__ == "__main__":
    unittest.main()
