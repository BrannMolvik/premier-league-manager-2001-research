"""Bounded debugger ABI/planning contracts; NOT native capacity initialization proof."""
import ctypes
import unittest

from gate13_native_capacity_watch import (
    ALLOC_RETURN, CONSTRUCTED, IMPORTED, UNCONTROLLED_READ, CAPACITY_OFFSETS,
    CapacityWatchError, DebugEvent, WatchPlan, Wow64Context, arm_writes,
)


class NativeCapacityWatchTests(unittest.TestCase):
    def test_source_qualified_lifecycle_sites(self):
        self.assertEqual((ALLOC_RETURN, CONSTRUCTED, IMPORTED, UNCONTROLLED_READ),
                         (0x40BC14, 0x40BC43, 0x40BA2C, 0x5DA538))
        self.assertEqual(CAPACITY_OFFSETS, (0x13C, 0x140))

    def test_array_cookie_and_stride_not_club_id(self):
        self.assertEqual(WatchPlan(5).club_address(0x100000, 30), 0x100D4C)
        self.assertEqual(WatchPlan(0).club_address(0x100000, 1), 0x100004)

    def test_fail_closed_bounds(self):
        for kwargs in ({'club_index': -1}, {'club_index': True}, {'seconds': 0},
                       {'seconds': 61}, {'max_events': 0}, {'max_events': 4097}):
            with self.subTest(kwargs=kwargs), self.assertRaises(CapacityWatchError):
                WatchPlan(**kwargs)

    def test_allocation_bounds_and_alignment(self):
        for allocation, count in ((0, 6), (0x100001, 6), (0xFFFFFFF0, 6),
                                  (0x100000, 5), (0x100000, 4097)):
            with self.subTest(allocation=allocation, count=count), self.assertRaises(CapacityWatchError):
                WatchPlan().club_address(allocation, count)

    def test_native_wow64_context_layout(self):
        self.assertEqual(ctypes.sizeof(Wow64Context), 716)
        self.assertEqual(Wow64Context.Eip.offset, 184)
        self.assertEqual(Wow64Context.EFlags.offset, 192)
        self.assertEqual(Wow64Context.Dr7.offset, 24)

    @unittest.skipUnless(ctypes.sizeof(ctypes.c_void_p) == 8, '64-bit debugger ABI')
    def test_host_debug_event_layout(self):
        self.assertEqual(ctypes.sizeof(DebugEvent), 176)
        self.assertEqual(DebugEvent.u.offset, 16)

    def test_watch_is_exact_two_dword_writes_not_execute_or_values(self):
        context = Wow64Context()
        context.Eax, context.Eip = 0x12345678, 0x403660
        context.Dr2, context.Dr3, context.Dr6 = 99, 98, 3
        arm_writes(context, 0x100000)
        self.assertEqual((context.Dr0, context.Dr1), (0x10013C, 0x100140))
        self.assertEqual((context.Dr2, context.Dr3, context.Dr6), (0, 0, 0))
        self.assertEqual(context.Dr7, 0xDD0005)
        self.assertEqual((context.Eax, context.Eip), (0x12345678, 0x403660))

    def test_bad_watch_receiver_rejected(self):
        for value in (0, 0x100001, 0xFFFFFFF0):
            with self.subTest(value=value), self.assertRaises(CapacityWatchError):
                arm_writes(Wow64Context(), value)


if __name__ == '__main__':
    unittest.main()
