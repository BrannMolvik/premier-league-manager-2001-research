"""Source-bounded four-scoring-stage inherited B store evidence and negatives."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import unpack_from
from unittest import TestCase
from original_match_four_b_direct_writer import (
    OriginalStageBWriterEvidenceError,
    source_last_explicit_b_writer_before_nonhuman_stage,
)


class FourScoringStageBDirectWriterTests(TestCase):
    def test_first_direct_writer_can_be_absent_when_stage1_skipped(self):
        r = source_last_explicit_b_writer_before_nonhuman_stage(
            target_stage=2, reached_prior_stage_gates=(None,))
        self.assertIsNone(r.preceding_native_stage)
        self.assertEqual(r.native_store_sites, ())
        self.assertTrue(r.no_prior_explicit_writer_proven)
        self.assertFalse(r.native_b_qword_known)
        self.assertFalse(r.original_executed)
        self.assertFalse(r.game_state_updated)

    def test_first_stage_writes_even_for_nonhuman(self):
        r = source_last_explicit_b_writer_before_nonhuman_stage(
            target_stage=3, reached_prior_stage_gates=(False, False))
        self.assertEqual(r.preceding_native_stage, 1)
        self.assertEqual(r.native_store_sites, (0x5DA9AD,))

    def test_later_human_stage_overwrites_and_nonhuman_preserves(self):
        for stage, prior, last in (
            (4, (True, True, False), 2),
            (4, (None, False, True), 3),
            (4, (None, False, False), None),
            (4, (False, None, False), 1),
            (4, (None, None, None), None),
        ):
            with self.subTest(stage=stage, prior=prior):
                r = source_last_explicit_b_writer_before_nonhuman_stage(
                    target_stage=stage, reached_prior_stage_gates=prior)
                self.assertEqual(r.preceding_native_stage, last)
                self.assertFalse(r.native_b_qword_known)

    def test_no_invented_prior_history_or_human_classification(self):
        for stage, history in (
            (1, ()), (2, ()), (2, (False, False)),
            (3, (False, 0)), (4, (False, None, 'human')),
            (2, [False]), (True, ()), (4, ()),
        ):
            with self.subTest(stage=stage, history=history):
                with self.assertRaises(OriginalStageBWriterEvidenceError):
                    source_last_explicit_b_writer_before_nonhuman_stage(
                        target_stage=stage, reached_prior_stage_gates=history)

    def test_original_native_stage_guards_and_explicit_b_store_sites(self):
        exe = environ.get('FM2001_ORIGINAL_EXE')
        if not exe:
            self.skipTest('private original PE absent in CI')
        raw = Path(exe).read_bytes()
        self.assertEqual((len(raw), sha256(raw).hexdigest()), (
            4714541, '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        for src, target in ((0x5DA981, 0x5DAC05), (0x5DAC14, 0x5DAE80),
                            (0x5DAE92, 0x5DB101), (0x5DB110, 0x5DB37C)):
            with self.subTest(guard=hex(src)):
                pos = src - 0x400000
                self.assertEqual(raw[pos:pos+2], b'\x0f\x85')
                self.assertEqual(src + 6 + unpack_from('<i', raw, pos+2)[0], target)
        for src, code in (
            (0x5DA9AD, 'dd 5c 24 38'),
            (0x5DAC57, '89 4c 24 3c 8b ce 89 44 24 38'),
            (0x5DAED5, '89 4c 24 38 8b ce 89 54 24 3c'),
            (0x5DB153, '89 4c 24 3c 8b ce 89 44 24 38'),
            (0x5DAC79, 'c7 44 24 30 00 00 00 00'),
            (0x5DAEF7, 'c7 44 24 30 00 00 00 00'),
            (0x5DB175, 'c7 44 24 30 00 00 00 00'),
            (0x5DA8D9, '8d 8c 24 98 00 00 00 8d 94 24 90 00 00 00 51 52'),
        ):
            with self.subTest(site=hex(src)):
                b = bytes.fromhex(code)
                self.assertEqual(raw[src-0x400000:src-0x400000+len(b)], b)
        self.assertEqual(raw[0x5DA967-0x400000:0x5DA96C-0x400000],
                         bytes.fromhex('e8 54 22 e3 ff'))

    def test_native_668350_temporarily_truncates_and_restores_x87_cw(self):
        exe = environ.get('FM2001_ORIGINAL_EXE')
        if not exe:
            self.skipTest('private original PE absent in CI')
        raw = Path(exe).read_bytes()
        self.assertEqual((len(raw), sha256(raw).hexdigest()), (
            4714541, '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        native = bytes.fromhex(
            '55 8b ec 83 c4 f4 9b d9 7d fe 9b 66 8b 45 fe 80 cc 0c '
            '66 89 45 fc d9 6d fc df 7d f4 d9 6d fe 8b 45 f4 8b 55 f8 c9 c3')
        self.assertEqual(raw[0x668350-0x400000:0x668350-0x400000+len(native)],native)
        # OR AH,0x0C requests x87 RC=11 (truncate); FISTP QWORD;
        # FLDCW restores the saved prior control word before returning.
        for va in (0x5DAA00, 0x5DABCA, 0x5DABDB, 0x5DAE45, 0x5DAE56,
                   0x5DB0C6, 0x5DB0D7, 0x5DB341, 0x5DB352):
            with self.subTest(call=hex(va)):
                off=va-0x400000
                self.assertEqual(raw[off], 0xE8)
                self.assertEqual(va+5+unpack_from('<i',raw,off+1)[0],0x668350)
