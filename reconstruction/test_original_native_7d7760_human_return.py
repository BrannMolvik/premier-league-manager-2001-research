"""Original 7D7760 expiry event constructs DIFFERENT recovery notice first.

Unit expected values come from private canonical original 5D7B40 x86 and
EnglishEAM.str/idx source, not the modern port's previous injury logic.
Native callback execution, human delivery and GUI are intentionally false.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from struct import pack_into, unpack_from, pack
from unittest import TestCase, main

from original_native_7d7760_human_return import (
    ORIGINAL_RECOVERY_NOTICE_ROUTES,
    Original7D7760HumanReturnReached,
    Original7D7760ReturnSourceError,
    source_original_7d7760_human_return_from_reached,
)
from original_eamail_language import load_verified_original_eamail_language


def original_reached(*, status=0, player_id=123, human=1,
                     first=True, second=None, day=0, due=0):
    event=bytearray(20)
    pack_into("<IIII",event,0,0x7D7760,due,1,0x60000)
    event[0x10]=status
    # Native malloc leaves these bytes uninitialized; do not invent zeros.
    event[0x11:0x14]=bytes((0xED,0xF0,0x01))
    player=bytearray(0x250)
    pack_into("<H",player,4,player_id)
    pack_into("<I",player,0x14,0x101)
    pack_into("<I",player,0x24C,0x70000)
    club=bytearray(0x44)
    pack_into("<I",club,0x40,777)
    return Original7D7760HumanReturnReached(
        bytes(event),0x60000,pack("<I",player_id),bytes(player),
        day,day,human,
        first if human else None,
        second if human and first is False else None,
        bytes(club) if human else None,
    )


class Original7D7760HumanRecoverySourceTests(TestCase):
    def test_all_three_original_owner_families_and_four_severity_statuses(self):
        self.assertEqual(tuple(ORIGINAL_RECOVERY_NOTICE_ROUTES), (31,30,2))
        actual=set()
        for family,(first,second) in {
            31:(True,None),30:(False,True),2:(False,False),
        }.items():
            for status in range(4):
                with self.subTest(family=family,status=status):
                    candidate=original_reached(
                        human=1,first=first,second=second,status=status)
                    projection=source_original_7d7760_human_return_from_reached(candidate)
                    (constructor,vtable,title,body,idx,body_ids)=(
                        ORIGINAL_RECOVERY_NOTICE_ROUTES[family][status])
                    self.assertEqual((
                        projection.original_selected_family,
                        projection.original_event_status,
                        projection.original_selected_constructor_if_human,
                        projection.original_final_notice_vtable_if_human,
                        projection.original_notice_title_callback_if_human,
                        projection.original_notice_body_callback_if_human,
                        projection.original_eamail_title_idx_if_human,
                        projection.original_eamail_body_ids_if_human,
                        projection.original_recipient_manager_key_if_human,
                    ),(family,status,constructor,vtable,title,body,idx,body_ids,777))
                    self.assertEqual(projection.original_7bd564_notice_wrapper_date_if_human,0)
                    self.assertEqual(projection.original_player_source_cleanup.original_descriptor_pointer_before,
                                     0x70000)
                    clean=projection.original_player_source_cleanup.original_player_after_source
                    self.assertEqual(unpack_from("<I",clean,0x24C)[0],0)
                    self.assertEqual(unpack_from("<I",clean,0x14)[0],0x100)
                    self.assertFalse(projection.original_947aa8_human_event_insert_executed)
                    self.assertFalse(projection.original_native_418ad0_executed)
                    self.assertFalse(projection.original_user_inbox_delivered)
                    self.assertFalse(projection.live_game_state_updated)
                    actual.add((family,status))
        self.assertEqual(len(actual),12)

    def test_original_ai_path_skips_recovery_notice_but_still_clears_injury(self):
        candidate=original_reached(human=0,status=3)
        receipt=source_original_7d7760_human_return_from_reached(candidate)
        self.assertFalse(receipt.original_registered_human)
        self.assertIsNone(receipt.original_selected_constructor_if_human)
        self.assertIsNone(receipt.original_7bd564_notice_wrapper_date_if_human)
        self.assertEqual(unpack_from("<I",
                         receipt.original_player_source_cleanup.original_player_after_source,
                         0x24C)[0],0)

    def test_due_signed_native_date_and_separate_envelope_creation_day(self):
        first=original_reached(day=0xFFFFFFFF,due=0xFFFFFFFE)
        r=source_original_7d7760_human_return_from_reached(first)
        self.assertEqual(r.original_source_due_day_signed,-2)
        self.assertEqual(r.original_source_current_day_signed,-1)
        self.assertEqual(r.original_7bd564_notice_wrapper_date_if_human,0xFFFFFFFF)
        future=original_reached(day=0xFFFFFFFD,due=0xFFFFFFFE)
        with self.assertRaisesRegex(Original7D7760ReturnSourceError,"future"):
            source_original_7d7760_human_return_from_reached(future)

    def test_original_source_metadata_is_not_a_fabricated_gui_mail_body(self):
        lang=load_verified_original_eamail_language(
            Path(__file__).resolve().parent.parent / "original_assets" / "source")
        ids=set()
        for family, cases in ORIGINAL_RECOVERY_NOTICE_ROUTES.items():
            for constructor,vtable,title,body,idx,body_ids in cases:
                with self.subTest(family=family,constructor=hex(constructor)):
                    self.assertEqual(lang.index.string_ids[idx],1407)
                    self.assertEqual(lang.strings[1407],"{PLAYERNAME:1} recovery")
                    self.assertEqual(tuple(lang.index.string_ids[idx+i] for i in (1,2,3)),
                                     body_ids)
                    ids.update(body_ids)
                    self.assertNotIn("{PLAYERNAME:1} recovery",str(body_ids))
        # Native family 30/status0 has a DISTINCT body at arg0 vs arg1/2.
        self.assertEqual(ORIGINAL_RECOVERY_NOTICE_ROUTES[30][0][5],
                         (1408,1409,1409))
        self.assertTrue(len(ids)>12)

    def test_source_owner_and_invalid_event_fail_closed(self):
        good=original_reached()
        bads=[
            replace(good,original_4139e0_human_club_lookup_al=True),
            replace(good,original_4139e0_human_club_lookup_al=2),
            replace(good,original_4d1190_lookup_nonnull_if_reached=None),
            replace(good,original_4d1110_lookup_nonnull_if_reached=True),
            replace(good,original_417270_source_club_record_if_reached=None),
            replace(good,original_player_id_payload_bytes=pack("<I",124)),
            replace(good,original_player_id_payload_pointer=0x60004),
            replace(good,original_player_before_due=good.original_player_before_due[:-1]),
            replace(good,original_native_event_bytes=good.original_native_event_bytes[:-1]),
            replace(good,original_native_scanner_target_date_raw=-1),
        ]
        for x in bads:
            with self.subTest(bad=x):
                with self.assertRaises(Original7D7760ReturnSourceError):
                    source_original_7d7760_human_return_from_reached(x)
        event=bytearray(good.original_native_event_bytes)
        pack_into("<I",event,8,2)
        with self.assertRaisesRegex(Original7D7760ReturnSourceError,"count"):
            source_original_7d7760_human_return_from_reached(
                replace(good,original_native_event_bytes=bytes(event)))
        event=bytearray(good.original_native_event_bytes)
        event[0x10]=4
        with self.assertRaises(Original7D7760ReturnSourceError):
            source_original_7d7760_human_return_from_reached(
                replace(good,original_native_event_bytes=bytes(event)))

    def test_all_36_original_return_body_variants_from_source_bytes(self):
        from original_native_7d7760_return_language import (
            source_original_7d7760_recovery_templates,
        )
        lang=load_verified_original_eamail_language(
            Path(__file__).resolve().parent.parent / "original_assets" / "source")
        cases=0
        for family,(first,second) in {
            31:(True,None),30:(False,True),2:(False,False),
        }.items():
            for status in range(4):
                receipt=source_original_7d7760_human_return_from_reached(
                    original_reached(status=status,first=first,second=second))
                for variant in range(3):
                    with self.subTest(family=family,status=status,variant=variant):
                        output=source_original_7d7760_recovery_templates(
                            receipt,lang,native_body_variant=variant)
                        self.assertEqual(output.original_title_template,
                                         "{PLAYERNAME:1} recovery")
                        self.assertEqual(output.original_body_template,
                                         lang.strings[
                                            ORIGINAL_RECOVERY_NOTICE_ROUTES[family][status][5][variant]
                                         ])
                        self.assertFalse(output.original_rendered_or_delivered)
                        cases+=1
        self.assertEqual(cases,36)

    def test_forged_original_return_body_and_selector_fail_closed(self):
        from original_native_7d7760_return_language import (
            OriginalRecoveryNoticeLanguageError,
            source_original_7d7760_recovery_templates,
        )
        lang=load_verified_original_eamail_language(
            Path(__file__).resolve().parent.parent / "original_assets" / "source")
        receipt=source_original_7d7760_human_return_from_reached(original_reached())
        for invalid in (None,1.0,True,-1,3,"0"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(OriginalRecoveryNoticeLanguageError):
                    source_original_7d7760_recovery_templates(
                        receipt,lang,native_body_variant=invalid)
        for forged in (
            replace(receipt,original_final_notice_vtable_if_human=0x7D7760),
            replace(receipt,original_selected_constructor_if_human=0x59EFA0),
            replace(receipt,original_947aa8_human_event_insert_executed=True),
        ):
            with self.assertRaises(OriginalRecoveryNoticeLanguageError):
                source_original_7d7760_recovery_templates(
                    forged,lang,native_body_variant=0)
        from dataclasses import replace as replaced
        index=list(lang.index.string_ids)
        index[2329]=942
        bad=replaced(lang,index=replaced(lang.index,string_ids=tuple(index)))
        with self.assertRaises(OriginalRecoveryNoticeLanguageError):
            source_original_7d7760_recovery_templates(
                receipt,bad,native_body_variant=0)
        strings=list(lang.strings.strings)
        strings[1411]="Changed message"
        bad=replaced(lang,strings=replaced(lang.strings,strings=tuple(strings)))
        with self.assertRaises(OriginalRecoveryNoticeLanguageError):
            source_original_7d7760_recovery_templates(
                receipt,bad,native_body_variant=0)

    def test_optional_exact_original_pe_constructor_vtables_and_titles(self):
        import os
        from hashlib import sha256
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:
            self.skipTest("Private original executable unavailable on CI")
        executable=Path(path).read_bytes()
        self.assertEqual(sha256(executable).hexdigest(),
                         "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        status_tables={31:0x5D8108,30:0x5D8118,2:0x5D8128}
        jumps={
            31:(0x5D7BEF,0x5D7C4B,0x5D7CA8,0x5D7D04),
            30:(0x5D7D99,0x5D7E02,0x5D7E5B,0x5D7EB7),
            2:(0x5D7F24,0x5D7F81,0x5D7FDE,0x5D8038),
        }
        for family,table in status_tables.items():
            self.assertEqual(unpack_from("<4I",executable,table-0x400000),
                             jumps[family])
            for status,route in enumerate(ORIGINAL_RECOVERY_NOTICE_ROUTES[family]):
                constructor,vtable,title,body,idx,body_ids=route
                with self.subTest(family=family,status=status):
                    self.assertEqual(
                        unpack_from("<II",executable,vtable-0x400000+24),
                        (title,body))
                    self.assertIn(pack("<I",0x87AC28-idx*4),
                                  executable[title-0x400000:title-0x400000+140])
                    for i in range(3):
                        self.assertIn(pack("<I",0x87AC28-(idx+i+1)*4),
                                      executable[body-0x400000:body-0x400000+0x250])
        for va,vtable in ((0x5D7D51,0x7CB37C),
                          (0x5D7F04,0x7CB424),
                          (0x5D8082,0x7CB2D4)):
            self.assertEqual(executable[va-0x400000:va-0x400000+6],
                             bytes.fromhex("c7 03")+pack("<I",vtable))



class Original7D7760MultiEventTests(TestCase):
    """Original 5D7B40 loops event+8 IDs; one unknown member blocks a batch."""

    def build_event(self, *, duplicate=False, malformed_second=False):
        from original_native_7d7760_human_return import (
            Original7D7760ReturnMemberReached,
            Original7D7760ReturnMultiReached,
        )
        a=original_reached(player_id=123,first=True,status=2,day=23,due=22)
        b=original_reached(player_id=124,human=0,status=2,day=23,due=22)
        native=bytearray(a.original_native_event_bytes)
        pack_into("<I",native,8,2)
        # Original native bytes +0x11..0x13 remain uninitialized, not zero.
        native[0x11:0x14]=bytes((0xFA,0xEF,0xB3))
        ids=pack("<II",123,123 if duplicate else 124)
        member_a=Original7D7760ReturnMemberReached(
            a.original_player_before_due,a.original_4139e0_human_club_lookup_al,
            a.original_4d1190_lookup_nonnull_if_reached,
            a.original_4d1110_lookup_nonnull_if_reached,
            a.original_417270_source_club_record_if_reached)
        member_b=Original7D7760ReturnMemberReached(
            b.original_player_before_due,b.original_4139e0_human_club_lookup_al,
            b.original_4d1190_lookup_nonnull_if_reached,
            b.original_4d1110_lookup_nonnull_if_reached,
            b.original_417270_source_club_record_if_reached)
        if malformed_second:
            member_b=replace(member_b,original_player_before_due=b"")
        return Original7D7760ReturnMultiReached(
            bytes(native),a.original_player_id_payload_pointer,ids,23,23,
            (member_a,member_b))

    def test_original_two_member_fifo_human_notice_then_ai_cleanup_source(self):
        from original_native_7d7760_human_return import (
            source_original_7d7760_multi_return_from_reached,
        )
        source=self.build_event()
        original_event=source.original_native_event_bytes
        batch=source_original_7d7760_multi_return_from_reached(source)
        self.assertEqual(batch.original_event_count,2)
        self.assertEqual(
            tuple(x.original_player_id for x in batch.original_ordered_player_receipts),
            (123,124))
        human,ai=batch.original_ordered_player_receipts
        self.assertEqual((human.original_event_status,human.original_selected_family),
                         (2,31))
        self.assertEqual(human.original_recipient_manager_key_if_human,777)
        self.assertEqual(human.original_7bd564_notice_wrapper_date_if_human,23)
        self.assertIsNone(ai.original_selected_constructor_if_human)
        self.assertIsNone(ai.original_7bd564_notice_wrapper_date_if_human)
        self.assertEqual(unpack_from("<I",
            ai.original_player_source_cleanup.original_player_after_source,0x24c)[0],0)
        self.assertFalse(batch.original_native_callback_executed)
        self.assertFalse(batch.live_game_state_updated)
        self.assertEqual(source.original_native_event_bytes,original_event)

    def test_multi_event_requires_exact_array_complete_identities_and_due(self):
        from original_native_7d7760_human_return import (
            Original7D7760ReturnSourceError,
            source_original_7d7760_multi_return_from_reached,
        )
        normal=self.build_event()
        errors=[
            (self.build_event(duplicate=True),"duplicate"),
            (self.build_event(malformed_second=True),"identity"),
            (replace(normal,ordered_reached_players=normal.ordered_reached_players[:1]),
             "count"),
            (replace(normal,original_player_id_payload_bytes=pack("<I",123)),
             "count"),
            (replace(normal,original_native_scanner_target_date_raw=21),
             "future"),
        ]
        for bad,fragment in errors:
            with self.subTest(fragment=fragment):
                with self.assertRaisesRegex(Original7D7760ReturnSourceError,fragment):
                    source_original_7d7760_multi_return_from_reached(bad)
        # The existing original constructor creates count1. A count2 event
        # must never pass through the single-reached receipt interface.
        single=original_reached()
        e=bytearray(single.original_native_event_bytes)
        pack_into("<I",e,8,2)
        with self.assertRaisesRegex(Original7D7760ReturnSourceError,"count"):
            source_original_7d7760_human_return_from_reached(
                replace(single,original_native_event_bytes=bytes(e)))


if __name__ == "__main__":
    main()
