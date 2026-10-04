"""Synthetic trace contracts only; not a native report-production test."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from gate13_button_source_trace import OriginalPETraceError
from gate13_live_report_producer_trace import (
    SOURCE_SHA256, LIVE_PRODUCER_WINDOWS, REMAINING_SETUP_WINDOWS, live_report_producer_trace,
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

    def test_remaining_setup_scope_is_mutually_exclusive_with_metadata_scope(self):
        pe = SimpleNamespace(sha256=SOURCE_SHA256, read=lambda address, size: bytes(size))
        with self.assertRaisesRegex(ValueError, 'either metadata-only or remaining-setup-only'):
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
