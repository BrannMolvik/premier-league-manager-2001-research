"""Source original LeagueMatch registered team / stat numeric 5DA538 tests."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase

from original_match_5da2f0_team_inputs import (
    OriginalNonManagedMatchInputError,
    original_5da2f0_4037b0_team_registration as membership,
    source_original_5da538_nonmanaged_team_fields as stats,
)
from original_native_417340_registered_user_gate import Original417340ReachedUser as Link


def fixture(*,team_key=0x10041, owner_keys=(), numbers=(17,18,19,20)):
    team=bytearray(0x144)
    pack_into('<I',team,4,team_key)
    for off,val in zip((0x134,0x138,0x13c,0x140),numbers):
        pack_into('<I',team,off,val)
    root=bytearray(0x9d0)
    if owner_keys:
        pack_into('<I',root,0x9cc,0x1000)
    nodes=[]
    for i,key in enumerate(owner_keys):
        ptr=0x1000+i*0x100;userptr=0x5000+i*0x100;ctxptr=0x9000+i*0x100
        node=bytearray(8);user=bytearray(0x5b8);context=bytearray(8)
        pack_into('<I',node,0,userptr)
        pack_into('<I',node,4,ptr+0x100 if i+1<len(owner_keys) else 0)
        pack_into('<I',user,0x5b4,ctxptr)
        pack_into('<I',context,4,key)
        nodes.append(Link(ptr,bytes(node),userptr,bytes(user),ctxptr,bytes(context)))
    return dict(original_team_pointer=0x4000,original_team_record=bytes(team),
                original_874c10_registry_root=bytes(root),original_reached_manager_links=tuple(nodes))


class Original5DA2F0TeamInputsTests(TestCase):
    def test_nonhuman_team_zero_users_and_second_user_wrong_full_club_key(self):
        for owners in ((),(0x41,),(0x2222,0x41)):
            case=fixture(owner_keys=owners)
            got=membership(**case)
            self.assertEqual(got.source_4037b0_return_al,0)
            self.assertIsNone(got.source_matching_registered_user_pointer)
            self.assertEqual(len(got.visited_registered_user_pointers),len(owners))
            numeric=stats(original_registration=got,original_team_pointer=0x4000,
                          original_team_record_after_4037b0=case['original_team_record'])
            self.assertEqual(numeric.source_nonmanaged_double_values_134_138_13c_140,(17.,18.,19.,20.))
            self.assertFalse(numeric.original_match_calculator_invoked)
            self.assertFalse(numeric.game_state_modified)

    def test_exact_full_key_human_stops_before_tail_and_refuses_fallback_numbers(self):
        case=fixture(owner_keys=(0x1111,0x10041,0x2222))
        # Native 4139F0 stops at first matching manager; tail is unreached.
        with self.assertRaises(OriginalNonManagedMatchInputError):
            membership(**case)
        case=fixture(owner_keys=(0x1111,0x10041))
        m=membership(**case)
        self.assertEqual(m.source_4037b0_return_al,1)
        self.assertEqual(m.source_matching_registered_user_pointer,0x5100)
        with self.assertRaises(OriginalNonManagedMatchInputError):
            stats(original_registration=m,original_team_pointer=0x4000,
                  original_team_record_after_4037b0=case['original_team_record'])

    def test_native_unsigned_u32_to_fild_qword_limit_only_first_two(self):
        # In ascending address order +134,+138,+13C,+140;
        # only +13C and +140 are compared to floating 200000.0.
        case=fixture(numbers=(0xffffffff,200001,200000,200001))
        m=membership(**case)
        got=stats(original_registration=m,original_team_pointer=0x4000,
                  original_team_record_after_4037b0=case['original_team_record'])
        self.assertEqual(got.original_team_fields_134_138_13c_140,
                         (0xffffffff,200001,200000,200001))
        self.assertEqual(got.source_nonmanaged_double_values_134_138_13c_140,
                         (4294967295.,200001.,200000.,0.))
        edge=fixture(numbers=(0,0,200001,200000))
        t=stats(original_registration=membership(**edge),original_team_pointer=0x4000,
                original_team_record_after_4037b0=edge['original_team_record'])
        self.assertEqual(t.source_nonmanaged_double_values_134_138_13c_140,(0.,0.,0.,200000.))

    def test_original_registry_broken_link_wrong_context_and_postcall_team_identity_rejected(self):
        case=fixture(owner_keys=(9,))
        root=bytearray(case['original_874c10_registry_root'])
        pack_into('<I',root,0x9cc,0x1100)
        with self.assertRaises(OriginalNonManagedMatchInputError):
            membership(**(case|{'original_874c10_registry_root':bytes(root)}))
        with self.assertRaises(OriginalNonManagedMatchInputError):
            membership(**(case|{'original_reached_manager_links':()}))
        link=case['original_reached_manager_links'][0]
        user=bytearray(link.original_user_record)
        pack_into('<I',user,0x5b4,0)
        wrong=Link(link.original_manager_link_pointer,link.original_manager_link_record,
                   link.original_user_pointer,bytes(user),link.original_user_context_pointer,
                   link.original_user_context_record)
        with self.assertRaises(OriginalNonManagedMatchInputError):
            membership(**(case|{'original_reached_manager_links':(wrong,)}))
        m=membership(**case)
        for ptr,bytesval in ((0x4001,case['original_team_record']),
                             (0x4000,bytes(0x144)),(0x4000,b'')):
            with self.subTest(ptr=ptr,n=len(bytesval)),self.assertRaises(OriginalNonManagedMatchInputError):
                stats(original_registration=m,original_team_pointer=ptr,
                      original_team_record_after_4037b0=bytesval)

    def test_canonical_original_pe_proves_registered_lookup_and_nonmanaged_field_reads(self):
        exe=environ.get('FM2001_ORIGINAL_EXE')
        if not exe:self.skipTest('original private executable unavailable in hosted CI')
        b=Path(exe).read_bytes()
        self.assertEqual((len(b),sha256(b).hexdigest()),(4714541,
          '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        signatures={
            0x4037b0:'51 b9 10 4c 87 00',
            0x4037b6:'e8 25 02 01 00',
            0x4139e0:'8b 44 24 04 8b 40 04 50',
            0x4139f0:'8b 81 cc 09 00 00',
            0x4139fe:'8b 10 8b 92 b4 05 00 00',
            0x413a06:'39 4a 04',
            0x5da31a:'e8 91 94 e2 ff 84 c0',
            0x5da321:'0f 84 11 02 00 00',
            0x5da538:'8b 86 40 01 00 00',
            0x5da56b:'8b 8e 3c 01 00 00',
            0x5da5a7:'8b 96 38 01 00 00',
            0x5da5ad:'8b 86 34 01 00 00',
            0x5da5cf:'8b 4d 08',
        }
        for addr,h in signatures.items():
            with self.subTest(addr=hex(addr)):
                sig=bytes.fromhex(h)
                self.assertEqual(b[addr-0x400000:addr-0x400000+len(sig)],sig)
        for addr,dest in ((0x4037b6,0x4139e0),(0x5da31a,0x4037b0)):
            self.assertEqual(addr+5+unpack_from('<i',b,addr-0x400000+1)[0],dest)
