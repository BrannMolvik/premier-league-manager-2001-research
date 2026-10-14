"""Original 0x615A60 native source-calendar head insertion, reached-only tests."""
from __future__ import annotations

from dataclasses import replace
from struct import pack_into, unpack_from
import unittest

from original_native_615890_slot_window import (
    source_original_615890_slot_window_from_reached_callbacks,
)
from original_native_615a60_atomic_insertion import (
    NATIVE_PRIMARY_CALENDAR_VA,
    NATIVE_SECONDARY_CALENDAR_VA,
    OriginalNativeCalendarInsertionError,
    source_original_615a60_atomic_link_projection,
    source_original_510ba0_through_615a60_staged_transaction,
)


def registry(base=0x2000, count=12, day_offset=0):
    data=bytearray(16)
    pack_into("<IiIi",data,0,base,count,day_offset,0)
    return bytes(data)


def outer(*, link=0x9000, start=-1):
    raw=bytearray(0x14)
    pack_into("<I",raw,0,0x7C4C24)
    pack_into("<I",raw,8,link)
    pack_into("<I",raw,0x10,start&0xFFFFFFFF)
    return bytes(raw)


def link(*, owner=0x7000, selector=0, vtable=0x7C9FE8, index=-1):
    raw=bytearray(0x1C)
    pack_into("<I",raw,0,vtable)
    pack_into("<I",raw,0x0C,selector)
    pack_into("<I",raw,0x10,index&0xFFFFFFFF)
    pack_into("<I",raw,0x14,owner)
    pack_into("<I",raw,0x18,0xA000)
    return bytes(raw)


def ev(selector=0):
    raw=bytearray(0x10)
    pack_into("<I",raw,0x0C,selector)
    return bytes(raw)


def vector(*, count=12, old_index=8, old_ptr=0x6000):
    raw=bytearray(count*4)
    if old_index is not None:
        pack_into("<I",raw,old_index*4,old_ptr)
    return bytes(raw)


def search(calendar, idx, outcomes):
    return source_original_615890_slot_window_from_reached_callbacks(
        original_calendar_registry=calendar,
        original_requested_index=idx,
        original_reached_615790_al_by_slot=outcomes,
    )


def insertion(*, source_va=NATIVE_PRIMARY_CALENDAR_VA,
              source_reg=None, selected_va=NATIVE_PRIMARY_CALENDAR_VA,
              selected_reg=None, source_slots=None, windows=None,
              outside=None, new_link=None, event_record=None,
              current_day=0, **kwargs):
    reg=registry() if source_reg is None else source_reg
    if windows is None:
        windows=(
            search(reg,6,{5:0,6:1}),
            search(reg,8,{7:0,8:0,9:0}),
        )
    defaults=dict(
        original_source_calendar_va=source_va,
        original_source_calendar_record=reg,
        original_selected_calendar_va=selected_va,
        original_selected_calendar_record=(
            reg if selected_reg is None else selected_reg),
        original_source_slot_vector=(
            vector() if source_slots is None else source_slots),
        original_global_day_9847fc=current_day,
        original_outer_node_pointer=0x7000,
        original_outer_node_after_510ba0=(
            outer() if outside is None else outside),
        original_inserted_link_pointer=0x9000,
        original_inserted_link_after_510380=(
            link(selector=int(source_va==NATIVE_SECONDARY_CALENDAR_VA))
            if new_link is None else new_link),
        original_reached_virtual18_event_pointer=0xA000,
        original_event_record_after_virtual18=(
            ev(selector=int(selected_va==NATIVE_SECONDARY_CALENDAR_VA))
            if event_record is None else event_record),
        original_reached_615890_windows=windows,
    )
    defaults.update(kwargs)
    return source_original_615a60_atomic_link_projection(**defaults)


