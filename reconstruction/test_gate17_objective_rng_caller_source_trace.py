"""Synthetic tests for the Gate-17 objective RNG caller source tracer."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate17_objective_rng_caller_source_trace import (
    Gate17ObjectiveRngCallerTraceError,
    main as tracer_main,
    objective_rng_caller_trace_report,
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

    # synthetic caller at 0x401020 -> 0x401180
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
    ("synthetic objective setup", 0x401020, 0x20),
    ("synthetic objective generator", 0x401180, 0x20),
)
CALL_TARGETS = (("fresh_objective_generator", 0x401180),)


class Gate17ObjectiveRngCallerSourceTraceTests(unittest.TestCase):
    def test_report_keeps_rng_caller_state_fail_closed(self):
        pe = parse_fixture()
        report = objective_rng_caller_trace_report(
            pe,
            windows=WINDOWS,
            call_targets=CALL_TARGETS,
            max_matches=8,
            with_disassembly=True,
        )

        self.assertEqual(report["source_sha256"], pe.sha256)
        contract = report["source_contract"]
        self.assertEqual(contract["dbruser_constructor_va"], 0x425680)
        self.assertEqual(contract["objective_setup_va"], 0x5DF670)
        self.assertEqual(contract["fresh_objective_generator_va"], 0x5DFD30)
        self.assertEqual(contract["shared_crt_bounded_rng_va"], 0x64D540)
        self.assertEqual(contract["hierarchy_class_helper_va"], 0x4FA520)
        self.assertEqual(contract["first_class_helper_va"], 0x4FA570)
        self.assertEqual(contract["last_class_equal_helper_va"], 0x4FA590)
        self.assertEqual(contract["promotion_playoff_status_helper_va"], 0x4F88C0)
        self.assertEqual(contract["objective_rng_bound"], 100)
        self.assertEqual(contract["objective_rng_lower_branch_max_inclusive"], 50)
        self.assertEqual(contract["objective_setup_slot_count"], 3)
        self.assertTrue(contract["fresh_branch_table_recovered"])
        self.assertTrue(contract["deterministic_non_pl_branches_materializable"])
        self.assertTrue(contract["rng_bearing_branches_require_shared_crt_state"])

        calls = report["direct_call_candidates"][0][
            "decoded_direct_calls_not_objective_rng_semantic_proof"
        ]
        self.assertEqual(tuple(row["callsite_va"] for row in calls), (0x401020,))
        self.assertEqual(
            calls[0]["classification"],
            "decoded_direct_call_candidate_not_lifecycle_semantic_proof",
        )

        self.assertFalse(report["objective_setup_callers_classified"])
        self.assertFalse(report["objective_setup_entry_crt_state_recovered"])
        self.assertFalse(report["rng_bearing_branch_draw_position_recovered"])
        self.assertFalse(report["fresh_objective_rng_replay_ready"])
        self.assertFalse(report["all_playable_scope_fresh_objectives_ready"])
        self.assertFalse(report["gate17_full_scope_ready"])
        self.assertFalse(report["gate17_complete"])

    def test_invalid_window_shape_fails_closed(self):
        with self.assertRaisesRegex(
            Gate17ObjectiveRngCallerTraceError,
            "trace windows",
        ):
            objective_rng_caller_trace_report(
                parse_fixture(),
                windows=(("bad", 0x401020),),
                call_targets=CALL_TARGETS,
            )

    def test_invalid_match_bound_fails_closed(self):
        for count in (0, 4097, True):
            with self.subTest(count=count):
                with self.assertRaisesRegex(
                    Gate17ObjectiveRngCallerTraceError,
                    "max_matches",
                ):
                    objective_rng_caller_trace_report(
                        parse_fixture(),
                        windows=WINDOWS,
                        call_targets=CALL_TARGETS,
                        max_matches=count,
                    )

    def test_invalid_call_target_fails_closed(self):
        with self.assertRaisesRegex(
            Gate17ObjectiveRngCallerTraceError,
            "call targets",
        ):
            objective_rng_caller_trace_report(
                parse_fixture(),
                windows=WINDOWS,
                call_targets=(("bad",),),
            )

    def test_cli_emits_private_neutral_trace_contract(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "objective-rng.json"
            argv = [
                "gate17_objective_rng_caller_source_trace.py",
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
                    "gate17_objective_rng_caller_source_trace.require_private_output_path",
                    return_value=None,
                ),
                patch(
                    "gate17_objective_rng_caller_source_trace.objective_rng_caller_trace_report",
                    side_effect=lambda pe, **kwargs: objective_rng_caller_trace_report(
                        pe,
                        windows=WINDOWS,
                        call_targets=CALL_TARGETS,
                        max_matches=kwargs["max_matches"],
                        with_disassembly=kwargs["with_disassembly"],
                    ),
                ),
            ):
                self.assertEqual(tracer_main(), 0)

            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(emitted["source_contract"]["fresh_branch_table_recovered"])
            self.assertFalse(emitted["fresh_objective_rng_replay_ready"])
            self.assertFalse(emitted["gate17_complete"])


if __name__ == "__main__":
    unittest.main()
