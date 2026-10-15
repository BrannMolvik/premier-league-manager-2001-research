"""Source exact numeric 0x66 original 451021 reader -> 5DC890 -> 5DD1F0."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase

from original_match_451021_numeric66_queue_join import (
    Original451021Numeric66SourceError,
    source_original_451021_match_numeric_66_queue_records as join,
)
from test_original_match_451021_indexed_owner import source_case
from test_original_match_5dd1f0_queue_query import linked,query


def source_inputs(*, records=(), owner=None, ptr=0x9010, bounds=((0,0,0),(9,9,9))):
    owner=owner if owner is not None else source_case(dispatch_word=0x66)
    actual_query=query(linked(records),bounds=bounds)
    return dict(original_reader_writer_owner_kwargs=owner,
       original_queue_pointer_at_5dc890=ptr,
       original_queue_owner_bytes_at_5dd1f0=actual_query['original_queue_owner_bytes'],
       original_linked_payload_nodes_at_5dd1f0=actual_query['original_linked_payload_nodes'],
       original_lower_range_triple_at_5dc890=actual_query['original_signed_lower_triple'],
       original_upper_range_triple_at_5dc890=actual_query['original_signed_upper_triple'])


class Original451021Numeric66Tests(TestCase):
    def test_original_66_score_query_selects_only_eligible_linked_records(self):
        s=join(**source_inputs(records=((2.5,0x66,(1,2,3)),
             (3.1,0x65,(1,2,3)),(0.0,0x66,(4,5,6)),
             (-1.0,0x66,(2,2,2)),(7.2,0x66,(20,0,0)))))
        self.assertEqual(s.original_source_5dd1f0_record_selection.original_selected_finite_contributions,(2.5,0.0))
        self.assertEqual(s.original_native_5dc890_selector_word,0x66)
        self.assertEqual((s.original_source_dispatch_branch,s.original_5dd1f0_call_site),(0x5dc8da,0x5dc910))
        self.assertFalse(s.original_source_query_values_independently_reached)
        self.assertFalse(s.original_game_state_updated)

    def test_reader_user_and_queue_snapshot_same_not_live_owner_proof(self):
        owner=source_case(dispatch_word=0x66,slot=0,current_manager_index=1,writer_key=42)
        s=join(**source_inputs(owner=owner,ptr=0x9020))
        self.assertEqual(s.indexed_native_user_queue_source.original_reader_user_pointer,0x2900)
        self.assertFalse(s.indexed_native_user_queue_source.native_snapshot_user_pointers_equal)
        self.assertFalse(s.original_native_x87_total_executed)

    def test_unreached_numeric_categories_and_wrong_queue_pointer_fail(self):
        bad=[
            source_inputs(owner=source_case(dispatch_word=0)),
            source_inputs(owner=source_case(dispatch_word=0x64)),
            source_inputs(owner=source_case(dispatch_word=0xc8)),
            source_inputs(ptr=0x9011),
            source_inputs(ptr=False),
            source_inputs(owner=source_case(slot=1)),
            source_inputs()|{'original_reader_writer_owner_kwargs':None},
            source_inputs()|{'original_lower_range_triple_at_5dc890':(False,0,0)},
        ]
        for case in bad:
            with self.subTest(case=str(case)[:100]),self.assertRaises(ValueError):
                join(**case)

    def test_original_exe_dispatch_0x66_branch_and_argument_stack(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE not available')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,
             '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x451005:'66 8b 51 04',
            0x45100E:'52 e8 bc 29 fc ff',
            0x4139D0:'8b 81 c4 09 00 00 50 e8 34 01 00 00 c3',
            0x45101A:'8b 8c 88 70 06 00 00',
            0x5DC8C3:'83 e8 00',
            0x5DC8CC:'83 e8 64 74 4b',
            0x5DC8D1:'83 e8 02 0f 85 47 08 00 00',
            0x5DC8DA:'8b 4c 24 24',
            0x5DC8F5:'6a 66',
            0x5DC910:'e8 db 08 00 00',
            0x5DC919:'c2 1c 00',
        }
        for va,hexbytes in sites.items():
            with self.subTest(site=hex(va)):
                signature=bytes.fromhex(hexbytes)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(signature)],signature)
        for site,target in ((0x45100F,0x4139D0),(0x451021,0x5DC890),(0x5DC910,0x5DD1F0)):
            off=site-0x400000
            self.assertEqual(raw[off],0xe8)
            self.assertEqual(site+5+unpack_from('<i',raw,off+1)[0],target)
