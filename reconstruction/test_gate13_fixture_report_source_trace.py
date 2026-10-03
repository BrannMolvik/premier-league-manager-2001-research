import os
from pathlib import Path
import unittest
from gate13_fixture_report_source_trace import FIXTURE_REPORT_WINDOWS, fixture_report_trace_report
from gate13_button_source_trace import OriginalPE32


class FixtureReportSourceTraceTests(unittest.TestCase):
    def test_profiles_include_capture_owner_and_native_input_not_just_popup(self):
        addresses = {va for _, va, _ in FIXTURE_REPORT_WINDOWS}
        self.assertTrue({0x51145B, 0x60BE50, 0x60BF10, 0x60BF90, 0x60C020,
                         0x5320B0, 0x653600, 0x64F960, 0x46E620} <= addresses)
        self.assertTrue({0x60BCB0, 0x659CF0, 0x659D30, 0x633610,
                         0x6336A0, 0x6336E0, 0x633B30} <= addresses)
        self.assertTrue(all(size > 0 for _, _, size in FIXTURE_REPORT_WINDOWS))
        self.assertEqual(len(addresses), len(FIXTURE_REPORT_WINDOWS))

    @unittest.skipUnless(os.environ.get('FM2001_ORIGINAL_EXE'), 'licensed original is private')
    def test_canonical_source_slot_calibration_and_private_scope(self):
        pe = OriginalPE32.parse(Path(os.environ['FM2001_ORIGINAL_EXE']).read_bytes())
        report = fixture_report_trace_report(pe)
        self.assertEqual(report['native_pointer_message'], 0x204)
        self.assertEqual(report['capture_count_offsets'], [0x5A4, 0xB54])
        self.assertFalse(report['runtime_capture_production_complete'])
        self.assertFalse(report['gate13_closed'])
        self.assertEqual(len(report['calibrated_slots']), 5)
        self.assertEqual(len(report['calibrated_script_dispatch_tables']), 5)
        self.assertEqual(report['participant_statistics_bits_per_record'], 12)
        self.assertEqual(report['script_count_bits'], 10)
        self.assertEqual(len(report['windows']), len(FIXTURE_REPORT_WINDOWS))
