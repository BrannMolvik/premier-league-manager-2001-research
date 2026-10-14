"""Native 606540 no-human branch to 60AA20 source-ownership tests."""
from dataclasses import replace
import unittest

from original_native_605f90_dispatch import (
    Original606540Reached, source_original_606540_pre_human_from_reached,
)
from original_native_606540_to_60aa20 import (
    Original606540To60AA20NonhumanReached,
    source_original_606540_nonhuman_pending_from_reached,
)
from original_native_60aa20_pending_source import Original60AA20SourceError
from test_original_native_605f90_dispatch import predispatched
from test_original_native_60aa20_pending_source import reached as pending_input


def chain(status=0):
    p = predispatched(subtype=1,draw=0)
    if status == 0:
        h=source_original_606540_pre_human_from_reached(
            Original606540Reached(p,10,50,original_82232c_short_base=4))
    elif status == 1:
        h=source_original_606540_pre_human_from_reached(
            Original606540Reached(p,65,50,original_822324_second_threshold=80,
                original_second_rng4_result=0,original_822330_medium_base=35))
    else:
        h=source_original_606540_pre_human_from_reached(
            Original606540Reached(p,85,50,original_822324_second_threshold=80,
                original_822328_third_threshold=95,
                original_second_rng4_result=2,original_822334_long_base=60))
    n=pending_input(status=status,delta=h.original_schedule_delta_from_rng,
        base=h.original_schedule_base_from_mutable_source,source77=90)
    n=replace(n,descriptor_before=h.original_source_descriptor_before_417340)
    return Original606540To60AA20NonhumanReached(p,h,0,n)


class Source606540To60AA20Tests(unittest.TestCase):
    def test_606540_nonhuman_branch_preserves_owner_and_queues_source_projection(self):
        for status in (0,1,2):
            with self.subTest(status=status):
                q=chain(status)
                x=source_original_606540_nonhuman_pending_from_reached(q)
                self.assertEqual(x.original_pending_identity.original_player_id_u16,123)
                self.assertEqual(x.original_pending_identity.original_status_byte,status)
                self.assertEqual(x.original_duration_after_mitigation,
                                 q.prehuman_606540.original_schedule_delta_from_rng)
                self.assertEqual(x.original_rng5_draw_count,0)
                self.assertFalse(x.original_queue_inserted)

    def test_false_native_human_or_forged_stage_rejected(self):
        q=chain()
        corrupted=bytearray(q.prehuman_606540.original_source_descriptor_before_417340)
        corrupted[6]^=1
        for bad in (
            replace(q,original_606540_417340_al=1),
            replace(q,original_606540_417340_al=True),
            replace(q,prehuman_606540=replace(q.prehuman_606540,
                original_source_descriptor_before_417340=bytes(corrupted)),
                original_60aa20_reached=replace(q.original_60aa20_reached,
                    descriptor_before=bytes(corrupted))),
            replace(q,original_60aa20_reached=replace(q.original_60aa20_reached,
                    player_id=456)),
            replace(q,original_60aa20_reached=replace(q.original_60aa20_reached,
                    duration_delta_arg=3)),
            replace(q,original_60aa20_reached=replace(q.original_60aa20_reached,
                    registered_417340_al=1)),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(Original60AA20SourceError):
                    source_original_606540_nonhuman_pending_from_reached(bad)

if __name__=='__main__':
    unittest.main()
