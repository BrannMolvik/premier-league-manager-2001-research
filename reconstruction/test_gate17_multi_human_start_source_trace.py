"""Synthetic tests for the private Gate-17 multi-human Start tracer."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate17_multi_human_start_source_trace import (
    Gate17MultiHumanStartTraceError,
    main as tracer_main,
    multi_human_start_trace_report,
)


def synthetic_pe() -> bytes:
    out = bytearray(0x900)
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
    struct.pack_into("<IIII", out, sections + 8, 0x600, 0x1000, 0x600, 0x200)

    # synthetic Start owner at VA 0x401020: call 0x401180; ret
    call_va = 0x401020
    target_va = 0x401180
    out[0x220] = 0xE8
    struct.pack_into("<i", out, 0x221, target_va - (call_va + 5))
    out[0x225] = 0xC3

    # raw global-address occurrence, explicitly not classified as xref
    struct.pack_into("<I", out, 0x250, 0x405000)

    # synthetic target
    out[0x380:0x384] = b"\x55\x8b\xec\xc3"
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


WINDOWS = (
    ("synthetic start", 0x401020, 0x20),
    ("synthetic continuation", 0x401180, 0x20),
)
GLOBALS = (("global_user_count", 0x405000),)
CALL_TARGETS = (("teamselect_start_continuation", 0x401180),)


class Gate17MultiHumanStartSourceTraceTests(unittest.TestCase):
    def test_report_preserves_known_source_contract_and_fail_closed_boundary(self):
        pe = parse_fixture()
        report = multi_human_start_trace_report(
            pe,
            windows=WINDOWS,
            globals_to_find=GLOBALS,
            call_targets=CALL_TARGETS,
            max_matches=8,
            with_disassembly=True,
        )

        self.assertEqual(report["source_sha256"], pe.sha256)
        self.assertEqual(report["source_contract"]["source_proven_hard_user_cap"], 6)
        self.assertTrue(
            report["source_contract"]["selection_appends_users_recovered"]
        )
        self.assertTrue(
            report["source_contract"]["start_consumes_existing_user_list_recovered"]
        )

        candidates = report["global_candidates"][0][
            "byte_occurrences_not_proven_xrefs"
        ]
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["candidate_va"], 0x401050)

        calls = report["direct_call_candidates"][0][
            "decoded_direct_calls_not_handoff_semantic_proof"
        ]
        self.assertEqual(tuple(row["callsite_va"] for row in calls), (0x401020,))
        self.assertEqual(
            calls[0]["classification"],
            "decoded_direct_call_candidate_not_lifecycle_semantic_proof",
        )

        self.assertFalse(report["ordered_multi_user_start_iteration_recovered"])
        self.assertFalse(report["shared_multi_human_runtime_owner_recovered"])
        self.assertFalse(
            report["simultaneous_human_fixture_dispatch_order_recovered"]
        )
        self.assertFalse(report["multi_human_save_serialization_recovered"])
        self.assertFalse(
            report["multi_human_save_reload_continuation_recovered"]
        )
        self.assertFalse(report["multi_human_gameplay_supported"])
        self.assertFalse(report["gate17_full_scope_ready"])
        self.assertFalse(report["gate17_complete"])

    def test_invalid_window_shape_fails_closed(self):
        with self.assertRaisesRegex(
            Gate17MultiHumanStartTraceError,
            "trace windows",
        ):
            multi_human_start_trace_report(
                parse_fixture(),
                windows=(("bad", 0x401020),),
                globals_to_find=GLOBALS,
                call_targets=CALL_TARGETS,
            )

    def test_invalid_match_bound_fails_closed(self):
        for count in (0, 4097, True):
            with self.subTest(count=count):
                with self.assertRaisesRegex(
                    Gate17MultiHumanStartTraceError,
                    "max_matches",
                ):
                    multi_human_start_trace_report(
                        parse_fixture(),
                        windows=WINDOWS,
                        globals_to_find=GLOBALS,
                        call_targets=CALL_TARGETS,
                        max_matches=count,
                    )

    def test_invalid_global_and_call_targets_fail_closed(self):
        with self.assertRaisesRegex(
            Gate17MultiHumanStartTraceError,
            "global targets",
        ):
            multi_human_start_trace_report(
                parse_fixture(),
                windows=WINDOWS,
                globals_to_find=(("bad",),),
                call_targets=CALL_TARGETS,
            )
        with self.assertRaisesRegex(
            Gate17MultiHumanStartTraceError,
            "call targets",
        ):
            multi_human_start_trace_report(
                parse_fixture(),
                windows=WINDOWS,
                globals_to_find=GLOBALS,
                call_targets=(("bad",),),
            )

    def test_cli_emits_private_neutral_trace_contract(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "multi-human-start.json"
            argv = [
                "gate17_multi_human_start_source_trace.py",
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
                    "gate17_multi_human_start_source_trace.require_private_output_path",
                    return_value=None,
                ),
                patch(
                    "gate17_multi_human_start_source_trace.multi_human_start_trace_report",
                    side_effect=lambda pe, **kwargs: multi_human_start_trace_report(
                        pe,
                        windows=WINDOWS,
                        globals_to_find=GLOBALS,
                        call_targets=CALL_TARGETS,
                        max_matches=kwargs["max_matches"],
                        with_disassembly=kwargs["with_disassembly"],
                    ),
                ),
            ):
                self.assertEqual(tracer_main(), 0)

            emitted = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(
                emitted["source_contract"]["source_proven_hard_user_cap"],
                6,
            )
            self.assertFalse(emitted["multi_human_gameplay_supported"])
            self.assertFalse(emitted["gate17_complete"])


if __name__ == "__main__":
    unittest.main()
