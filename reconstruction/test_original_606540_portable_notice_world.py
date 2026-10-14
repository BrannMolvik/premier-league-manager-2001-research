"""Source-only portable 606540 pending -> native due -> per-user owner tests.

This test builds original-byte fixture evidence, not a claim that an original
Windows game, true heap callback or physical PEAMail UI was exercised.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from struct import pack, pack_into
from unittest import TestCase, main

from original_native_613ee0_multi_chain import (
    Original613EE0LinkedEvent, Original613EE0MultiChainReached,
)
from original_606540_portable_notice_world import (
    Original606540PortableWorld, Original606540PortableWorldError,
)
from test_original_native_606540_human_mail_route import source


def scan(*reached, today=0):
    header = bytearray(0x14)
    linked = []
    for i, r in enumerate(reached):
        ptr = 0x60000 + 0x1000*i
        nxt = 0x60000 + 0x1000*(i+1) if i+1 < len(reached) else 0
        prev = 0x60000 + 0x1000*(i-1) if i else 0
        linked.append(Original613EE0LinkedEvent(
            ptr,
            pack("<III",r.original_7bd564_wrapper_pointer,nxt,prev),
            r.original_7bd564_wrapper_pointer,
            r.original_7bd564_wrapper_before_due,
        ))
    pack_into("<I",header,0,1)
    if linked:
        pack_into("<II",header,4,linked[0].wrapper_pointer,linked[-1].wrapper_pointer)
    return Original613EE0MultiChainReached(
        bytes(header),tuple(linked),today,0x41A364)


def queued(world, reached):
    return world.append_source_constructor(
        reached.original_construction_source,
        reached_source_club_record=reached.original_417270_constructor_club_record,
        reached_source_club_pointer=reached.original_417270_constructor_club_pointer,
    )


def independent_wrapper(reached, delta):
    """Distinct native transient event/object pointers on a second source item."""
    from struct import unpack_from
    new_notice=reached.original_constructed_notice_pointer+delta
    return replace(
        reached,
        original_constructed_notice_pointer=new_notice,
        original_7bd564_wrapper_pointer=reached.original_7bd564_wrapper_pointer+delta,
        original_7bd564_wrapper_before_due=pack(
            "<III",0x7BD564,
            unpack_from("<I",reached.original_7bd564_wrapper_before_due,4)[0],
            new_notice
        ),
    )


class PortableSourceInjuryNoticeWorldTests(TestCase):
    def test_real_source_constructor_to_registered_user_portable_receipt(self):
        reached=source(family=0,recipient=True,lookup=True)
        initial=Original606540PortableWorld()
        with_pending=queued(initial,reached)
        self.assertEqual(len(with_pending.pending),1)
        self.assertEqual(len(initial.pending),0)
        self.assertEqual(with_pending.pending[0].original_due_day_raw,0)
        self.assertEqual(with_pending.pending[0].original_type,31)
        finished=with_pending.apply_original_due_batch(
            reached_global_scan=scan(reached),
            original_due_notices=((1,reached),),
            registered_manager_keys=(777,),
        )
        self.assertEqual(finished.pending,())
        self.assertEqual(len(finished.user_notices),1)
        item=finished.user_notices[0]
        self.assertEqual((item.serial,item.original_player_id,item.original_type,
                          item.recipient_manager_key,item.original_record_day_raw),
                         (1,with_pending.pending[0].original_player_id,31,777,0))
        self.assertFalse(item.visible_inbox_accepted)
        self.assertEqual(Original606540PortableWorld.restore(finished.snapshot()),finished)

    def test_source_type2_direct_and_30_31_later_lookup_recheck(self):
        for family in (0,1,2):
            with self.subTest(family=family):
                r=source(family=family,recipient=True,lookup=True)
                w=queued(Original606540PortableWorld(),r)
                done=w.apply_original_due_batch(
                    reached_global_scan=scan(r),
                    original_due_notices=((1,r),),
                    registered_manager_keys=(777,),
                )
                self.assertEqual(len(done.user_notices),1)
                self.assertEqual(done.user_notices[0].original_type,(31,30,2)[family])
        for family in (0,1):
            with self.subTest(later_lookup_lost=family):
                r=source(family=family,recipient=True,lookup=False)
                w=queued(Original606540PortableWorld(),r)
                done=w.apply_original_due_batch(
                    reached_global_scan=scan(r),
                    original_due_notices=((1,r),),
                    registered_manager_keys=(777,),
                )
                self.assertEqual(done.pending,())
                self.assertEqual(done.user_notices,())

    def test_unregistered_recipient_does_not_fabricate_a_user_mailbox(self):
        r=source(family=2,recipient=False)
        w=queued(Original606540PortableWorld(),r)
        ended=w.apply_original_due_batch(
            reached_global_scan=scan(r),
            original_due_notices=((1,r),),
            registered_manager_keys=(),
        )
        self.assertEqual(ended.pending,())
        self.assertEqual(ended.user_notices,())
        present=source(family=2,recipient=True)
        w=queued(Original606540PortableWorld(),present)
        with self.assertRaisesRegex(Original606540PortableWorldError,
                                    "registry"):
            w.apply_original_due_batch(
                reached_global_scan=scan(present),
                original_due_notices=((1,present),),
                registered_manager_keys=(),
            )

    def test_two_same_day_events_preserve_source_order_and_transaction(self):
        a=source(family=0,manager_key=777)
        b=independent_wrapper(source(family=2,manager_key=999),0x1000)
        state=queued(queued(Original606540PortableWorld(),a),b)
        self.assertEqual(tuple(x.serial for x in state.pending),(1,2))
        combined=scan(a,b)
        before=deepcopy(state.snapshot())
        with self.assertRaisesRegex(Original606540PortableWorldError,"All due"):
            state.apply_original_due_batch(
                reached_global_scan=combined,
                original_due_notices=((1,a),),
                registered_manager_keys=(777,999),
            )
        self.assertEqual(state.snapshot(),before)
        done=state.apply_original_due_batch(
            reached_global_scan=combined,
            original_due_notices=((1,a),(2,b)),
            registered_manager_keys=(777,999),
        )
        self.assertEqual(tuple(item.recipient_manager_key for item in done.user_notices),
                         (777,999))
        self.assertEqual(tuple(item.serial for item in done.user_notices),(1,2))
        self.assertEqual(Original606540PortableWorld.restore(done.snapshot()),done)

    def test_due_7d7760_player_expiry_never_silently_dropped_from_same_day(self):
        r=source(family=0,manager_key=777)
        state=queued(Original606540PortableWorld(),r)
        world=scan(r)
        first=world.ordered_source_nodes[0]
        link=bytearray(first.wrapper_before)
        pack_into("<I",link,4,0x61000)
        player_expiry=bytearray(20)
        pack_into("<I",player_expiry,0,0x7D7760)
        pack_into("<I",player_expiry,4,0)
        pack_into("<I",player_expiry,8,1)
        pack_into("<I",player_expiry,12,0xB0000)
        second=Original613EE0LinkedEvent(
            0x61000,pack("<III",0x90000,0,0x60000),
            0x90000,bytes(player_expiry),
        )
        header=bytearray(world.global_947aa8_header_before)
        pack_into("<I",header,8,0x61000)
        mixed=replace(
            world,
            global_947aa8_header_before=bytes(header),
            ordered_source_nodes=(replace(first,wrapper_before=bytes(link)),second),
        )
        with self.assertRaisesRegex(Original606540PortableWorldError,"7D7760"):
            state.apply_original_due_batch(
                reached_global_scan=mixed,
                original_due_notices=((1,r),),
                registered_manager_keys=(777,),
            )
        self.assertEqual(state.pending[0].serial,1)
        self.assertEqual(state.user_notices,())

    def test_future_date_is_never_consumed_and_wrong_owner_rolls_back(self):
        r=source(family=0,manager_key=777)
        state=queued(Original606540PortableWorld(),r)
        future_scan=scan(r,today=0xFFFFFFFF)
        unchanged=state.apply_original_due_batch(
            reached_global_scan=future_scan,
            original_due_notices=(),
            registered_manager_keys=(777,),
        )
        # signed current=-1 precedes original due=0
        self.assertEqual(unchanged,state)
        with self.assertRaises(Original606540PortableWorldError):
            state.apply_original_due_batch(
                reached_global_scan=scan(r),
                original_due_notices=((1,replace(
                    r,original_417270_constructor_club_pointer=0xFFFF)),),
                registered_manager_keys=(777,),
            )
        self.assertEqual(len(state.pending),1)
        self.assertEqual(len(state.user_notices),0)

    def test_invalid_saved_identity_vtable_field_and_visibility_fail_closed(self):
        r=source(family=0)
        state=queued(Original606540PortableWorld(),r)
        valid=state.snapshot()
        for key,value in (
            ("original_type",2),
            ("original_class_vtable",0x7D1CE0),
            ("original_creation_manager_key",-1),
            ("original_due_day_raw",0x100000000),
            ("serial",True),
        ):
            corrupted=deepcopy(valid)
            corrupted["pending"][0][key]=value
            with self.subTest(key=key):
                with self.assertRaises(Original606540PortableWorldError):
                    Original606540PortableWorld.restore(corrupted)
        done=state.apply_original_due_batch(
            reached_global_scan=scan(r),
            original_due_notices=((1,r),),
            registered_manager_keys=(777,),
        )
        for forged in (True,1):
            corrupt=done.snapshot()
            corrupt["user_notices"][0]["visible_inbox_accepted"]=forged
            with self.subTest(forged=forged):
                with self.assertRaises(Original606540PortableWorldError):
                    Original606540PortableWorld.restore(corrupt)


if __name__ == "__main__":
    main()
