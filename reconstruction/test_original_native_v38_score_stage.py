"""Original 0x513570 event linked-score stage, read-only source regressions."""
from __future__ import annotations

import unittest
from struct import pack_into, unpack_from

from original_native_v38_score_stage import (
    OriginalV38ScoreStageError,
    source_original_513570_pre_rng_score_stage,
)

WRAPPED_V38_VTABLE = 0x7C9D9C


def match(*, scores=(3, 4), prior=(0, 0, 0, 0), flags=0,
          vtable=WRAPPED_V38_VTABLE):
    result = bytearray(0x5C)
    pack_into("<I", result, 0, vtable)
    pack_into("<H", result, 0x3C, scores[0])
    pack_into("<H", result, 0x3E, scores[1])
    pack_into("<I", result, 0x44, flags)
    result[0x58:0x5C] = bytes(prior)
    return bytes(result)


def context(*, primary=0, secondary=0, head=0, scores=(3,4)):
    raw = bytearray(0xD52)
    pack_into("<I", raw, 0xD0C, primary)
    pack_into("<I", raw, 0xD10, secondary)
    pack_into("<I", raw, 0xB60, head)
    pack_into("<H", raw, 0xD4C, scores[0])
    pack_into("<H", raw, 0xD50, scores[1])
    return bytes(raw)


def event(*, kind, owner=0, side=0, following=0):
    result = bytearray(0x38)
    for offset, value in ((0x28, kind), (0x24, owner),
                          (0x04, side), (0x34, following)):
        pack_into("<I", result, offset, value)
    return bytes(result)


def scorestage(native_match=None, ctx=None, events=None, **kwargs):
    return source_original_513570_pre_rng_score_stage(
        original_match_record=match() if native_match is None else native_match,
        original_context=context() if ctx is None else ctx,
        original_linked_events={} if events is None else events,
        **kwargs)


