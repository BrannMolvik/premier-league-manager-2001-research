"""Cross-check independently source-bounded nonhuman 60AA20 receipts.

The specialized 606540 nonhuman contract uses two real native 417340
proof records. A separate 60AA20-only projection is compared against it
using TEST fixtures, not by claiming original executable execution or
port queue integration. A semantic disagreement blocks integration.
"""
from __future__ import annotations

import unittest

from original_native_60aa20_pending_event import (
    source_original_60aa20_nonhuman_pending_from_reached,
)
from original_native_60aa20_pending_source import (
    Original60AA20Reached, source_original_60aa20_project,
)
from test_original_native_60aa20_pending_event import reached as specialized_input


class Original60AA20IndependentProjectionTests(unittest.TestCase):
    def test_original_nonhuman_status_and_duration_crosscheck(self):
        for case in (
            dict(first606540=10, rng4=None, source77=60, initial22=254, global_day=100),
            dict(first606540=65, rng4=0, source77=60, initial22=254, global_day=100),
            dict(first606540=85, rng4=2, source77=60, initial22=253, global_day=100),
            dict(first606540=97, rng4=2, source77=0, initial22=253, global_day=0xfffffffe),
        ):
            with self.subTest(case=case):
                # Specialized source receipt cannot skip either independently
                # qualified 417340 nonhuman manager proof.
                src=specialized_input(**case)
                qualified=source_original_60aa20_nonhuman_pending_from_reached(src)
                stage=src.original_606540_predispatch
                pid=stage.original_player_id
                generic=source_original_60aa20_project(
                    Original60AA20Reached(
                        player_id=pid,
                        player_before=src.original_player_at_60aa20,
                        descriptor_before=src.original_descriptor_at_60aa20,
                        descriptor_pointer=src.original_descriptor_pointer,
                        # Synthetic getter identities for a differential TEST.
                        # A real original receipt needs reached native getters.
                        resolver_player_ids=(pid,)*6,
                        duration_delta_arg=stage.original_schedule_delta_from_rng,
                        player77_decrement_base_arg=stage.original_schedule_base_from_mutable_source,
                        current_date_9847fc=src.original_raw_global_calendar_day_9847fc,
                        registered_417340_al=0,
                    )
                )
                self.assertEqual(generic.original_player_after_source,
                                 qualified.original_player_after_41a860_and_60aa20)
                self.assertEqual(generic.original_descriptor_after_source,
                                 qualified.original_descriptor_after_60aa20)
                self.assertEqual(generic.original_duration_after_mitigation,
                                 qualified.original_duration_after_native_mitigation)
                self.assertEqual(generic.original_pending_identity.original_date_raw_u32,
                                 qualified.original_pending_event_candidate.original_due_day_raw)
                self.assertEqual(generic.original_pending_identity.original_status_byte,
                                 qualified.original_pending_event_candidate.original_subtype_status_5)
                self.assertEqual(generic.original_rng5_draw_count,0)
                self.assertFalse(generic.original_queue_inserted)
                self.assertFalse(qualified.original_pending_event_candidate.original_947aa8_pending_queue_changed)


if __name__=='__main__':
    unittest.main()
