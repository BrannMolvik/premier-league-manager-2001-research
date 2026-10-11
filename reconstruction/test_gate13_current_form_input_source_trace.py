"""Source-only synthetic tests: original licensed FM2001 PE remains private."""
from __future__ import annotations

from hashlib import sha256
from importlib.util import find_spec
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from gate13_button_source_trace import OriginalPE32
from gate13_current_form_input_source_trace import (
    CLASSIFICATION,
    CURRENT_FORM_INPUT_WINDOWS,
    DIRECT_CALL_TARGETS,
    GLOBAL_POINTER_LEADS,
    CurrentFormInputTraceError,
    current_form_input_source_report,
    decoded_direct_caller_leads,
    main as trace_main,
)
from test_gate13_button_source_trace import synthetic_pe


WINDOWS = (
    ("synthetic form constructor", 0x401020, 0x10),
    ("synthetic widget callback", 0x401070, 0x10),
)
GLOBALS = (("synthetic private pointer", 0x946590),)
TARGETS = (("synthetic callback", 0x401070),)


def local_source():
    # Only source-free, synthetic bytes. Independent Capstone caller canary.
    data = bytearray(synthetic_pe())
    data[0x200:0x2A0] = b"\x90" * 0xA0
    data[0x220] = 0xE8
    struct.pack_into("<i", data, 0x221, 0x401070 - (0x401020 + 5))
    data[0x225] = 0xC3
    data[0x270:0x274] = b"\x55\x8b\xec\xc3"
    struct.pack_into("<I", data, 0x2A4, 0x946590)
    return bytes(data)


def fixture():
    raw = local_source()
    return OriginalPE32.parse(raw, expected_sha256=sha256(raw).hexdigest())


class OriginalCurrentFormInputPrivateTraceTests(unittest.TestCase):
    def test_known_source_anchors_are_inspection_leads_only(self):
        self.assertIn(
            ("native sort1 alternate row 0x2B0 constructor", 0x4480A0, 0x590),
            CURRENT_FORM_INPUT_WINDOWS,
        )
        self.assertIn(("radio_child_callback", 0x5D4AC0), DIRECT_CALL_TARGETS)
        self.assertIn(("source_mouse_current_owner", 0x984814), GLOBAL_POINTER_LEADS)

    def test_private_source_windows_and_global_not_semantic(self):
        pe = fixture()
        report = current_form_input_source_report(
            pe, windows=WINDOWS, globals_to_find=GLOBALS, call_targets=TARGETS,
        )
        self.assertEqual(report["source_sha256"], pe.sha256)
        self.assertEqual(len(report["windows"]), 2)
        self.assertEqual(report["windows"][0]["start_va"], 0x401020)
        self.assertEqual(report["windows"][0]["raw_hex"][:2], "e8")
        self.assertEqual(
            report["windows"][0]["classification"],
            "bounded_window_not_verified_function_boundaries",
        )
        self.assertIsNone(report["windows"][0]["linear_disassembly_not_cfg"])
        self.assertIsNone(report["decoded_direct_call_candidates"])
        pointers = report["global_pointer_candidates"][0]["raw_occurrences_not_decoded_xrefs"]
        self.assertEqual(tuple(c["candidate_va"] for c in pointers), (0x402004,))
        self.assertEqual(report["original_contract"]["form_slot_count"], 6)
        self.assertEqual(report["original_contract"]["native_sort_current_form_state"], 1)
        self.assertFalse(report["six_widget_row_geometry_and_font_source_verified_by_this_trace"])
        self.assertFalse(report["root_wm_lbutton_to_radio_event15_source_verified_by_this_trace"])
        self.assertFalse(report["original_league_tables_mouse_input_integrated"])
        self.assertFalse(report["gate13_complete"])
        self.assertFalse(report["gate17_complete"])
        self.assertIn("not authorize a click", report["evidence_limit"])

    @unittest.skipUnless(find_spec("capstone") is not None, "Capstone optional")
    def test_direct_calls_are_candidates_not_mouse_owner_or_layout_proofs(self):
        pe = fixture()
        leads = decoded_direct_caller_leads(pe, TARGETS)
        self.assertEqual(len(leads), 1)
        self.assertEqual(tuple(c["callsite_va"] for c in
            leads[0]["candidate_calls_not_mouse_or_widget_semantics"]), (0x401020,))
        self.assertEqual(
            leads[0]["candidate_calls_not_mouse_or_widget_semantics"][0]["classification"],
            CLASSIFICATION,
        )
        report = current_form_input_source_report(
            pe, windows=WINDOWS, globals_to_find=GLOBALS, call_targets=TARGETS,
            with_disassembly=True, scan_direct_calls=True,
        )
        self.assertGreater(len(report["windows"][0]["linear_disassembly_not_cfg"]), 1)
        self.assertFalse(report["root_wm_lbutton_to_radio_event15_source_verified_by_this_trace"])

    def test_bad_source_windows_are_never_promoted(self):
        pe = fixture()
        for windows in (
            (("missing size", 0x401020),),
            (("duplicate", 0x401020, 10), ("duplicate", 0x401070, 10)),
            (("data as executable", 0x402000, 4),),
            (("bool", True, 4),),
            (("zero", 0x401020, 0),),
            (("too large", 0x401020, 0x1001),),
        ):
            with self.subTest(windows=windows):
                with self.assertRaises(CurrentFormInputTraceError):
                    current_form_input_source_report(
                        pe, windows=windows, globals_to_find=(),
                    )

    def test_invalid_options_and_duplicate_source_calls_fail_closed(self):
        pe = fixture()
        for invalid in (-1, 0, 4097, True, "2"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(CurrentFormInputTraceError):
                    current_form_input_source_report(
                        pe, windows=WINDOWS, globals_to_find=(),
                        max_matches=invalid,
                    )
        for invalid in ("True", 1, None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(CurrentFormInputTraceError):
                    current_form_input_source_report(
                        pe, windows=WINDOWS, globals_to_find=(),
                        with_disassembly=invalid,
                    )
        with self.assertRaisesRegex(CurrentFormInputTraceError, "duplicate global"):
            current_form_input_source_report(
                pe, windows=WINDOWS,
                globals_to_find=(("same", 0x946590), ("same", 0x946590)),
            )
        with self.assertRaisesRegex(CurrentFormInputTraceError, "duplicate"):
            decoded_direct_caller_leads(
                pe, (("same", 0x401070), ("same", 0x401070)),
            )

    def test_cli_private_output_and_neutral_report_without_original_program(self):
        pe = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            executable = Path(tmp) / "synthetic.exe"
            output = Path(tmp) / "current-form-private.json"
            executable.write_bytes(local_source())
            with (
                patch.object(OriginalPE32, "parse", return_value=pe),
                patch("gate13_current_form_input_source_trace.CURRENT_FORM_INPUT_WINDOWS", WINDOWS),
                patch("gate13_current_form_input_source_trace.GLOBAL_POINTER_LEADS", GLOBALS),
                patch("gate13_current_form_input_source_trace.DIRECT_CALL_TARGETS", TARGETS),
                patch.object(sys, "argv", [
                    "gate13_current_form_input_source_trace.py",
                    str(executable), "--output", str(output),
                ]),
            ):
                self.assertEqual(trace_main(), 0)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["source_sha256"], pe.sha256)
            self.assertFalse(data["gate13_complete"])
            self.assertFalse(data["original_six_widget_rendering_integrated"])


if __name__ == "__main__":
    unittest.main()
