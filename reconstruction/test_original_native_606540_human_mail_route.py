"""Source native 606540 original human notice -> signed due -> 413020 mailbox owner.

All 15 actual constructor vtables, native 5CE660 type31/30/2 and 413020
jump table entries tested against the private verified original PE when supplied.
No original binary execution or Inbox row creation.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from struct import pack_into,unpack_from
import hashlib,os,unittest

from original_native_606540_human_notice import (
    source_original_606540_human_notice_plan,
)
from original_native_606540_human_mail_route import (
    Original606540HumanDueReached, Original606540HumanMailRouteError,
    source_original_606540_human_notice_due_to_user,_CONSTRUCTORS,
    _TYPE_BY_LOOKUP_FAMILY,_TYPE_CASE_BRANCHES,
)
from original_native_413020_type12_human_route import Original413020ReachedManager
from test_original_native_606540_human_notice import notice as constructor_source


def user_node(pointer, userptr, nextptr, club_key, ctxptr, queueptr):
    node=bytearray(8)
    pack_into("<II",node,0,userptr,nextptr)
    user=bytearray(0x6b8)
    pack_into("<I",user,0x5b4,ctxptr)
    pack_into("<I",user,0x6b4,queueptr)
    ctx=bytearray(0x44)
    pack_into("<I",ctx,0x40,club_key)
    return Original413020ReachedManager(
        pointer,bytes(node),userptr,bytes(user),ctxptr,bytes(ctx))


def source(*,family=0,status=0,subtype=1,recipient=True,lookup=True,
           manager_key=777,now=0):
    ctor=constructor_source(
        first=family==0,second=None if family==0 else family==1,
        status=status,subtype=subtype)
    plan=source_original_606540_human_notice_plan(ctor)
    kind=_TYPE_BY_LOOKUP_FAMILY[family]
    vt,tag=_CONSTRUCTORS[plan.original_selected_constructor_address]
    obj=bytearray(plan.original_constructor_object_size)
    for off,val in (
        (0,vt),(4,0xffffffff),(8,6),(0xc,5),
        (0x10,1),(0x14,manager_key),(0x18,0xffffffff),
        (0x1c,kind),(0x20,plan.original_player_id if kind==2 else 0),
        (0x24,0 if kind==2 else 0xffffffff),
        (0x3c,plan.original_player_id),
        (0x40,plan.original_player_id if kind==2 else manager_key),
    ):
        pack_into("<I",obj,off,val)
    if kind==2:
        pack_into("<I",obj,0x44,manager_key)
    wrapper=bytearray(12)
    pack_into("<III",wrapper,0,0x7bd564,
              plan.original_notice_wrapper_date_raw_u32,0x70000)
    club=bytearray(0x44)
    pack_into("<I",club,4,ctor.original_registered_417340_owner_proof.original_source_club_owner_key)
    pack_into("<I",club,0x40,manager_key)
    world=bytearray(0x9d0)
    nodes=()
    if recipient:
        pack_into("<I",world,0x9cc,0x1000)
        first=user_node(0x1000,0x11000,0x2000,888,0x21000,0x91000)
        second=user_node(0x2000,0x2000,0,manager_key,0x22000,0x92000)
        nodes=(first,second)
    return Original606540HumanDueReached(
        original_construction_source=ctor,
        original_417270_constructor_club_pointer=ctor.original_registered_417340_owner_proof.original_source_club_pointer,
        original_417270_constructor_club_record=bytes(club),
        original_constructed_notice_pointer=0x70000,
        original_constructed_notice_bytes_before_due=bytes(obj),
        original_7bd564_wrapper_pointer=0x80000,
        original_7bd564_wrapper_before_due=bytes(wrapper),
        original_native_current_date_raw_u32=now,
        original_global_874c10_record_at_due=bytes(world),
        original_413020_reached_manager_nodes=nodes,
        original_413020_type_lookup_nonnull_if_reached=lookup if recipient and kind in (30,31) else None,
    )


class Original606540HumanMailTests(unittest.TestCase):
    def test_all_fifteen_original_constructors_have_correct_typed_due_owner(self):
        found=set()
        for family in (0,1,2):
            for subtype in (0,1,2):
                for status in (0,1,2,3):
                    if subtype==2 and status>1:continue
                    with self.subTest(family=family,subtype=subtype,status=status):
                        x=source(family=family,subtype=subtype,status=status)
                        y=source_original_606540_human_notice_due_to_user(x)
                        plan=source_original_606540_human_notice_plan(x.original_construction_source)
                        found.add(y.original_constructor)
                        self.assertEqual(y.original_concrete_notice_vtable,
                                         _CONSTRUCTORS[y.original_constructor][0])
                        self.assertEqual(y.original_native_virtual0c_tag,
                                         _CONSTRUCTORS[y.original_constructor][1])
                        self.assertEqual(y.original_native_type_descriptor,
                                         _TYPE_BY_LOOKUP_FAMILY[family])
                        self.assertEqual(y.original_type_case_address,
                                         _TYPE_CASE_BRANCHES[family])
                        self.assertEqual(y.original_413020_reached_manager_links,(0x1000,0x2000))
                        self.assertEqual(y.original_413020_qualified_recipient_user_pointer,0x2000)
                        self.assertEqual(y.original_413020_candidate_user_queue_pointer,0x92000)
                        self.assertEqual(unpack_from("<I",y.original_source_notice_after_5cfa20,4)[0],
                                         plan.original_notice_wrapper_date_raw_u32)
                        self.assertEqual(unpack_from("<I",y.original_source_due_wrapper_after_5cfa20,8)[0],0)
                        self.assertFalse(y.original_native_5cfa20_executed)
                        self.assertFalse(y.original_native_413020_executed)
                        self.assertFalse(y.original_user_queue_mutated)
                        self.assertFalse(y.original_inbox_row_rendered)
                        self.assertFalse(y.live_game_state_updated)
        self.assertEqual(found,set(_CONSTRUCTORS))

    def test_later_native_413020_lookups_are_independent_from_constructor_time(self):
        for family in (0,1):
            x=source(family=family,lookup=False)
            y=source_original_606540_human_notice_due_to_user(x)
            self.assertTrue(y.original_413020_deferred_lookup_gated_out)
            self.assertIsNone(y.original_413020_qualified_recipient_user_pointer)
            self.assertIsNone(y.original_413020_candidate_user_queue_pointer)
            self.assertEqual(y.original_413020_reached_manager_links,(0x1000,0x2000))
            with self.assertRaisesRegex(Original606540HumanMailRouteError,"later"):
                source_original_606540_human_notice_due_to_user(replace(
                    x,original_413020_type_lookup_nonnull_if_reached=None))
        x=source(family=2)
        with self.assertRaisesRegex(Original606540HumanMailRouteError,"skips"):
            source_original_606540_human_notice_due_to_user(replace(
                x,original_413020_type_lookup_nonnull_if_reached=True))

    def test_missing_user_not_broadcast_or_promoted_to_mail(self):
        for family in (0,1,2):
            x=source(family=family,recipient=False)
            y=source_original_606540_human_notice_due_to_user(x)
            self.assertEqual(y.original_413020_reached_manager_links,())
            self.assertIsNone(y.original_413020_qualified_recipient_user_pointer)
            self.assertIsNone(y.original_413020_candidate_user_queue_pointer)
            self.assertFalse(y.original_inbox_row_rendered)

    def test_owner_vtable_category_type_player_club_and_future_date_guards(self):
        x=source()
        original=x.original_constructed_notice_bytes_before_due
        changed=[]
        for off,new in (
            (0,0x7d1514),(8,4),(0x10,2),(0x14,500),
            (0x1c,30),(0x3c,456),(0x40,33),(0x24,5)
        ):
            raw=bytearray(original)
            pack_into("<I",raw,off,new)
            changed.append(replace(x,original_constructed_notice_bytes_before_due=bytes(raw)))
        club=bytearray(x.original_417270_constructor_club_record)
        pack_into("<I",club,0x40,9)
        changed.append(replace(x,original_417270_constructor_club_record=bytes(club)))
        changed.append(replace(x,original_417270_constructor_club_pointer=0x8888))
        wrapper=bytearray(x.original_7bd564_wrapper_before_due)
        pack_into("<I",wrapper,8,0x65432)
        changed.append(replace(x,original_7bd564_wrapper_before_due=bytes(wrapper)))
        changed.append(replace(x,original_native_current_date_raw_u32=0xfffffffd))
        changed.append(replace(x,original_constructed_notice_bytes_before_due=original[:-1]))
        for bad in changed:
            with self.subTest(bad=bad):
                with self.assertRaises(Original606540HumanMailRouteError):
                    source_original_606540_human_notice_due_to_user(bad)

    def test_original_second_registered_club_association_cannot_be_guessed(self):
        x=source(family=2,status=2)
        r=bytearray(x.original_constructed_notice_bytes_before_due)
        pack_into("<I",r,0x20,124)
        with self.assertRaisesRegex(Original606540HumanMailRouteError,"kind2"):
            source_original_606540_human_notice_due_to_user(replace(
                x,original_constructed_notice_bytes_before_due=bytes(r)))
        r=bytearray(x.original_constructed_notice_bytes_before_due)
        pack_into("<I",r,0x44,999)
        with self.assertRaisesRegex(Original606540HumanMailRouteError,"kind2"):
            source_original_606540_human_notice_due_to_user(replace(
                x,original_constructed_notice_bytes_before_due=bytes(r)))

    def test_user_chain_must_be_complete_typed_first_match_and_no_extra_nodes(self):
        x=source()
        first,second=x.original_413020_reached_manager_nodes
        n=bytearray(first.original_manager_link_record);pack_into("<I",n,4,0x9999)
        for bad in (
            replace(x,original_413020_reached_manager_nodes=(second,)),
            replace(x,original_413020_reached_manager_nodes=(replace(
                first,original_manager_link_record=bytes(n)),second)),
            replace(x,original_413020_reached_manager_nodes=(first,)),
            replace(x,original_413020_reached_manager_nodes=(first,second,second)),
            replace(x,original_413020_reached_manager_nodes=(first,replace(
                second,original_user_pointer=0x8989))),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(Original606540HumanMailRouteError):
                    source_original_606540_human_notice_due_to_user(bad)

    def test_optional_private_original_pe_class_families_and_jump_tables(self):
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:self.skipTest("canonical original executable remains private")
        data=Path(path).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        for ctor,(vtable,tag) in _CONSTRUCTORS.items():
            with self.subTest(ctor=hex(ctor)):
                region=data[ctor-0x400000:ctor-0x400000+145]
                # Native constructor stores exact selected .rdata vtable.
                self.assertIn(bytes((0xc7,0x06))+vtable.to_bytes(4,"little"),region)
                ret=unpack_from("<I",data,vtable-0x400000+12)[0]
                self.assertEqual(data[ret-0x400000:ret-0x400000+6],
                                 b"\xb8"+tag.to_bytes(4,"little")+b"\xc3")
                self.assertEqual(unpack_from("<I",data,vtable-0x400000+16)[0],0x40dfb0)
                self.assertEqual(unpack_from("<I",data,vtable-0x400000+60)[0],0x4093e0)
                self.assertEqual(unpack_from("<I",data,vtable-0x400000+64)[0],0x470ce0)
        # Original 413020 type31/30/2 branch graph; 31 and 30 retest lookup.
        self.assertEqual(data[0x41321f-0x400000:0x413224-0x400000],
                         bytes.fromhex("e8 6c df 0b 00"))
        self.assertEqual(data[0x4130e3-0x400000:0x4130e8-0x400000],
                         bytes.fromhex("e8 28 e0 0b 00"))
        for kind,target in ((31,0x413218),(30,0x4130dc),(2,0x41325a)):
            if kind==2:continue  # signed underflow bypasses switch
            case_byte=data[0x413554-0x400000+kind-8]
            self.assertEqual(unpack_from("<I",data,0x413510-0x400000+4*case_byte)[0],target)


if __name__=="__main__":unittest.main()
