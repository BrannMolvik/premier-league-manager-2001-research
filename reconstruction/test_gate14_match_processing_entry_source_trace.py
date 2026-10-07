"""Regression coverage for the candidate-only Gate-14 match entry tracer."""
from importlib.util import find_spec
import unittest

from gate14_match_processing_entry_source_trace import (
    MATCH_PROCESSING_ROUTER_VA,
    Gate14MatchProcessingEntryTraceError,
    match_processing_entry_trace_report,
)
from test_gate13_button_vtable_xref_candidates import source_style_fixture


class MatchProcessingEntryTraceTests(unittest.TestCase):
    def test_router_identity_is_the_existing_source_closed_entry(self):
        self.assertEqual(MATCH_PROCESSING_ROUTER_VA, 0x513010)

    @unittest.skipUnless(find_spec("capstone"), "Capstone optional outside focused CI")
    def test_direct_candidate_remains_explicitly_unadjudicated(self):
        # source_style_fixture has a synthetic direct CALL at 0x401020 -> 0x401040.
        report = match_processing_entry_trace_report(
            source_style_fixture(),
            router_va=0x401040,
            context_before=0x10,
            context_after=0x20,
            with_disassembly=True,
        )

        self.assertEqual(report["direct_candidate_count"], 1)
        candidate = report["direct_candidates"][0]
        self.assertEqual(candidate["candidate_instruction_va"], 0x401020)
        self.assertEqual(candidate["candidate_target_va"], 0x401040)
        self.assertEqual(candidate["candidate_mnemonic"], "call")
        self.assertEqual(candidate["context_start_va"], 0x401010)
        self.assertGreater(candidate["context_window_bytes"], 0)
        self.assertTrue(candidate["context_raw_hex"])
        self.assertTrue(candidate["context_linear_disassembly_only"])
        self.assertIn("not_runtime", candidate["classification"])

        self.assertTrue(report["direct_candidate_scan_completed"])
        self.assertFalse(report["direct_callers_adjudicated"])
        self.assertFalse(report["indirect_or_vtable_callers_scanned"])
        self.assertFalse(report["management_owner_recovered"])
        self.assertFalse(report["fixture_start_condition_recovered"])
        self.assertFalse(report["management_ui_entry_trigger_recovered"])
        self.assertFalse(report["match_processing_entry_route_recovered"])
        self.assertFalse(report["gate14_complete"])
        self.assertIn("manual", report["evidence_limit"].lower())
        self.assertIn("indirect", report["evidence_limit"].lower())

    @unittest.skipUnless(find_spec("capstone"), "Capstone optional outside focused CI")
    def test_empty_direct_scan_does_not_promote_recovery(self):
        report = match_processing_entry_trace_report(
            source_style_fixture(),
            router_va=0x401070,
        )
        self.assertEqual(report["direct_candidate_count"], 0)
        self.assertEqual(report["direct_candidates"], ())
        self.assertFalse(report["management_ui_entry_trigger_recovered"])
        self.assertFalse(report["match_processing_entry_route_recovered"])

    def test_invalid_trace_arguments_fail_closed(self):
        pe = source_style_fixture()
        for router in (-1, 1 << 32, True, "0x513010"):
            with self.subTest(router=router):
                with self.assertRaises(Gate14MatchProcessingEntryTraceError):
                    match_processing_entry_trace_report(pe, router_va=router)
        for count in (0, -1, True, 1.5):
            with self.subTest(count=count):
                with self.assertRaises(Gate14MatchProcessingEntryTraceError):
                    match_processing_entry_trace_report(
                        pe,
                        router_va=0x401040,
                        max_candidates=count,
                    )
        for before, after in ((-1, 1), (0, 0), (0x1001, 1), (0, 0x1001)):
            with self.subTest(before=before, after=after):
                with self.assertRaises(Gate14MatchProcessingEntryTraceError):
                    match_processing_entry_trace_report(
                        pe,
                        router_va=0x401040,
                        context_before=before,
                        context_after=after,
                    )


if __name__ == "__main__":
    unittest.main()