class OriginalCalendarInsertion615A60Tests(unittest.TestCase):
    def test_same_registry_two_searches_slot_head_and_new_link_are_atomic(self):
        old=vector()
        created=link()
        result=insertion()
        self.assertEqual(result.original_requested_index,6)
        self.assertEqual(result.original_first_search_index,6)
        self.assertEqual(result.original_reached_search_indices,(6,8))
        self.assertEqual(result.original_selected_slot_index,8)
        self.assertEqual(result.original_old_slot_head_pointer,0x6000)
        self.assertEqual(result.original_inserted_node_native_signed_index,8)
        self.assertEqual(unpack_from("<I",result.projected_source_slot_vector,32)[0],0x9000)
        self.assertEqual(unpack_from("<I",result.projected_inserted_node_record,4)[0],0x6000)
        self.assertEqual(unpack_from("<i",result.projected_inserted_node_record,0x10)[0],8)
        self.assertEqual(result.projected_source_slot_vector[:32],old[:32])
        self.assertEqual(result.projected_inserted_node_record[0x14:],created[0x14:])
        self.assertFalse(result.native_world_write_committed)
        self.assertFalse(result.original_virtual_callbacks_executed)
        self.assertFalse(result.native_match_completion_proven)

    def test_original_selected_event_calendar_changes_stored_link_index(self):
        selected=registry(base=0x3000)
        result=insertion(selected_va=NATIVE_SECONDARY_CALENDAR_VA,
                         selected_reg=selected)
        self.assertEqual(result.source_calendar_va,NATIVE_PRIMARY_CALENDAR_VA)
        self.assertEqual(result.source_selected_calendar_va,
                         NATIVE_SECONDARY_CALENDAR_VA)
        self.assertEqual(result.original_selected_slot_index,8)
        self.assertEqual(result.original_inserted_node_native_signed_index,-1016)
        self.assertEqual(unpack_from("<I",result.projected_inserted_node_record,0x10)[0],
                         (-1016)&0xFFFFFFFF)

    def test_native_source_secondary_registry_can_insert_in_own_calendar(self):
        source=registry(base=0x3000)
        r=insertion(source_va=NATIVE_SECONDARY_CALENDAR_VA,source_reg=source,
                    selected_va=NATIVE_SECONDARY_CALENDAR_VA,
                    selected_reg=source,
                    windows=(search(source,6,{5:0,6:1}),
                             search(source,8,{7:0,8:0,9:0})))
        self.assertEqual(r.original_inserted_node_native_signed_index,8)

    def test_no_match_and_today_clamp_use_factual_source_start(self):
        source=registry()
        r=insertion(
            windows=(search(source,6,{5:0,6:0,7:0}),),
            source_slots=vector(old_index=6))
        self.assertEqual(r.original_selected_slot_index,6)
        r=insertion(current_day=10,
                    windows=(search(source,11,{10:0,11:0}),),
                    source_slots=vector(old_index=11))
        self.assertEqual(r.original_first_search_index,11)
        self.assertEqual(r.original_selected_slot_index,11)

    def test_false_first_search_then_extra_callbacks_rejected(self):
        reg=registry()
        good=search(reg,6,{5:0,6:0,7:0})
        with self.assertRaisesRegex(OriginalNativeCalendarInsertionError,"first false"):
            insertion(windows=(good,good))

    def test_missing_final_false_window_and_wrong_search_order_rejected(self):
        reg=registry()
        matched=search(reg,6,{5:0,6:1})
        with self.assertRaisesRegex(OriginalNativeCalendarInsertionError,"next search"):
            insertion(windows=(matched,))
        wrong=search(reg,7,{6:0,7:0,8:0})
        with self.assertRaisesRegex(OriginalNativeCalendarInsertionError,"window"):
            insertion(windows=(matched,wrong))
        forged=replace(matched,called_615790_indices=(6,))
        with self.assertRaisesRegex(OriginalNativeCalendarInsertionError,"first match"):
            insertion(windows=(forged,search(reg,8,{7:0,8:0,9:0})))

    def test_source_calendar_selected_owner_mismatch_rejected(self):
        with self.assertRaisesRegex(OriginalNativeCalendarInsertionError,"selected original"):
            insertion(selected_va=NATIVE_SECONDARY_CALENDAR_VA,
                      event_record=ev(0))
        with self.assertRaisesRegex(OriginalNativeCalendarInsertionError,"identical original"):
            insertion(selected_reg=registry(base=0x3000))
        with self.assertRaises(OriginalNativeCalendarInsertionError):
            insertion(source_va=0x947AD0)

    def test_allocated_link_must_be_correct_native_record(self):
        cases=(
            {"new_link":link(vtable=0x7C4D70)},
            {"new_link":link(index=1)},
            {"new_link":link(owner=0x1111)},
            {"new_link":link(selector=1)},
            {"new_link":bytes(0x1B)},
            {"outside":outer(link=0)},
            {"outside":bytes(0x13)},
            {"original_inserted_link_pointer":0x7000},
        )
        for case in cases:
            with self.subTest(case=case):
                with self.assertRaises(OriginalNativeCalendarInsertionError):
                    insertion(**case)

    def test_native_slot_graph_and_header_must_be_source_reachable(self):
        bad=(
            {"source_slots":vector(count=11)},
            {"source_reg":registry(base=0)},
            {"source_reg":registry(count=0)},
            {"source_reg":registry(base=0x2001)},
            {"source_slots":vector(old_index=8,old_ptr=0x9000)},
            {"original_reached_virtual18_event_pointer":None},
            {"event_record":bytes(15)},
            {"current_day":True},
            {"current_day":0x80000000},
            {"windows":()},
            {"windows":"not a sequence"},
            {"max_searches":0},
            {"max_searches":1},
        )
        for case in bad:
            with self.subTest(case=case):
                with self.assertRaises(OriginalNativeCalendarInsertionError):
                    insertion(**case)

    def test_fail_closed_if_final_source_index_outside_slot_vector(self):
        source=registry(count=6)
        # At source request index 6 (outer node+10 is -1),
        # 0x615890 has an empty range, while source 0x615A60 would
        # dereference a slot outside this source registry allocation.
        window=search(source,6,{5:0})
        with self.assertRaisesRegex(OriginalNativeCalendarInsertionError,"outside"):
            insertion(source_reg=source,windows=(window,),
                      source_slots=vector(count=6,old_index=None))


