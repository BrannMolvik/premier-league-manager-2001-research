"""Synthetic tests for the private Gate-17 secondary-owner source tracer."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate17_secondary_owner_source_trace import (
    Gate17SecondaryOwnerTraceError,
    decoded_direct_call_candidates,
    main as tracer_main,
    secondary_owner_trace_report,
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

    # synthetic owner at VA 0x401020: call 0x401180; ret
    off = 0x220
    call_va = 0x401020
    target_va = 0x401180
    out[off] = 0xE8
    struct.pack_into("<i", out, off + 1, target_va - (call_va + 5))
    out[off + 5] = 0xC3

    # Raw little-endian global-address occurrence, deliberately not classified
    # as an xref by the tracer.
    struct.pack_into("<I", out, 0x250, 0x405000)

    # synthetic target bytes.
    out[0x380:0x384] = b"\x55\x8b\xec\xc3"
    return bytes(out)


def parse_fixture() -> OriginalPE32:
    raw = synthetic_pe()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


WINDOWS = (
    ("synthetic selector", 0x401020, 0x20),
    ("synthetic target", 0x401180, 0x20),
)
GLOBALS = (("synthetic secondary global", 0x405000),)
CALL_TARGETS = (("synthetic lifecycle target", 0x401180),)


class Gate17SecondaryOwnerSourceTraceTests(unittest.TestCase):
    def test_decoded_direct_calls_do_not_promote_lifecycle_semantics(self):
        rows = decoded_direct_call_candidates(
            parse_fixture(),
            0x401180,
            max_matches=8,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["callsite_va"], 0x401020)
        self.assertEqual(rows[0]["target_va"], 0x401180)
        self.assertEqual(
            rows[0]["classification"],
            "decoded_direct_call_candidate_not_lifecycle_semantic_proof",
        )

    def test_report_retains_raw_global_candidate_and_fail_closed_capability(self):
        pe = parse_fixture()
        report = secondary_owner_trace_report(
            pe,
            windows=WINDOWS,
            globals_to_find=GLOBALS,
            call_targets=CALL_TARGETS,
            max_matches=8,
            with_disassembly=True,
        )
        self.assertEqual(report["source_sha256"], pe.sha256)
        self.assertEqual(len(report["windows"]), 2)
        self.assertEqual(len(report["global_candidates"]), 1)
        candidates = report["global_candidates"][0][
            "byte_occurrences_not_proven_xrefs"
        ]
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["candidate_va"], 0x401050)
        calls = report["direct_call_candidates"][0][
            "decoded_direct_calls_not_lifecycle_semantic_proof"
        ]
        self.assertEqual(tuple(row["callsite_va"] for row in calls), (0x401020,))

        self.assertTrue(report["secondary_startup_container_identity_recovered"])
        self.assertTrue(report["secondary_match_insertion_routing_recovered"])
        self.assertFalse(report["live_secondary_runtime_owner_recovered"])
        self.assertFalse(report["live_secondary_daily_execution_binding_recovered"])
        self.assertFalse(report["secondary_season_continuation_recovered"])
        self.assertFalse(report["secondary_human_match_dispatch_recovered"])
        self.assertFalse(report["secondary_save_serialization_recovered"])
        self.assertFalse(report["secondary_save_reload_continuation_recovered"])
        self.assertFalse(report["procedural_secondary_scope_playable"])
        self.assertFalse(report["gate17_full_scope_ready"])
        self.assertFalse(report["gate17_complete"])
        self.assertIn("do not prove ordinary daily execution", report["evidence_limit"])

    def test_invalid_direct_call_scan_arguments_fail_closed(self):
        pe = parse_fixture()
        for target in (-1, 1 << 32, True):
            with self.subTest(target=target):
                with self.assertRaises(Gate17SecondaryOwnerTraceError):
                    decoded_direct_call_candidates(pe, target)
        for count in (0, 4097, True):
            with self.subTest(count=count):
                with self.assertRaises(Gate17SecondaryOwnerTraceError):
                    decoded_direct_call_candidates(pe, 0x401180, max_matches=count)

    def test_bad_report_window_fails_closed(self):
        pe = parse_fixture()
        with self.assertRaisesRegex(
            Gate17SecondaryOwnerTraceError,
            "trace windows",
        ):
            secondary_owner_trace_report(
                pe,
                windows=(("bad", 0x401020),),
                globals_to_find=GLOBALS,
                call_targets=CALL_TARGETS,
            )

    def test_cli_emits_private_neutral_trace_contract(self):
        pe = parse_fixture()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.exe"
            source.write_bytes(synthetic_pe())
            output = Path(directory) / "secondary-owner.json"
            argv = [
                "gate17_secondary_owner_source_trace.py",
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
                    "gate17_secondary_owner_source_trace.require_private_output_path",
                    return_value=None,
                ),
                patch(
                    "gate17_secondary_owner_source_trace.secondary_owner_trace_report",
                    side_effect=lambda pe, **kwargs: secondary_owner_trace_report(
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
            self.assertFalse(emitted["live_secondary_runtime_owner_recovered"])
            self.assertFalse(emitted["secondary_save_serialization_recovered"])
            self.assertFalse(emitted["procedural_secondary_scope_playable"])
            self.assertFalse(emitted["gate17_complete"])


if __name__ == "__main__":
    unittest.main()
