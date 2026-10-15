"""Original 4A8260 two-register scheduled event AL/ticks preserve source order."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import unpack_from
from unittest import TestCase

from original_presults_native_event_work import (
    OriginalPResultsDatedEventReceipt as Receipt,
    OriginalPResultsSourceCallback as Callback,
    OriginalPResultsEventSourceError,
)
from original_presults_two_collection_dispatch import (
    OriginalPResultsTwoCollectionSourceReceipt,
    source_original_4a8260_two_collection_date_callbacks as combine,
    source_original_4a8260_native_progress_counter_receipts as progress,
)


def event(pointer, source_pass):
    return Callback(pointer,source_pass,0x10,0x4a71f0)


def receipt(items,second_return):
    return Receipt(tuple(items),second_return)


class OriginalPResultsTwoCollectionTests(TestCase):
    def test_primary_nonzero_secondary_zero_original_returns_primary_true(self):
        p=receipt((event(0x1000,1),event(0x1000,2)),True)
        s=receipt((event(0x2000,1),),False)
        r=combine(original_primary_947ad8=p,original_secondary_947af0=s)
        self.assertTrue(r.original_4a8260_return_al_nonzero)
        self.assertTrue(r.original_primary_6168c0_return_al_nonzero)
        self.assertFalse(r.original_secondary_6168c0_return_al_nonzero)
        self.assertEqual(tuple((v.original_event_pointer,v.source_pass)
                               for v in r.ordered_source_callbacks),
                         ((0x1000,1),(0x1000,2),(0x2000,1)))
        self.assertFalse(r.original_native_date_event_callbacks_executed)
        self.assertFalse(r.original_game_state_advanced)
        self.assertFalse(r.original_presults_gui_rendered)

    def test_only_second_secondary_al_true_does_not_change_original_return(self):
        p=receipt((event(0x1000,1),),False)
        s=receipt((event(0x2000,2),),True)
        r=combine(original_primary_947ad8=p,original_secondary_947af0=s)
        self.assertFalse(r.original_4a8260_return_al_nonzero)
        self.assertTrue(r.original_secondary_6168c0_return_al_nonzero)
        ticks=progress(original_two_collection_receipt=r,
            original_before_processed_64=1,
            original_first_collection_4a7210_total_68=2)
        self.assertEqual(tuple((v.processed_count,v.total_count)
                               for v in ticks),((2,2),(3,2)))
        self.assertEqual(ticks[0].native_width,800)
        # Actual original +64 increments for the secondary callback even
        # though +68 came from PRIMARY pre-count only. Drawing 1200px
        # from a source 800px image still requires an independent clip proof.
        self.assertEqual(ticks[1].native_width,1200)

    def test_empty_both_orig_collections_do_not_manufacture_tick_or_al(self):
        r=combine(original_primary_947ad8=receipt((),False),
                  original_secondary_947af0=receipt((),False))
        self.assertFalse(r.original_4a8260_return_al_nonzero)
        self.assertEqual(r.ordered_source_callbacks,())
        self.assertEqual(progress(original_two_collection_receipt=r,
            original_before_processed_64=0,
            original_first_collection_4a7210_total_68=0),())

    def test_wrong_native_al_overlap_order_and_counters_fail_closed(self):
        good=dict(original_primary_947ad8=receipt((event(0x1000,1),),False),
                  original_secondary_947af0=receipt((event(0x2000,2),),True))
        bads=(
           dict(original_primary_947ad8=None),
           dict(original_primary_947ad8=receipt((event(0x1000,2),),False)),
           dict(original_primary_947ad8=receipt((event(0x1000,1),),True)),
           dict(original_secondary_947af0=receipt((event(0x1000,2),),True)),
           dict(original_secondary_947af0=receipt((event(0x2000,2),event(0x3000,1)),True)),
           dict(original_secondary_947af0=receipt((Callback(0,1,0x10,0x4a71f0),),False)),
           dict(original_secondary_947af0=receipt((Callback(0x2000,1,8,0x4a71f0),),False)),
           dict(original_secondary_947af0=receipt((event(0x2000,1),),None)),
        )
        for change in bads:
            with self.subTest(change=change),self.assertRaises(OriginalPResultsEventSourceError):
                combine(**(good|change))
        r=combine(**good)
        for changed in (
           {'original_before_processed_64':True},
           {'original_before_processed_64':-1},
           {'original_before_processed_64':0x7fffffff},
           {'original_first_collection_4a7210_total_68':False},
           {'original_first_collection_4a7210_total_68':-1},
           {'original_first_collection_4a7210_total_68':0x80000000},
           {'original_two_collection_receipt':None},
        ):
            with self.subTest(changed=changed),self.assertRaises(OriginalPResultsEventSourceError):
                progress(**(dict(original_two_collection_receipt=r,
                     original_before_processed_64=0,
                     original_first_collection_4a7210_total_68=2)|changed))

    def test_directly_constructed_composite_cannot_override_first_al_or_ordered_events(self):
        from dataclasses import replace
        source=combine(original_primary_947ad8=receipt((event(0x1000,1),),False),
                       original_secondary_947af0=receipt((event(0x2000,2),),True))
        for forged in (replace(source,original_4a8260_return_al_nonzero=True),
                       replace(source,ordered_source_callbacks=()),
                       replace(source,original_secondary_6168c0_return_al_nonzero=False),
                       replace(source,original_native_date_event_callbacks_executed=True)):
            with self.subTest(forged=forged),self.assertRaises(OriginalPResultsEventSourceError):
                progress(original_two_collection_receipt=forged,
                         original_before_processed_64=0,
                         original_first_collection_4a7210_total_68=2)

    def test_canonical_private_pe_4a8260_both_native_registry_calls_and_return_owner(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private actual original executable not provided')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,
            '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x4a8260:'53 b9 d8 7a 94 00',
            0x4a8266:'e8 55 e6 16 00',
            0x4a826b:'b9 f0 7a 94 00',
            0x4a8270:'8a d8',
            0x4a8272:'e8 49 e6 16 00',
            0x4a8277:'8a c3 5b c3',
            0x4a84ea:'8b cf e8 1f ed ff ff',
        }
        for va,h in sites.items():
            with self.subTest(va=hex(va)):
                b=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(b)],b)
        for site,target in ((0x4a8266,0x6168c0),(0x4a8272,0x6168c0),
                            (0x4a84ec,0x4a7210)):
            self.assertEqual(site+5+unpack_from('<i',raw,site-0x400000+1)[0],target)