def native_entry_event(flags=0):
    raw=bytearray(0x48)
    pack_into("<I",raw,0x44,flags)
    return bytes(raw)


def full_native_insert(*, reg=None, entry=None, source=None, allocated=None,
                       arg=0, selected_va=NATIVE_PRIMARY_CALENDAR_VA,
                       selected_registry=None, **overrides):
    base=registry() if reg is None else reg
    args=dict(
        original_source_calendar_va=NATIVE_PRIMARY_CALENDAR_VA,
        original_source_calendar_record_before_ctor=base,
        original_selected_calendar_va=selected_va,
        original_selected_calendar_record_before_ctor=(
            base if selected_registry is None else selected_registry),
        original_source_slot_vector=vector(),
        original_global_day_9847fc=0,
        original_outer_node_pointer=0x7000,
        original_outer_node_after_entry_virtual18=(
            outer(link=0) if source is None else source),
        original_entry_virtual18_event_pointer=0xA100,
        original_entry_event_after_virtual18=(
            native_entry_event() if entry is None else entry),
        original_allocator_result_link_pointer=0x9000,
        original_allocator_result_link_bytes=(
            bytes(0x1C) if allocated is None else allocated),
        original_510ba0_caller_argument=arg,
        original_reached_link_virtual18_event_pointer=0xA000,
        original_event_after_link_virtual18=ev(
            selector=int(selected_va==NATIVE_SECONDARY_CALENDAR_VA)),
        original_reached_615890_windows=(
            search(base,6,{5:0,6:1}),
            search(base,8,{7:0,8:0,9:0})),
    )
    args.update(overrides)
    return source_original_510ba0_through_615a60_staged_transaction(**args)


class Original510BA0Through615A60Tests(unittest.TestCase):
    def test_full_native_constructor_counter_and_calendar_link(self):
        initial=bytearray(registry())
        pack_into("<I",initial,0x0C,7)
        link_bytes=bytearray(0x1C)
        link_bytes[5]=0x91
        result=full_native_insert(reg=bytes(initial),
                                  selected_registry=bytes(initial),
                                  allocated=bytes(link_bytes))
        self.assertEqual(
            unpack_from("<I",result.original_outer_node_after_native_link_store,8)[0],
            0x9000)
        self.assertEqual(
            unpack_from("<I",result.original_source_registry_after_counter_increment,0xC)[0],
            8)
        made=result.original_link_insertion.projected_inserted_node_record
        self.assertEqual(unpack_from("<I",made,0)[0],0x7C9FE8)
        self.assertEqual(unpack_from("<I",made,0x0C)[0],14)
        self.assertEqual(unpack_from("<I",made,0x10)[0],8)
        self.assertEqual(unpack_from("<I",made,0x14)[0],0x7000)
        self.assertEqual(unpack_from("<I",made,0x18)[0],0)
        self.assertEqual(made[5],0x91)
        self.assertEqual(unpack_from("<I",
            result.original_link_insertion.projected_source_slot_vector,32)[0],0x9000)
        self.assertFalse(result.native_world_write_committed)
        self.assertFalse(result.original_allocator_effects_proven)

    def test_full_native_cross_calendar_preserves_source_owner(self):
        result=full_native_insert(
            selected_va=NATIVE_SECONDARY_CALENDAR_VA,
            selected_registry=registry(base=0x3000))
        self.assertEqual(
            result.original_link_insertion.original_inserted_node_native_signed_index,
            -1016)
        self.assertEqual(unpack_from("<I",
            result.original_source_registry_after_counter_increment,0xC)[0],1)

    def test_full_native_source_gate_and_allocator_fail_closed(self):
        wrong=bytearray(outer(link=0))
        pack_into("<I",wrong,0xC,1)
        cases=(
            {"entry":native_entry_event(0x40)},
            {"source":outer(link=0x9000)},
            {"source":bytes(wrong)},
            {"allocated":bytes(0x1B)},
            {"arg":-1},
            {"arg":0x100000000},
            {"arg":True},
            {"original_allocator_result_link_pointer":0},
            {"original_entry_virtual18_event_pointer":None},
            {"original_entry_event_after_virtual18":bytes(0x47)},
            {"original_outer_node_pointer":0},
            {"selected_registry":registry(base=0x3000)},
        )
        for kw in cases:
            with self.subTest(kwargs=kw):
                with self.assertRaises(OriginalNativeCalendarInsertionError):
                    full_native_insert(**kw)


if __name__=="__main__":
    unittest.main()
