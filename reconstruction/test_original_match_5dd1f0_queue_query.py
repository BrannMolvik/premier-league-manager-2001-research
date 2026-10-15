"""Native 5DD1F0 read-back of original 5DC510/617D70 linked records."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack,pack_into,unpack_from
from unittest import TestCase
from original_match_5dd1f0_queue_query import (
    Original5DD1F0LinkedPayload,Original5DD1F0QueueSourceError,
    source_original_5dd1f0_queue_readback as readback,
)


def record(val,tag,coords=(0,0,0)):
    b=bytearray(0x20)
    pack_into('<dH',b,0,val,tag)
    # The word is at +0x10, not +0x08.
    pack_into('<H',b,0x10,tag)
    pack_into('<iii',b,0x14,*coords)
    return bytes(b)


def query(nodes=(), bounds=((0,0,0),(9,9,9)), word=0x66):
    first=nodes[0].original_wrapper_pointer if nodes else 0
    last=nodes[-1].original_wrapper_pointer if nodes else 0
    h=bytearray(12)
    pack_into('<II',h,4,first,last)
    return dict(original_queue_owner_bytes=bytes(h),original_linked_payload_nodes=nodes,
        original_query_type_dword=word,
        original_signed_lower_triple=tuple(x&0xffffffff for x in bounds[0]),
        original_signed_upper_triple=tuple(x&0xffffffff for x in bounds[1]))


def linked(records):
    out=[]
    for i,(val,tag,coords) in enumerate(records):
        pointer=0x1000+i*0x40
        next_pointer=0x1000+(i+1)*0x40 if i+1<len(records) else 0
        prev_pointer=0x1000+(i-1)*0x40 if i else 0
        data=0x2000+i*0x40
        out.append(Original5DD1F0LinkedPayload(pointer,pack('<III',data,next_pointer,prev_pointer),
                                            data,record(val,tag,coords)))
    return tuple(out)


class Original5DD1F0NativeQueueTests(TestCase):
    def test_empty_original_queue_returns_no_contributions(self):
        r=readback(**query())
        self.assertEqual((r.original_inspected_wrapper_pointers,
            r.original_source_selected_wrapper_pointers,r.original_selected_finite_contributions),((),(),()))
        self.assertFalse(r.native_x87_sum_executed)

    def test_original_type_gate_and_numeric_source_filter(self):
        rows=linked(((1.25,0x66,(1,2,3)),(9.5,0x65,(1,2,3)),
                     (-4.0,0x66,(1,2,3)),(3.75,0x66,(4,0,0)),
                     (2.0,0x66,(9,9,9)),(0.0,0x66,(1,2,3))))
        r=readback(**query(rows,bounds=((1,2,3),(4,0,0))))
        self.assertEqual(r.original_source_selected_wrapper_pointers,
                         (0x1000,0x1000+3*0x40,0x1000+5*0x40))
        self.assertEqual(r.original_selected_finite_contributions,(1.25,3.75,0.))
        self.assertEqual(len(r.original_inspected_wrapper_pointers),6)
        self.assertFalse(r.live_game_state_updated)

    def test_original_signed_lexicographic_comparison_is_not_component_wise(self):
        rows=linked(((1.0,0x66,(3,-200,777)),(2.0,0x66,(-1,900,900)),
                     (3.0,0x66,(2,3,4)),(4.0,0x66,(3,50,0))))
        r=readback(**query(rows,bounds=((2,3,4),(3,40,-30))))
        self.assertEqual(r.original_selected_finite_contributions,(1.0,3.0))
        r=readback(**query(rows,bounds=((-1,0,0),(-1,999,999))))
        self.assertEqual(r.original_selected_finite_contributions,(2.0,))

    def test_reject_incomplete_or_corrupted_source_linkage_and_duplicate_data(self):
        rows=linked(((1.,0x66,(1,1,1)),(2.,0x66,(1,1,2))))
        broken=[
           query(rows[:1]),
           query(rows)|{'original_queue_owner_bytes':bytes(12)},
           query(rows)|{'original_linked_payload_nodes':(rows[1],rows[0])},
           query(rows)|{'original_linked_payload_nodes':(rows[0],rows[0])},
           query(rows)|{'original_linked_payload_nodes':(rows[0],Original5DD1F0LinkedPayload(
                   rows[1].original_wrapper_pointer,rows[1].original_wrapper_bytes,
                   rows[0].original_payload_pointer,rows[0].original_payload_bytes))},
           query(rows)|{'original_linked_payload_nodes':list(rows)},
        ]
        for bad in broken:
            with self.subTest(case=str(bad)[:90]), self.assertRaises(Original5DD1F0QueueSourceError):
                readback(**bad)

    def test_input_validation_and_nonfinite_guard(self):
        for bad in (
            query()|{'original_query_type_dword':False},
            query()|{'original_signed_lower_triple':(0,True,0)},
            query()|{'original_signed_lower_triple':(1,2)},
            query()|{'original_queue_owner_bytes':bytearray(12)},
            query(linked(((float('nan'),0x66,(1,2,3)),))),
            query(linked(((float('inf'),0x66,(1,2,3)),))),
            query(linked(((1.0,0x66,(1,2,3)),)),bounds=((3,0,0),(2,0,0))),
        ):
            with self.subTest(case=str(bad)[:90]), self.assertRaises(Original5DD1F0QueueSourceError):
                readback(**bad)

    def test_original_private_exe_5dd1f0_and_signed_filters(self):
        p=environ.get('FM2001_ORIGINAL_EXE')
        if not p:self.skipTest('private original PE unavailable in hosted CI')
        raw=Path(p).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),(4714541,
          '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        signatures={
            0x5DD1FB:'8b 71 04',
            0x5DD21D:'8b 0e 66 8b 45 08 66 39 41 10',
            0x5DD22D:'6a 00 e8 9c 76 00 00 dc 1d f8 d5 7b 00 df e0 f6 c4 01',
            0x5DD278:'e8 e3 fd 06 00 85 c0 74 47',
            0x5DD2AE:'e8 6d fd 06 00 85 c0 74 11',
            0x5DD2C8:'8b 76 04 85 f6 0f 85 4a ff ff ff',
            0x64D020:'8b 01 8b 54 24 04 3b c2 7e 05',
            0x64D031:'8b 41 04 8b 54 24 08 3b c2 7e 05',
            0x64D043:'8b 41 08 8b 4c 24 0c 3b c1 7e 05',
            0x64D060:'8b 01 8b 54 24 04 3b c2 7d 05',
            0x64D071:'8b 41 04 8b 54 24 08 3b c2 7d 05',
            0x64D083:'8b 41 08 8b 4c 24 0c 3b c1 7d 05',
        }
        for va,h in signatures.items():
            with self.subTest(va=hex(va)):
                data=bytes.fromhex(h)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(data)],data)
        self.assertEqual(unpack_from('<d',raw,0x7BD5F8-0x400000)[0],0.)
