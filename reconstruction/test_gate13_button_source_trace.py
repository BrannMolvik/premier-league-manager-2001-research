"""Synthetic PE32 boundary tests and opt-in canonical Button source inspection.

Hosted CI intentionally never bundles or downloads the original executable.
"""
from hashlib import sha256
from importlib.util import find_spec
import os
from pathlib import Path
import tempfile
import struct
import unittest

from ea444_tables import CANONICAL_EXE_SHA256
from gate13_button_source_trace import (
    CANDIDATE_GLOBAL_TARGETS,
    KNOWN_BUTTON_WINDOWS,
    OriginalPE32,
    OriginalPETraceError,
    button_trace_report,
    disassemble_window,
    require_private_output_path,
)


def synthetic_pe() -> bytes:
    out = bytearray(0x300)
    out[:2] = b"MZ"
    struct.pack_into("<I", out, 0x3C, 0x80)
    out[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<HH", out, 0x84, 0x14C, 2)
    struct.pack_into("<H", out, 0x80 + 20, 0xE0)
    option = 0x80 + 24
    struct.pack_into("<H", out, option, 0x10B)
    struct.pack_into("<I", out, option + 28, 0x400000)
    sections = option + 0xE0
    out[sections:sections + 8] = b".text\x00\x00\x00"
    struct.pack_into("<IIII", out, sections + 8, 0x90, 0x1000, 0xA0, 0x200)
    second = sections + 40
    out[second:second + 8] = b".rdata\x00\x00"
    struct.pack_into("<IIII", out, second + 8, 0x20, 0x2000, 0x40, 0x2A0)
    # Exact mapped code-window start and a raw byte-occurrence candidate.
    out[0x200:0x207] = b"\x55\x8b\xec\xb8\x01\x00\x00"
    struct.pack_into("<I", out, 0x200 + 0x40, 0x946590)
    struct.pack_into("<I", out, 0x2A0 + 0x04, 0x946590)
    return bytes(out)


def parse_fixture(data: bytes | None = None) -> OriginalPE32:
    raw = synthetic_pe() if data is None else data
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


class CanonicalButtonTraceTests(unittest.TestCase):
    def test_pin_existing_exact_code_windows_without_claiming_frame_states(self):
        self.assertEqual(
            tuple(va for _, va, _ in KNOWN_BUTTON_WINDOWS),
            (
                0x4C1BA0, 0x4C3770, 0x4D885F, 0x5F4500, 0x652FD0,
                0x657650, 0x64F380, 0x64F3C0, 0x64F3E0, 0x64F510,
                0x64F520, 0x64F710, 0x64F750, 0x64F7A0, 0x4DA480,
                0x5CFA50,
            ),
        )
        self.assertIn(("PStartMenu button atlas global", 0x946590),
                      CANDIDATE_GLOBAL_TARGETS)
        self.assertIn(("Common button font global", 0x9197E0),
                      CANDIDATE_GLOBAL_TARGETS)
        self.assertEqual(
            CANONICAL_EXE_SHA256,
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"
        )

    def test_pe32_virtual_to_file_address_and_section_boundaries(self):
        pe = parse_fixture()
        self.assertEqual(pe.image_base, 0x400000)
        self.assertEqual([s.name for s in pe.sections], [".text", ".rdata"])
        self.assertEqual(pe.read(0x401000, 7), b"\x55\x8b\xec\xb8\x01\x00\x00")
        self.assertEqual(pe.read(0x402004, 4), struct.pack("<I", 0x946590))
        self.assertEqual(pe.section_for_va(0x402004)[0].name, ".rdata")
        self.assertEqual(pe.bounded_window(0x40108E, 50), b"\x00\x00")
        with self.assertRaisesRegex(OriginalPETraceError, "boundary"):
            pe.read(0x40108F, 2)
        for va in (0x400000, 0x401090, 0x402020, 0xFFFFFFFF):
            with self.subTest(va=va):
                with self.assertRaises(OriginalPETraceError):
                    pe.read(va, 4)

    def test_pointer_hits_are_marked_raw_candidates_not_proven_xrefs(self):
        pe = parse_fixture()
        references = pe.pointer_byte_candidates(0x946590)
        self.assertEqual(
            [(x["candidate_va"], x["section"]) for x in references],
            [(0x401040, ".text"), (0x402004, ".rdata")],
        )
        self.assertTrue(all("candidate" in x["classification"] for x in references))
        self.assertEqual(len(pe.pointer_byte_candidates(0x946590, max_matches=1)), 1)

    def test_source_window_report_is_reproducible_and_explicitly_bounded(self):
        pe = parse_fixture()
        report = button_trace_report(
            pe, windows=(("synthetic prologue", 0x401000, 7),),
            globals_to_find=(("test atlas global", 0x946590),),
        )
        self.assertEqual(report["source_sha256"], sha256(synthetic_pe()).hexdigest())
        self.assertEqual(report["windows"][0]["raw_hex"], "558becb8010000")
        self.assertEqual(report["windows"][0]["window_bytes"], 7)
        self.assertIsNone(report["windows"][0]["linear_disassembly_only"])
        self.assertEqual(
            len(report["global_candidates"][0]["byte_occurrences_not_proven_xrefs"]), 2
        )
        self.assertIn("Manual CFG", report["evidence_limit"])
        with self.assertRaisesRegex(OriginalPETraceError, "expected"):
            button_trace_report(
                pe, windows=(("invalid data target", 0x402000, 3),),
                globals_to_find=(),
            )

    def test_rejects_other_executables_or_malformed_pe(self):
        source = synthetic_pe()
        with self.assertRaisesRegex(OriginalPETraceError, "expected original"):
            OriginalPE32.parse(source)
        corrupted = bytearray(source)
        corrupted[:2] = b"NO"
        with self.assertRaisesRegex(OriginalPETraceError, "MZ"):
            parse_fixture(bytes(corrupted))
        corrupted = bytearray(source)
        struct.pack_into("<H", corrupted, 0x84, 0x8664)
        with self.assertRaisesRegex(OriginalPETraceError, "i386"):
            parse_fixture(bytes(corrupted))
        corrupted = bytearray(source)
        struct.pack_into("<I", corrupted, 0x178 + 20, 0xFFFF)
        with self.assertRaisesRegex(OriginalPETraceError, "section"):
            parse_fixture(bytes(corrupted))

    def test_disassembly_report_must_remain_outside_tracked_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            with self.assertRaisesRegex(OriginalPETraceError, "outside"):
                require_private_output_path(
                    root / "research/private-trace.json", repository_root=root
                )
            require_private_output_path(
                Path(directory) / "private-result.json", repository_root=root
            )

    @unittest.skipUnless(find_spec("capstone"), "Capstone optional in hosted CI")
    def test_optional_linear_x86_instruction_list(self):
        lines = disassemble_window(b"\x90\xc3", 0x401000)
        self.assertEqual(
            [(x["va"], x["mnemonic"]) for x in lines],
            [(0x401000, "nop"), (0x401001, "ret")],
        )

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE"),
        "Original licensed executable intentionally not bundled in CI",
    )
    def test_opt_in_original_source_exact_windows_and_raw_pointer_candidates(self):
        pe = OriginalPE32.parse(
            Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes()
        )
        self.assertEqual(pe.sha256, CANONICAL_EXE_SHA256)
        report = button_trace_report(pe, with_disassembly=False)
        self.assertEqual(len(report["windows"]), len(KNOWN_BUTTON_WINDOWS))
        self.assertTrue(all(x["section"] == ".text" for x in report["windows"]))
        self.assertEqual(
            [x["target_va"] for x in report["global_candidates"]],
            [va for _, va in CANDIDATE_GLOBAL_TARGETS],
        )


if __name__ == "__main__":
    unittest.main()
