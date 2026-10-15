"""Private original PE source checks for four scored 5DA250 operand slots."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack, pack_into
from unittest import TestCase
from original_match_four_5da250_argument_source import (
    OriginalFourStage5DA250ArgumentError,
    source_original_four_stage_5da250_arguments,
)

def case(stage,human,a=0.0,b=4.0):
    stack=bytearray(0x40)
    pack_into('<d',stack,0x30,a)
    pack_into('<d',stack,0x38,b)
    user=bytearray(0x10)
    pack_into('<i',user,0x8,-11)
    pack_into('<i',user,0xC,17)
    return dict(source_stage=stage,
        original_stage_stack_before_argument_pushes=bytes(stack),
        original_4037b0_human_gate=human,
        original_selected_user_694_record_if_human=bytes(user) if human else None,
        original_5e48d0_stored_qword_if_directly_copied_to_b=(pack('<d',b) if human or stage==1 else None))

class Four5DA250StageArgumentsTests(TestCase):
    def test_four_human_operand_owners_and_different_stat_offsets(self):
        for stage in range(1,5):
            with self.subTest(stage=stage):
                out=source_original_four_stage_5da250_arguments(**case(stage,True,a=2.0))
                self.assertEqual((out.native_first_qword_a,out.native_second_qword_b),
                    (pack('<d',2.0),pack('<d',4.0)))
                self.assertEqual(out.human_user_694_signed_dword_if_reached,17 if stage<=2 else -11)
                self.assertEqual(out.source_b_owner,'stage-5e48d0-direct')
                self.assertFalse(out.live_game_state_updated)

    def test_nonhuman_stage1_fresh_b_later_stages_carried_unknown(self):
        for stage in range(1,5):
            out=source_original_four_stage_5da250_arguments(**case(stage,False))
            self.assertEqual(out.native_first_qword_a,b'\x00'*8)
            self.assertIsNone(out.human_user_694_signed_dword_if_reached)
            self.assertEqual(out.source_b_owner,'stage-5e48d0-direct'
                if stage==1 else 'stage-stack-retained-origin-unresolved')

    def test_unreached_guessed_inputs_fail_closed(self):
        sample=case(3,True,a=1.0)
        bad=[
            sample|{'source_stage':0}, sample|{'source_stage':True},
            sample|{'original_stage_stack_before_argument_pushes':b''},
            sample|{'original_4037b0_human_gate':1},
            sample|{'original_selected_user_694_record_if_human':None},
            sample|{'original_5e48d0_stored_qword_if_directly_copied_to_b':pack('<d',5)},
            case(2,False)|{'original_5e48d0_stored_qword_if_directly_copied_to_b':pack('<d',4)},
            case(4,False,a=2),
            case(2,False)|{'original_selected_user_694_record_if_human':b'\x00'*16},
        ]
        for p in bad:
            with self.subTest(p=p):
                with self.assertRaises(OriginalFourStage5DA250ArgumentError):
                    source_original_four_stage_5da250_arguments(**p)

    def test_private_original_four_stage_push_and_human_b_source_opcodes(self):
        path=environ.get('FM2001_ORIGINAL_EXE')
        if not path:self.skipTest('private original exe absent in CI')
        raw=Path(path).read_bytes()
        self.assertEqual((len(raw),sha256(raw).hexdigest()),
            (4714541,'833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'))
        sites={
            0x5da995:'6a 00 6a 00 6a 01 50 51 8d 4c 24 34 e8 0a 9a 00 00 8b c8 e8 23 9f 00 00',
            0x5dac28:'6a 00 6a 00 6a 01 51 52 8d 4c 24 34 e8 77 97 00 00 8b c8 e8 90 9c 00 00',
            0x5daea6:'6a 00 6a 00 6a 01 52 50 8d 4c 24 34 e8 f9 94 00 00 8b c8 e8 12 9a 00 00',
            0x5db124:'6a 00 6a 00 6a 01 51 52 8d 4c 24 34 e8 7b 92 00 00 8b c8 e8 94 97 00 00',
            0x5e43d8:'c2 10 00',
            0x5e48d0:'8b 44 24 04 dd 01 85 c0 74 06 dc 35 88 ad 87 00 c2 04 00',
            0x5daae5:'8b 54 24 3c 52 8b 54 24 34',
            0x5daaf2:'8b 44 24 3c 8b 4c 24 38 50 51 dc 4c 24 24 52',
            0x5dab07:'e8 44 f7 ff ff',
            0x5dad62:'8b 4c 24 3c db 44 90 08 8b 54 24 38 8b 44 24 34 51 8b 4c 24 34',
            0x5dad7b:'52 50 51 8b ce dd 5c 24 68',
            0x5dad84:'e8 c7 f4 ff ff',
            0x5dafe1:'8b 54 24 3c 52 8b 54 24 34',
            0x5daff2:'8b 4c 24 38 50 51 dc 4c 24 24 52',
            0x5db003:'e8 48 f2 ff ff',
            0x5db25e:'8b 4c 24 3c db 44 90 08 8b 54 24 38 8b 44 24 34 51 8b 4c 24 34',
            0x5db277:'52 50 51 8b ce dd 5c 24 60',
            0x5db280:'e8 cb ef ff ff',
            0x5da9ad:'dd 5c 24 38',
            0x5da9cb:'db 40 0c dc 64 24 38 dd 5c 24 30',
            0x5dac40:'dd 5c 24 20',
            0x5dac57:'89 4c 24 3c',
            0x5dac5d:'89 44 24 38',
            0x5dac6c:'db 40 0c dc 64 24 20 dd 5c 24 30',
            0x5dac79:'c7 44 24 30 00 00 00 00',
            0x5daebe:'dd 5c 24 20',
            0x5daed5:'89 4c 24 38',
            0x5daedb:'89 54 24 3c',
            0x5daeea:'db 40 08 dc 64 24 20 dd 5c 24 30',
            0x5daef7:'c7 44 24 30 00 00 00 00',
            0x5db13c:'dd 5c 24 20',
            0x5db153:'89 4c 24 3c',
            0x5db159:'89 44 24 38',
            0x5db168:'db 40 08 dc 64 24 20 dd 5c 24 30',
            0x5db175:'c7 44 24 30 00 00 00 00',
        }
        for va,seq in sites.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(seq)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(expected)],expected)
