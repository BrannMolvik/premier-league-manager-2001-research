"""Synthetic trace contracts only; not a native report-production test."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from gate13_button_source_trace import OriginalPETraceError
from gate13_live_report_producer_trace import (
    SOURCE_SHA256,
    LIVE_PRODUCER_WINDOWS,
    REMAINING_SETUP_DISPLACEMENTS,
    REMAINING_SETUP_WINDOWS,
    classify_remaining_setup_memory_operands,
    live_report_producer_trace,
)


class LiveReportProducerTraceTests(unittest.TestCase):
    def test_metadata_scope_skips_completed_producers(self):
        reads = []
        def read(address, size):
            reads.append((address, size))
            return bytes(size)
        report = live_report_producer_trace(SimpleNamespace(sha256=SOURCE_SHA256, read=read),
                                            metadata_only=True)
        self.assertEqual(reads, [(address, size) for _, address, size in LIVE_PRODUCER_WINDOWS[21:]])
        self.assertEqual(len(report['windows']), 11)
        self.assertFalse(report['runtime_capture_production_complete'])

    def test_remaining_setup_scope_reads_only_bounded_blocker_windows(self):
        reads = []

        def read(address, size):
            reads.append((address, size))
            return bytes(size)

        report = live_report_producer_trace(
            SimpleNamespace(sha256=SOURCE_SHA256, read=read),
            remaining_setup_only=True,
        )
        self.assertEqual(
            reads,
            [(address, size) for _, address, size in REMAINING_SETUP_WINDOWS],
        )
        self.assertEqual(len(report['windows']), len(REMAINING_SETUP_WINDOWS))
        self.assertFalse(report['remaining_setup_trace_complete'])
        self.assertFalse(report['legacy_capacity_writer_identified'])
        self.assertFalse(report['gate13_closed'])

    def test_bounded_memory_operand_classifier_preserves_direction_and_registers(self):
        # mov eax,[ecx+13Ch]; mov [edx+140h],eax;
        # add dword ptr [ebx+130h],1; cmp byte ptr [esi+76h],0
        blob = bytes.fromhex(
            "8b813c010000"
            "898240010000"
            "83833001000001"
            "807e7600"
        )
        rows = classify_remaining_setup_memory_operands(blob, 0x500000)
        self.assertEqual(
            [(row["displacement"], row["access"]) for row in rows],
            [(0x13C, "read"), (0x140, "write"), (0x130, "read_write"), (0x76, "read")],
        )
        self.assertEqual(
            [row["base_register"] for row in rows],
            ["ecx", "edx", "ebx", "esi"],
        )
        self.assertTrue(all(row["candidate_only"] for row in rows))
        self.assertTrue(all(not row["semantic_identity_proven"] for row in rows))
        self.assertEqual(
            tuple(sorted({row["displacement"] for row in rows})),
            tuple(sorted(REMAINING_SETUP_DISPLACEMENTS)),
        )

    def test_bounded_memory_operand_classifier_ignores_other_displacements(self):
        blob = bytes.fromhex(
            "8b810c010000"  # mov eax,[ecx+10Ch]
            "898244010000"  # mov [edx+144h],eax
        )
        self.assertEqual(
            classify_remaining_setup_memory_operands(blob, 0x500000),
            [],
        )

    def test_remaining_setup_disassembly_adds_candidates_only_to_bounded_scope(self):
        pe = SimpleNamespace(
            sha256=SOURCE_SHA256,
            read=lambda address, size: bytes(size),
        )
        classified = [{"candidate_only": True}]
        with (
            patch(
                "gate13_live_report_producer_trace.disassemble_window",
                return_value=[],
            ),
            patch(
                "gate13_live_report_producer_trace.classify_remaining_setup_memory_operands",
                return_value=classified,
            ) as classifier,
        ):
            report = live_report_producer_trace(
                pe,
                with_disassembly=True,
                remaining_setup_only=True,
            )
        self.assertEqual(classifier.call_count, len(REMAINING_SETUP_WINDOWS))
        self.assertTrue(
            all(
                row["bounded_memory_operand_candidates"] == classified
                for row in report["windows"]
            )
        )
        self.assertFalse(report["remaining_setup_trace_complete"])
        self.assertFalse(report["legacy_capacity_writer_identified"])

    def test_remaining_setup_scope_is_mutually_exclusive_with_metadata_scope(self):
        pe = SimpleNamespace(
            sha256=SOURCE_SHA256,
            read=lambda address, size: bytes(size),
        )
        with self.assertRaisesRegex(
            ValueError,
            'either metadata-only or remaining-setup-only',
        ):
            live_report_producer_trace(
                pe,
                metadata_only=True,
                remaining_setup_only=True,
            )

    def test_rejects_wrong_source_before_reading(self):
        def unexpected_read(*args):
            raise AssertionError('read before canonical identity verification')
        with self.assertRaises(OriginalPETraceError):
            live_report_producer_trace(SimpleNamespace(sha256='wrong', read=unexpected_read))

    def test_window_contract_does_not_promote_runtime_production(self):
        pe = SimpleNamespace(sha256=SOURCE_SHA256, read=lambda address, size: bytes(size))
        report = live_report_producer_trace(pe)
        self.assertEqual(len(report['windows']), len(LIVE_PRODUCER_WINDOWS))
        self.assertFalse(report['runtime_capture_production_complete'])
        self.assertFalse(report['normal_pmatchinfo_opening_verified'])
        self.assertFalse(report['gate13_closed'])
        for window in report['windows']:
            self.assertEqual(len(window['sha256']), 64)
            self.assertNotIn('linear_disassembly_not_cfg', window)

    def test_optional_disassembly_keeps_evidence_boundary(self):
        pe = SimpleNamespace(sha256=SOURCE_SHA256, read=lambda address, size: bytes(size))
        with patch('gate13_live_report_producer_trace.disassemble_window', return_value=[]):
            report = live_report_producer_trace(pe, with_disassembly=True)
        self.assertTrue(all('linear_disassembly_not_cfg' in row for row in report['windows']))
        self.assertFalse(report['runtime_capture_production_complete'])


if __name__ == '__main__':
    unittest.main()
