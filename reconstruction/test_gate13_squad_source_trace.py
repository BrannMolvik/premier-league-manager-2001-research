"""Synthetic tests for the fail-closed Gate 13 Squad source trace."""
from hashlib import sha256
import os
from pathlib import Path
import unittest

from ea444_tables import CANONICAL_EXE_SHA256
from gate13_button_source_trace import OriginalPE32
from gate13_squad_source_trace import (
    SQUAD_TRACE_WINDOWS,
    SQUAD_VTABLE_SEEDS,
    squad_trace_report,
)
from original_squad_resources import (
    CBASE_PLAYER_LIST_VFTABLE_VA,
    FORMATION_TEXT_BAR_SETUP_VA,
    FORMATION_TEXT_FORM_SETUP_VA,
    FORMATION_TEXT_VFTABLE_VA,
    SQUAD_PITCH_SETUP_VA,
    SQUAD_PITCH_VFTABLE_VA,
    SQUAD_SCREEN_EVENT_HANDLER_VA,
    SQUAD_SCREEN_SETUP_VA,
    SQUAD_SCREEN_VFTABLE_VA,
)
from test_gate13_button_source_trace import synthetic_pe


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


class Gate13SquadSourceTraceTests(unittest.TestCase):
    def test_trace_is_pinned_only_to_already_proven_squad_anchors(self):
        self.assertEqual(
            SQUAD_VTABLE_SEEDS,
            (
                ("CBasePlayerList class vtable", CBASE_PLAYER_LIST_VFTABLE_VA),
                ("FormationText class vtable", FORMATION_TEXT_VFTABLE_VA),
                ("PSquadPitch class vtable", SQUAD_PITCH_VFTABLE_VA),
                ("PSquadScreen class vtable", SQUAD_SCREEN_VFTABLE_VA),
            ),
        )
        self.assertEqual(
            tuple(va for _, va, _ in SQUAD_TRACE_WINDOWS),
            (
                SQUAD_PITCH_SETUP_VA,
                FORMATION_TEXT_BAR_SETUP_VA,
                FORMATION_TEXT_FORM_SETUP_VA,
                SQUAD_SCREEN_SETUP_VA,
                SQUAD_SCREEN_EVENT_HANDLER_VA,
            ),
        )
        self.assertEqual(CBASE_PLAYER_LIST_VFTABLE_VA, 0x7C5BC8)
        self.assertEqual(FORMATION_TEXT_VFTABLE_VA, 0x7C5700)
        self.assertEqual(SQUAD_PITCH_VFTABLE_VA, 0x7C54A8)
        self.assertEqual(SQUAD_SCREEN_VFTABLE_VA, 0x7C5CA4)

    def test_synthetic_report_marks_vtable_values_as_candidates_only(self):
        report = squad_trace_report(
            parse_fixture(),
            windows=(("synthetic bounded code", 0x401000, 7),),
            vtable_seeds=(("synthetic class vtable", 0x402000),),
            entries_per_vtable=3,
        )
        self.assertEqual(report["windows"][0]["raw_hex"], "558becb8010000")
        self.assertEqual(len(report["raw_vtable_slots"]), 3)
        self.assertIsNone(report["linear_direct_branch_candidates"])
        self.assertIn("require manual", report["evidence_limit"].lower())
        self.assertNotIn("verified_frame", report)
        self.assertNotIn("column_meanings", report)

    def test_optional_disassembly_still_does_not_promote_semantics(self):
        report = squad_trace_report(
            parse_fixture(),
            with_disassembly=True,
            windows=(("synthetic bounded code", 0x401000, 7),),
            vtable_seeds=(("synthetic class vtable", 0x402000),),
            entries_per_vtable=2,
        )
        self.assertIsInstance(report["windows"][0]["linear_disassembly_only"], list)
        self.assertEqual(report["linear_direct_branch_candidates"], [])
        self.assertIn("state-to-frame", report["evidence_limit"])

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE"),
        "Licensed original executable intentionally not bundled in hosted CI",
    )
    def test_opt_in_canonical_executable_accepts_all_proven_squad_anchors(self):
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        report = squad_trace_report(pe, with_disassembly=False)
        self.assertEqual(report["source_sha256"], CANONICAL_EXE_SHA256)
        self.assertEqual(
            [item["seed_va"] for item in report["seed_vtables"]],
            [va for _, va in SQUAD_VTABLE_SEEDS],
        )
        self.assertTrue(report["raw_vtable_slots"])


if __name__ == "__main__":
    unittest.main()
