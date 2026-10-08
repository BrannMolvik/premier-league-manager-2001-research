"""Synthetic, asset-free regression tests for the read-only font-global leads."""
from hashlib import sha256
import struct
import unittest

from gate13_button_source_trace import OriginalPE32
from gate14_fastview_font_global_source_trace import (
    Gate14FontGlobalTraceError,
    font_global_candidate_report,
    linear_font_wrapper_instruction_candidates,
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


def _synthetic_instruction_pe() -> OriginalPE32:
    """Aligned NOP-coded section with literal and indexed pointer decoys."""
    blob = bytearray(_synthetic_pe().data)
    blob[0x200:0x500] = b"\\x90" * 0x300
    # mov eax,[0x87BEA0] => literal absolute memory operand.
    blob[0x230:0x235] = b"\\xA1" + struct.pack("<I", 0x87BEA0)
    # push 0x87BE90 => immediate pointer operand.
    blob[0x250:0x255] = b"\\x68" + struct.pack("<I", 0x87BE90)
    # mov eax,[eax+0x87BEA0] => displacement is NOT absolute.
    blob[0x270:0x276] = b"\\x8B\\x80" + struct.pack("<I", 0x87BEA0)
    # A second valid absolute reference, to test explicit truncation.
    blob[0x290:0x295] = b"\\xA1" + struct.pack("<I", 0x87BEA0)
    # Existing .data literal at 0x402010 remains a raw-only decoy.
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

    def test_opt_in_decoded_leads_exclude_register_displacements_and_data(self):
        pe = _synthetic_instruction_pe()
        targets = ((0, 0x87BEA0), (1, 0x87BE90))
        report = font_global_candidate_report(
            pe, targets=targets, callsites=(),
            scan_linear_wrapper_candidates=True,
        )
        first, second = report["linear_font_wrapper_candidates_not_xrefs"]
        self.assertEqual(
            tuple(x["candidate_instruction_va"] for x in first["candidates"]),
            (0x401030, 0x401090),
        )
        self.assertEqual(
            tuple(x["candidate_instruction_va"] for x in second["candidates"]),
            (0x401050,),
        )
        self.assertEqual(
            tuple(x["operand_kind"] for x in first["candidates"]),
            ("register_free_absolute_memory", "register_free_absolute_memory"),
        )
        self.assertEqual(second["candidates"][0]["operand_kind"], "literal_immediate")
        self.assertFalse(first["verified_xref_or_initializer"])
        self.assertTrue(all(
            x["classification"] ==
            "linear_decoded_candidate_not_verified_xref_or_write"
            for x in first["candidates"] + second["candidates"]
        ))
        self.assertFalse(report["selector_zero_font_object_and_filename_resolved"])
        self.assertFalse(report["league_table_text_producers_resolved"])
        self.assertFalse(report["gate14_complete"])

        default_report = font_global_candidate_report(
            pe, targets=targets, callsites=()
        )
        self.assertIsNone(default_report["linear_font_wrapper_candidates_not_xrefs"])
        limited = linear_font_wrapper_instruction_candidates(
            pe, targets=targets, max_candidates_per_target=1,
        )
        self.assertEqual(len(limited[0]["candidates"]), 1)
        self.assertTrue(limited[0]["candidate_limit_reached"])
        self.assertFalse(limited[1]["candidate_limit_reached"])

    def test_linear_candidate_bad_inputs_fail_closed(self):
        pe = _synthetic_instruction_pe()
        for args in (
            {"max_candidates_per_target": 0},
            {"max_candidates_per_target": True},
            {"targets": ((0, 0x87BEA0), (0, 0x87BE90))},
            {"targets": ((0, 0x87BEA0), (1, 0x87BEA0))},
            {"targets": ((6, 0x87BEA0),)},
            {"targets": ((0, -1),)},
        ):
            with self.subTest(args=args):
                with self.assertRaises(Gate14FontGlobalTraceError):
                    linear_font_wrapper_instruction_candidates(pe, **args)
        with self.assertRaises(Gate14FontGlobalTraceError):
            font_global_candidate_report(
                pe, targets=(), callsites=(),
                scan_linear_wrapper_candidates=1,
            )

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
