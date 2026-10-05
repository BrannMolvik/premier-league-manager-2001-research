"""Synthetic tests for the Gate-17 sporting-objective progression tracer."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate17_sporting_objective_progression_source_trace import (
    Gate17SportingObjectiveProgressionTraceError,
    main as tracer_main,
    sporting_objective_progression_trace_report,
)


def synthetic_pe() -> bytes:
    out = bytearray(0xA00)
    out[:2] = b"MZ"
    struct.pack_into("<I", out, 0x3C, 0x80)
    out[0x80:0x84] = b"PE\x00\x00"
    struct.pack_into("<HH", out, 0x84, 0x14C, 1)
    struct.pack_into("<H", out, 0x80 + 20, 0xE0)
    option = 0x80 + 24
    struct.pack_into("<H", out, option, 0x10B)
    struct.pack_into("<I", out, option + 28, 0x400000)
    sections = option + 0xE0
    out[sections:sections + 8] = b".text\x00\x00\x00"
    struct.pack_into("<IIII", out, sections + 8, 0x700, 0x1000, 0x700, 0x200)

    # synthetic owner at 0x401020 -> 0x401180
    call_va = 0x401020
    target_va = 0x401180
    out[0x220] = 0xE8
    struct.pack_into("<i", out, 0x221, target_va - (call_va + 5))
    out[0x225] = 0xC3
    out[0x380:0x384] = b"\x55\x8b\xec\xc3"
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


WINDOWS = (
    ("synthetic annual owner", 0x401020, 0x20),
    ("synthetic sporting target", 0x401180, 0x20),
)
CALL_TARGETS = (("sporting_objective_progression", 0x401180),)


class Gate17SportingObjectiveProgressionSourceTraceTests(unittest.TestCase):
    def test_report_retains_known_source_anchors_and_stays_fail_closed(self):
        pe = parse_fixture()
        report = sporting_objective_progression_trace_report(
            pe,
            windows=WINDOWS,
            call_targets=CALL_TARGETS,
            max_matches=8,
            with_disassembly=True,
        )

        self.assertEqual(report["source_sha256"], pe.sha256)
        contract = report["source_contract"]
        self.assertEqual(contract["annual_competition_transition_va"], 0x4A8628)
        self.assertEqual(contract["sporting_objective_progress_va"], 0x5E1C00)
        self.assertEqual(contract["sporting_objective_branch_va"], 0x5E0310)
        self.assertEqual(
            contract["sporting_objective_classification_compare_va"],
            0x5E07E4,
        )
        self.assertEqual(
            contract["between_progression_passes_transition_va"],
            0x4F9010,
        )
        self.assertEqual(
            contract["annual_objective_evaluation_caller_va"],
            0x426220,
        )
        self.assertEqual(contract["annual_objective_evaluation_va"], 0x5E1D90)
        self.assertEqual(
            contract["dbruser_sacking_reason_setter_va"],
            0x42C6C0,
        )
        self.assertEqual(contract["objective_selected_id_offset"], 0x64)
        self.assertEqual(contract["objective_progression_gate_offset"], 0x68)
        self.assertEqual(contract["objective_progression_state_offset"], 0x9C)
        self.assertEqual(contract["sporting_objective_switch_case_count"], 17)
        self.assertEqual(contract["sporting_objective_pass_sequence"], [1, 0] if isinstance(contract["sporting_objective_pass_sequence"], list) else (1, 0))
        self.assertTrue(contract["same_premier_league_slice_recovered"])
        self.assertTrue(contract["annual_evaluation_year_gate_recovered"])

        calls = report["direct_call_candidates"][0][
            "decoded_direct_calls_not_sporting_progression_semantic_proof"
        ]
        self.assertEqual(tuple(row["callsite_va"] for row in calls), (0x401020,))
        self.assertEqual(
            calls[0]["classification"],
            "decoded_direct_call_candidate_not_lifecycle_semantic_proof",
        )

        self.assertFalse(report["annual_sporting_owner_chronology_recovered"])
        self.assertFalse(report["non_pl_objective_branch_table_recovered"])
        self.assertFalse(
            report["promotion_relegation_classification_semantics_recovered"]
        )
        self.assertFalse(report["non_pl_progression_gate_update_recovered"])
        self.assertFalse(report["non_pl_sporting_objective_progression_ready"])
        self.assertFalse(
            report["all_playable_scope_sporting_progression_ready"]
        )
        self.assertFalse(report["gate17_full_scope_ready"])
        self.assertFalse(report["gate17_complete"])

    def test_invalid_window_shape_fails_closed(self):
        with self.assertRaisesRegex(
            Gate17SportingObjectiveProgressionTraceError,
            "trace windows",
        ):
            sporting_objective_progression_trace_report(
                parse_fixture(),
                windows=(("bad", 0x401020),),
                call_targets=CALL_TARGETS,
            )

    def test_invalid_match_bound_fails_closed(self):
        for count in (0, 4097, True):
            with self.subTest(count=count):
                with self.assertRaisesRegex(
                    Gate17SportingObjectiveProgressionTraceError,
                    "max_matches",
                ):
                    sporting_objective_progression_trace_report(
                        parse_fixture(),
                        windows=WINDOWS,
                        call_targets=CALL_TARGETS,
                        max_matches=count,
                    )

    def test_invalid_call_target_fails_closed(self):
        with self.assertRaisesRegex(
            Gate17SportingObjectiveProgressionTraceError,
            "call targets",
        ):
            sporting_objective_progression_trace_report(
                parse_fixture(),
                windows=WINDOWS,
                call_targets=(("bad",),),
            )

    def test_cli_emits_private_neutral_trace_contract(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "sporting-objective.json"
            argv = [
                "gate17_sporting_objective_progression_source_trace.py",
                str(source),
                "--output",
                str(output),
                "--max-matches",
                "8",
            ]
            with (
                patch.object(OriginalPE32, "parse", return_value=pe),
                patch.object(sys, "argv", argv),
                patch(
                    "gate17_sporting_objective_progression_source_trace."
                    "require_private_output_path",
                    return_value=None,
                ),
                patch(
                    "gate17_sporting_objective_progression_source_trace."
                    "sporting_objective_progression_trace_report",
                    side_effect=lambda pe, **kwargs: (
                        sporting_objective_progression_trace_report(
                            pe,
                            windows=WINDOWS,
                            call_targets=CALL_TARGETS,
                            max_matches=kwargs["max_matches"],
                            with_disassembly=kwargs["with_disassembly"],
                        )
                    ),
                ),
            ):
                self.assertEqual(tracer_main(), 0)

            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(
                emitted["source_contract"]["same_premier_league_slice_recovered"]
            )
            self.assertFalse(
                emitted["non_pl_sporting_objective_progression_ready"]
            )
            self.assertFalse(emitted["gate17_complete"])


if __name__ == "__main__":
    unittest.main()
