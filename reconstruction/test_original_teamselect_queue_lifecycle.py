"""Original 0x947AA8 event owner: source-only vtable and Continue lifecycle."""
import unittest
from original_teamselect_queue_lifecycle import (
    OriginalQueueLifecycleError,
    OriginalQueueObservedEvent,
    OriginalQueueOwnerProjection,
    original_queue_new_owner,
    project_original_queue_drain,
    project_original_teamselect_continue_clear,
)


class QueueSourceTests(unittest.TestCase):
    def test_original_ctor_writes_enabled_and_empty_head_tail_state(self):
        self.assertEqual(original_queue_new_owner(),
                         OriginalQueueOwnerProjection(1, (), 0, None))

    def test_zero_callback_deletes_nonzero_retains_and_sequential_order(self):
        owner = OriginalQueueOwnerProjection(1, (4, 8, 12), 0, 0)
        traces = (
            OriginalQueueObservedEvent(4, 0, None, 0),
            OriginalQueueObservedEvent(8, 1, 0, 1),
            OriginalQueueObservedEvent(12, 2, 2, 0),
        )
        result = project_original_queue_drain(owner, traces)
        self.assertEqual(result.removed_event_identities, (4, 12))
        self.assertEqual(result.kept_event_identities, (8,))
        self.assertEqual(result.owner.source_event_identities, (8,))
        self.assertEqual(result.virtual_call_order,
                         ((4,4),(4,24),(8,4),(8,4),(8,24),
                          (12,4),(12,4),(12,24)))
        self.assertEqual(owner.source_event_identities, (4,8,12))

    def test_processing_reentrancy_marks_deferred_without_callbacks(self):
        owner = OriginalQueueOwnerProjection(1,(9,11),1,0)
        result = project_original_queue_drain(owner, ())
        self.assertEqual(result.owner,
                         OriginalQueueOwnerProjection(1,(9,11),1,1))
        self.assertEqual(result.virtual_call_order, ())
        self.assertEqual(result.removed_event_identities, ())

    def test_teamselect_continue_disposes_retained_entries_not_reruns_events(self):
        owner = OriginalQueueOwnerProjection(1,(8,14),0,0)
        result = project_original_teamselect_continue_clear(owner)
        self.assertEqual(result.removed_event_identities,(8,14))
        self.assertEqual(result.owner,OriginalQueueOwnerProjection(1,(),0,0))
        self.assertEqual(result.virtual_call_order,())

    def test_invalid_observation_cannot_fabricate_queue_state(self):
        owner=OriginalQueueOwnerProjection(1,(2,),0,0)
        invalid=(
            (),
            (OriginalQueueObservedEvent(9,0,None,0),),
            (OriginalQueueObservedEvent(2,0,0,0),),
            (OriginalQueueObservedEvent(2,1,None,0),),
            (OriginalQueueObservedEvent(2,False,None,0),),
        )
        for trace in invalid:
            with self.subTest(trace=trace):
                with self.assertRaises(OriginalQueueLifecycleError):
                    project_original_queue_drain(owner,trace)
        with self.assertRaises(OriginalQueueLifecycleError):
            project_original_teamselect_continue_clear(
                OriginalQueueOwnerProjection(1,(1,1),0,0))
        with self.assertRaises(OriginalQueueLifecycleError):
            project_original_queue_drain(
                OriginalQueueOwnerProjection(1,(2,),1,0),
                (OriginalQueueObservedEvent(2,0,None,0),))


if __name__ == '__main__':
    unittest.main()