class OriginalV38LinkedScoreStageTests(unittest.TestCase):
    def test_native_zero_count_fast_return_ignores_head_and_bit2(self):
        original = match(prior=(7, 8, 9, 10), flags=4)
        result = scorestage(
            native_match=original, ctx=context(head=0x1000), events={})
        self.assertEqual(result.projected_match_record, original)
        self.assertFalse(result.requires_513659_bit2_resolution)
        self.assertEqual(result.visited_event_pointers, ())
        self.assertTrue(result.prior_wrapper_5112a0_effects_proven)
        self.assertFalse(result.native_match_completion_proven)

    def test_native_5112a0_wrapper_overwrites_both_old_score_words(self):
        # 0x5136C0 calls 0x5112A0 first, even when 0x513570 then
        # immediately takes its zero-count fast return.
        raw = match(scores=(33, 44))
        receipt = scorestage(
            native_match=raw, ctx=context(scores=(5, 6)))
        self.assertEqual(
            (unpack_from("<H", receipt.projected_match_record, 0x3C)[0],
             unpack_from("<H", receipt.projected_match_record, 0x3E)[0]),
            (5, 6))
        self.assertTrue(receipt.prior_wrapper_5112a0_effects_proven)
        self.assertFalse(receipt.native_match_completion_proven)

    def test_primary_kind8_to_two_scoring_events_and_kind7_stop(self):
        chain = {
            0x1000: event(kind=2, following=0x2000),
            0x2000: event(kind=8, following=0x3000),
            0x3000: event(kind=0, owner=0, side=0, following=0x4000),
            0x4000: event(kind=4, owner=3, side=9, following=0x5000),
            0x5000: event(kind=7, following=0x6000),
            0x6000: event(kind=0, owner=0),
        }
        result = scorestage(
            ctx=context(primary=1, secondary=1, head=0x1000),
            events=chain)
        raw=result.projected_match_record
        self.assertEqual(tuple(raw[0x58:0x5C]), (1, 1, 0, 0))
        self.assertEqual((unpack_from("<H", raw, 0x3C)[0],
                          unpack_from("<H", raw, 0x3E)[0]), (2, 3))
        self.assertEqual(result.final_cursor_pointer, 0x5000)
        self.assertNotIn(0x6000, result.visited_event_pointers)
        self.assertFalse(result.native_match_completion_proven)

    def test_secondary_continues_from_primary_type9_not_head(self):
        chain = {
            0x1000: event(kind=8, following=0x2000),
            0x2000: event(kind=2, side=0, following=0x3000),
            0x3000: event(kind=9, following=0x4000),
            0x4000: event(kind=1, side=1, owner=3),
        }
        result = scorestage(
            ctx=context(primary=1, secondary=1, head=0x1000), events=chain)
        raw=result.projected_match_record
        self.assertEqual(tuple(raw[0x58:0x5C]), (1, 0, 0, 1))
        self.assertEqual((unpack_from("<H", raw, 0x3C)[0],
                          unpack_from("<H", raw, 0x3E)[0]), (2, 4))
        self.assertEqual(result.final_cursor_pointer, 0)

    def test_secondary_only_scans_to_kind9_then_counts(self):
        chain = {
            0x1000: event(kind=0, following=0x2000),
            0x2000: event(kind=9, following=0x3000),
            0x3000: event(kind=4, owner=0, side=0, following=0x4000),
            0x4000: event(kind=4, owner=7, side=1),
        }
        result = scorestage(ctx=context(secondary=2, head=0x1000),
                            events=chain)
        self.assertEqual(tuple(result.projected_match_record[0x58:0x5C]),
                         (0, 0, 1, 0))
        self.assertEqual(result.final_cursor_pointer, 0)
        self.assertEqual(result.visited_event_pointers,
                         (0x1000,0x2000,0x3000,0x4000))

    def test_secondary_without_kind9_does_not_count_earlier_event(self):
        result = scorestage(
            ctx=context(secondary=1, head=0x1000),
            events={0x1000: event(kind=2, following=0x2000),
                    0x2000: event(kind=0)})
        self.assertEqual(result.projected_match_record, match())
        self.assertEqual(result.final_cursor_pointer, 0)

    def test_signed_byte_primary_subtraction_and_uint16_wrap(self):
        raw = match(scores=(0,0), prior=(0xFF,1,0,0))
        result = scorestage(native_match=raw,
                            ctx=context(primary=1, head=0, scores=(0,0)),events={})
        self.assertEqual((unpack_from("<H", result.projected_match_record,0x3C)[0],
                          unpack_from("<H", result.projected_match_record,0x3E)[0]),
                         (1, 65535))
        self.assertEqual(result.projected_match_record[0x58:0x5A],b"\xff\x01")

    def test_secondary_byte_counter_wraps_and_bit2_is_left_unresolved(self):
        result = scorestage(
            native_match=match(prior=(0,0,255,0), flags=4),
            ctx=context(secondary=1,head=0x1000),
            events={0x1000:event(kind=9,following=0x2000),
                    0x2000:event(kind=0)})
        self.assertEqual(result.projected_match_record[0x5A],0)
        self.assertTrue(result.requires_513659_bit2_resolution)
        self.assertFalse(result.native_match_completion_proven)

    def test_fail_closed_invalid_owner_and_missing_reached_pointer(self):
        invalid = (
            {"native_match":match(vtable=0x7C4C24)},
            {"native_match":bytes(0x5B)},
            {"ctx":bytes(0xD51)},
            {"ctx":bytearray(0xD52)},
            {"events":[]},
            {"max_linked_nodes":True},
            {"ctx":context(primary=1,head=0x1000)},
            {"ctx":context(primary=1,head=0x1000),
             "events":{0x1000:bytearray(0x38)}},
            {"ctx":context(primary=1,head=0x1000),
             "events":{0x1000:bytes(0x37)}},
        )
        for row in invalid:
            with self.subTest(row=row):
                with self.assertRaises(OriginalV38ScoreStageError):
                    scorestage(**row)

    def test_cycle_detection_has_no_partial_published_score(self):
        with self.assertRaisesRegex(OriginalV38ScoreStageError, "cyclic"):
            scorestage(
                ctx=context(primary=1,head=0x1000),
                events={0x1000:event(kind=2,following=0x1000)})
        with self.assertRaisesRegex(OriginalV38ScoreStageError, "cyclic"):
            scorestage(
                ctx=context(secondary=1,head=0x1000),
                events={0x1000:event(kind=9,following=0x2000),
                        0x2000:event(kind=0,following=0x2000)})

    def test_bound_rejects_too_many_original_events(self):
        with self.assertRaisesRegex(OriginalV38ScoreStageError,"caller bound"):
            scorestage(
                ctx=context(primary=1,head=0x1000),
                events={0x1000:event(kind=1,following=0x2000),
                        0x2000:event(kind=8)},max_linked_nodes=1)


if __name__ == "__main__":
    unittest.main()
