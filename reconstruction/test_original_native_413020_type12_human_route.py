"""Regression: source original 0x413020 concrete type12 per-human queue owner."""
from __future__ import annotations
from struct import pack_into
import unittest

from original_native_5cfa20_due_event_transfer import (
    source_original_5cfa20_reached_due_transfer,
)
from original_native_413020_type12_human_route import (
    Original413020ManagerRouteError, Original413020ReachedManager,
    source_original_413020_first_human_owner_for_type12,
)


def original_event(team=77, vtable=0x7D1514):
    ev=bytearray(12)
    pack_into("<III",ev,0,0x7BD564,950,0x9000)
    obj=bytearray(0x48)
    pack_into("<I",obj,0,vtable)
    pack_into("<I",obj,0x10,1)
    pack_into("<I",obj,0x14,team)
    pack_into("<I",obj,0x1c,12)
    return source_original_5cfa20_reached_due_transfer(
        original_613ee0_caller_va=0x43216C,
        original_613ee0_processing_date=950,
        original_queue_event_pointer=0x8000,
        original_queue_event_record=bytes(ev),
        original_referenced_pointer=0x9000,
        original_referenced_object_record=bytes(obj),
    )


def global_world(head=0x1000):
    raw=bytearray(0x9d0)
    pack_into("<I",raw,0x9cc,head)
    return bytes(raw)


def manager(nodeptr,userptr,contextptr,team,queue,after=0):
    node=bytearray(8)
    pack_into("<II",node,0,userptr,after)
    user=bytearray(0x6b8)
    pack_into("<I",user,0x5b4,contextptr)
    pack_into("<I",user,0x6b4,queue)
    context=bytearray(0x44)
    pack_into("<I",context,0x40,team)
    return Original413020ReachedManager(nodeptr,bytes(node),userptr,bytes(user),
                                        contextptr,bytes(context))


def route(steps,*,head=0x1000,trans=None):
    return source_original_413020_first_human_owner_for_type12(
        original_due_transfer=original_event() if trans is None else trans,
        original_global_world_874c10_record=global_world(head),
        original_reached_manager_nodes=tuple(steps),
    )


class OriginalType12HumanOwnerTests(unittest.TestCase):
    def test_first_actual_matched_human_owner_gets_event(self):
        m1=manager(0x1000,0x2000,0x3000,51,0x5000,0x1100)
        m2=manager(0x1100,0x2100,0x3100,77,0x5100)
        r=route((m1,m2))
        self.assertEqual(r.original_visited_manager_nodes,(0x1000,0x1100))
        self.assertEqual(r.original_type12_association_identifier,77)
        self.assertEqual(r.original_selected_user_pointer,0x2100)
        self.assertEqual(r.original_selected_user_event_queue_pointer,0x5100)
        self.assertEqual(r.source_queue_wrapper_size,12)
        self.assertFalse(r.original_wrapper_allocated)
        self.assertFalse(r.player_visible_inbox_delivered)
        self.assertFalse(r.live_game_state_updated)

    def test_first_match_stops_without_inspecting_other_users(self):
        m1=manager(0x1000,0x2000,0x3000,77,0x5000,0x1100)
        m2=manager(0x1100,0x2100,0x3100,77,0x5100)
        r=route((m1,))
        self.assertEqual(r.original_selected_user_pointer,0x2000)
        with self.assertRaisesRegex(Original413020ManagerRouteError,"extra"):
            route((m1,m2))

    def test_userless_and_no_matching_human_route_are_not_mail_delivery(self):
        self.assertIsNone(route((),head=0).original_selected_user_pointer)
        m1=manager(0x1000,0x2000,0x3000,1,0x5000,0x1100)
        m2=manager(0x1100,0x2100,0x3100,2,0x5100)
        r=route((m1,m2))
        self.assertEqual(r.original_visited_manager_nodes,(0x1000,0x1100))
        self.assertIsNone(r.original_selected_user_event_queue_pointer)

    def test_both_585000_and_5853f0_original_event_classes_share_route(self):
        for v in (0x7D1514,0x7D1568):
            with self.subTest(v=hex(v)):
                r=route((manager(0x1000,0x2000,0x3000,77,0x5000),),
                        trans=original_event(vtable=v))
                self.assertEqual(r.original_selected_user_event_queue_pointer,0x5000)

    def test_wrong_global_link_or_unreached_node_rejected(self):
        with self.assertRaisesRegex(Original413020ManagerRouteError,"ended"):
            route(())
        with self.assertRaisesRegex(Original413020ManagerRouteError,"missing/mismatched"):
            route((manager(0x1100,0x2100,0x3100,77,0x5000),))
        with self.assertRaisesRegex(Original413020ManagerRouteError,"cyclic"):
            m=manager(0x1000,0x2000,0x3000,2,0x5000,0x1000)
            route((m,m))

    def test_missing_mapped_queue_and_owner_fields_failclosed(self):
        with self.assertRaisesRegex(Original413020ManagerRouteError,"per-user"):
            route((manager(0x1000,0x2000,0x3000,77,0),))
        with self.assertRaisesRegex(Original413020ManagerRouteError,"through"):
            source_original_413020_first_human_owner_for_type12(
                original_due_transfer=original_event(),
                original_global_world_874c10_record=b"",
                original_reached_manager_nodes=(),
            )
        m=manager(0x1000,0x2000,0x3000,77,0x5000)
        bad=Original413020ReachedManager(0x1000,m.original_manager_link_record,
                                         0x9999,m.original_user_record,
                                         0x3000,m.original_team_context_record)
        with self.assertRaisesRegex(Original413020ManagerRouteError,"identity mismatch"):
            route((bad,))

    def test_non_concrete_category_or_subtype_disallowed(self):
        t=original_event()
        from dataclasses import replace
        mutated=bytearray(t.original_referenced_after_5cfa20)
        pack_into("<I",mutated,0x1c,11)
        with self.assertRaisesRegex(Original413020ManagerRouteError,"category1/type12"):
            route((manager(0x1000,0x2000,0x3000,77,0x5000),),
                  trans=replace(t,original_referenced_after_5cfa20=bytes(mutated)))


if __name__ == "__main__":
    unittest.main()
