"""Candidate-only static byte/vtable inspection tests; not native state proof."""
from hashlib import sha256
from importlib.util import find_spec
import struct
import unittest

from gate13_button_source_trace import OriginalPE32, OriginalPETraceError
from gate13_button_vtable_xref_candidates import (
    SCREEN_VTABLE_SEEDS, SOURCE_CODE_SEEDS,
    extended_button_candidate_report,
    linear_direct_branch_candidates,
    screen_vtable_candidates,
)
from test_gate13_button_source_trace import synthetic_pe


def source_style_fixture() -> OriginalPE32:
    # Reuse the existing structurally verified synthetic PE32 fixture, then
    # install 1-byte NOPs to keep linear decoding aligned with test branches.
    fake = bytearray(synthetic_pe())
    fake[0x200:0x290] = b"\x90" * 0x90
    # Two synthetic, independently chosen .text function targets.
    struct.pack_into("<III", fake, 0x2A0, 0x401040, 0x401050, 0)
    # Direct CALL at 0x401020 to 0x401040.
    fake[0x220:0x225] = b"\xE8" + struct.pack("<i", 0x401040 - (0x401020 + 5))
    # Direct JMP at 0x401030 to 0x401050.
    fake[0x230:0x235] = b"\xE9" + struct.pack("<i", 0x401050 - (0x401030 + 5))
    return OriginalPE32.parse(fake, expected_sha256=sha256(fake).hexdigest())


class ClassVTableCandidateTests(unittest.TestCase):
    def test_original_source_seeds_are_existing_evidence_not_slot_semantics(self):
        self.assertEqual(
            SCREEN_VTABLE_SEEDS,
            (("PStartMenu class vtable", 0x7C64E0),
             ("TeamSelect class vtable", 0x7C7650)),
        )
        self.assertIn(("Button@ease setup", 0x652FD0), SOURCE_CODE_SEEDS)
        self.assertIn(("Zurich bitmap font loader", 0x657650), SOURCE_CODE_SEEDS)

    def test_bounds_code_pointer_classification_and_unmapped_slots(self):
        pe = source_style_fixture()
        slots = screen_vtable_candidates(
            pe, seeds=(("synthetic original-style class", 0x402000),),
            entries_per_seed=3,
        )
        self.assertEqual([s.entry_va for s in slots],
                         [0x402000, 0x402004, 0x402008])
        self.assertEqual([s.value for s in slots],
                         [0x401040, 0x401050, 0])
        self.assertEqual(
            [s.plausible_text_pointer for s in slots],
            [True, True, False],
        )
        self.assertEqual([s.mapped_section for s in slots],
                         [".text", ".text", None])
        # .rdata virtual size is 0x20; don't blindly scan beyond its end.
        bounded = screen_vtable_candidates(
            pe, seeds=(("near section boundary", 0x40201C),),
            entries_per_seed=64,
        )
        self.assertEqual(len(bounded), 1)
        for count in (0, 65, True, 1.5):
            with self.subTest(count=count):
                with self.assertRaises(OriginalPETraceError):
                    screen_vtable_candidates(
                        pe, seeds=(("candidate", 0x402000),),
                        entries_per_seed=count,
                    )
        with self.assertRaisesRegex(OriginalPETraceError, "maps to code"):
            screen_vtable_candidates(
                pe, seeds=(("not actual data vtable", 0x401000),),
            )

    def test_extended_report_does_not_promote_screen_vtables_to_shared_button(self):
        report = extended_button_candidate_report(
            source_style_fixture(),
            vtable_seeds=(("synthetic class table", 0x402000),),
            code_seeds=(("synthetic constructor", 0x401020),),
            entries_per_seed=3,
        )
        self.assertEqual(len(report["raw_vtable_slots"]), 3)
        self.assertIsNone(report["linear_direct_branch_candidates"])
        self.assertIn("unconfirmed", report["evidence_limit"].lower())
        self.assertIn("indirect", report["evidence_limit"])

    @unittest.skipUnless(find_spec("capstone"), "Capstone optional outside focused CI")
    def test_bounded_direct_call_and_jump_leads_are_not_claimed_as_real_xrefs(self):
        pe = source_style_fixture()
        targets = (
            ("candidate draw path", 0x401040),
            ("candidate update path", 0x401050),
        )
        edges = linear_direct_branch_candidates(pe, targets=targets)
        self.assertEqual(
            [(x["candidate_instruction_va"], x["candidate_target_va"])
             for x in edges],
            [(0x401020, 0x401040), (0x401030, 0x401050)],
        )
        self.assertTrue(all(
            x["classification"] == "linear_disassembly_only_unconfirmed_code_edge"
            for x in edges
        ))
        self.assertEqual(
            len(linear_direct_branch_candidates(
                pe, targets=targets, max_candidates=1,
            )), 1,
        )
        report = extended_button_candidate_report(
            pe,
            vtable_seeds=(("synthetic class vtable", 0x402000),),
            code_seeds=(("synthetic constructor", 0x401020),),
            entries_per_seed=3,
            search_direct_branches=True,
        )
        self.assertEqual(
            {x["candidate_target_va"] for x in report["linear_direct_branch_candidates"]},
            {0x401040, 0x401050},
        )
        self.assertIn(
            "synthetic class vtable sequential slot 0 candidate",
            report["linear_direct_branch_candidates"][0]["candidate_target_labels"],
        )
        for count in (0, True, 1.2):
            with self.subTest(count=count):
                with self.assertRaises(OriginalPETraceError):
                    linear_direct_branch_candidates(
                        pe, targets=targets, max_candidates=count,
                    )

if __name__ == "__main__":
    unittest.main()
