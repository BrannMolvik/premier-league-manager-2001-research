"""Original PResults 4A83F0 multi-registered-manager earliest NEXT candidate."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import unpack_from
from unittest import TestCase
from original_presults_multiuser_day_target import (
    OriginalPResultsMultiuserSourceError,
    OriginalPResultsRegisteredMatchCandidate as User,
    source_original_presults_4a83f0_multiuser_target as target,
)


def c(i,on_day=None):
    return User(0x2000+i*0x100,0x6000+i*0x100,
                0 if on_day is None else 0x9000+i*0x100,on_day)


def inputs(items=(c(0,6),)):
    return dict(original_registered_615d10_results=items,
                original_current_date_global_9847fc=2,
                original_max_days_global_87753c=14,
                original_selected_event_510a20_date=6,
                original_no_match_616a30_next_date=None)


class OriginalPResultsMultiUserDayTests(TestCase):
    def test_original_native_1_to_6_humans_earliest_event_wins_and_ties_preserve_first(self):
        for n in range(1,7):
            vals=tuple(c(i,7 if i%2 else 6) for i in range(n))
            r=target(**inputs(vals))
            self.assertEqual((r.earliest_original_manager_ordinal,
                              r.earliest_reached_event_pointer),(0,0x9000))
            self.assertEqual(r.original_selected_registered_user_ordinal_after_loop,0)
            self.assertEqual((r.original_native_target_date_index,
                              r.source_original_precount_4a7210_reached),(5,True))
            self.assertFalse(r.original_world_state_mutated)

    def test_second_human_earlier_target_then_cap_and_same_day_original_branches(self):
        vals=(c(0,12),c(1,5),c(2,5))
        r=target(**(inputs(vals)|{'original_selected_event_510a20_date':5}))
        self.assertEqual((r.earliest_original_manager_ordinal,r.earliest_reached_event_pointer),
                         (1,0x9100))
        self.assertEqual(r.original_native_target_date_index,4)
        capped=target(**(inputs(vals)|{'original_selected_event_510a20_date':5,
                                      'original_max_days_global_87753c':1}))
        self.assertEqual(capped.original_native_target_date_index,3)
        tomorrow=target(**(inputs((c(0,3),))|{'original_selected_event_510a20_date':3}))
        self.assertEqual(tomorrow.original_native_target_date_index,3)
        today=target(**(inputs((c(0,2),))|{'original_selected_event_510a20_date':2}))
        self.assertEqual(today.original_native_target_date_index,2)
        self.assertFalse(today.source_original_precount_4a7210_reached)

    def test_no_human_fixture_uses_actual_original_616a30_next_date_not_synthetic(self):
        val=inputs((c(0),c(1),c(2)))
        val['original_selected_event_510a20_date']=None
        val['original_no_match_616a30_next_date']=9
        s=target(**val)
        self.assertIsNone(s.earliest_original_manager_ordinal)
        self.assertIsNone(s.earliest_reached_event_pointer)
        self.assertEqual(s.original_native_target_date_index,8)
        self.assertEqual(s.original_selected_registered_user_ordinal_after_loop,0)

    def test_invalid_source_manager_registry_result_or_bypass_is_rejected(self):
        v=inputs()
        cases=[
            {'original_registered_615d10_results':()},
            {'original_registered_615d10_results':(c(0),)*2},
            {'original_registered_615d10_results':(c(0),)*7},
            {'original_registered_615d10_results':(dict(),)},
            {'original_registered_615d10_results':(c(0),)},
            {'original_selected_event_510a20_date':None},
            {'original_no_match_616a30_next_date':5},
            {'original_current_date_global_9847fc':True},
            {'original_current_date_global_9847fc':0x7fffffff,
             'original_max_days_global_87753c':1},
            {'original_max_days_global_87753c':-1},
            {'original_selected_event_510a20_date':True},
        ]
        for change in cases:
            with self.subTest(change=change),self.assertRaises(OriginalPResultsMultiuserSourceError):
                target(**(v|change))
        for kwargs in (
            dict(native_registered_user_pointer=0,native_user_5b4_club_pointer=1,
                 source_615d10_event_pointer=0,source_event10_date_slot=None),
            dict(native_registered_user_pointer=1,native_user_5b4_club_pointer=1,
                 source_615d10_event_pointer=0,source_event10_date_slot=7),
            dict(native_registered_user_pointer=1,native_user_5b4_club_pointer=1,
                 source_615d10_event_pointer=0x9000,source_event10_date_slot=None),
        ):
            with self.assertRaises(OriginalPResultsMultiuserSourceError):
                User(**kwargs)

    def test_private_original_pe_proves_exact_4a83f0_full_manager_source_loop(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE unavailable in hosted CI')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,
             '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x4a8435:'89 1d d4 55 87 00',
            0x4a843b:'b9 10 4c 87 00 e8 8b b5 f6 ff',
            0x4a844b:'8b 80 b4 05 00 00',
            0x4a8455:'b9 d8 7a 94 00 e8 b1 d8 16 00',
            0x4a8467:'8b 56 10 8b 48 10 3b d1 7e 02',
            0x4a8473:'a1 d4 55 87 00 40 99',
            0x4a847a:'f7 3d e4 55 87 00',
            0x4a8495:'e8 86 85 06 00',
            0x4a84b8:'b9 d8 7a 94 00 50 e8 6d e5 16 00',
            0x4a84d2:'8b 15 3c 75 87 00 8d 04 0a 3b e8',
            0x4a84e9:'55 8b cf e8 1f ed ff ff',
        }
        for va,h in sites.items():
            with self.subTest(va=hex(va)):
                b=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
        for call,expected in ((0x4a8440,0x4139d0),(0x4a845a,0x615d10),
                              (0x4a8495,0x510a20),(0x4a84be,0x616a30),
                              (0x4a84ec,0x4a7210)):
            with self.subTest(call=hex(call)):
                self.assertEqual(raw[call-0x400000],0xe8)
                self.assertEqual(call+5+unpack_from('<i',raw,call-0x400000+1)[0],expected)
