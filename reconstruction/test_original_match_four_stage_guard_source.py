"""Original four match-stage x87 guard source: all 16 independent masks."""
from hashlib import sha256
from itertools import product
from os import environ
from pathlib import Path
from unittest import TestCase
from original_match_four_stage_guard_source import (
    OriginalMatchStageGuardError,source_original_four_stage_guard_dispatch,
)

class FourIndependentNativeGuardTests(TestCase):
    def test_all_16_original_paths_leave_later_stages_reachable(self):
        skip_targets=(0x5dac05,0x5dae80,0x5db101,0x5db37c)
        enter_targets=(0x5da987,0x5dac1a,0x5dae98,0x5db116)
        for mask in product((0,1),repeat=4):
            with self.subTest(mask=mask):
                ah=tuple(0x40 if s else 0 for s in mask)
                out=source_original_four_stage_guard_dispatch(reached_native_x87_status_ah=ah)
                self.assertEqual(out.native_stage_entries,tuple(skip_targets[i] if s else enter_targets[i] for i,s in enumerate(mask)))
                self.assertEqual(out.common_after_stages,0x5db37c)
                self.assertFalse(out.actual_original_stage_executed)
                self.assertFalse(out.live_game_state_updated)

    def test_unordered_source_ah_is_not_assumed_numeric_zero(self):
        source=source_original_four_stage_guard_dispatch(reached_native_x87_status_ah=(0x45,0x01,0x44,0x05))
        self.assertEqual(source.native_stage_skipped,(True,False,True,False))
        self.assertEqual(source.reached_native_ah_bytes,(0x45,0x01,0x44,0x05))

    def test_absent_or_fake_original_fpu_status_fails_closed(self):
        for invalid in ((0,0,0),[0,0,0,0],(0,0,0,256),(0,0,0,True),(0,0,0,-1),None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(OriginalMatchStageGuardError):
                    source_original_four_stage_guard_dispatch(reached_native_x87_status_ah=invalid)

    def test_optional_canonical_private_exe_four_branch_signatures(self):
        p=environ.get("FM2001_ORIGINAL_EXE")
        if not p:self.skipTest("original executable private, not available in hosted CI")
        pe=Path(p).read_bytes()
        self.assertEqual((len(pe),sha256(pe).hexdigest()),(4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sig={0x5da97c:"df e0",0x5da97e:"f6 c4 40",0x5da981:"0f 85 7e 02 00 00",0x5dac0f:"df e0",0x5dac11:"f6 c4 40",0x5dac14:"0f 85 66 02 00 00",0x5dae8d:"df e0",0x5dae8f:"f6 c4 40",0x5dae92:"0f 85 69 02 00 00",0x5db10b:"df e0",0x5db10d:"f6 c4 40",0x5db110:"0f 85 66 02 00 00"}
        for va,hexcode in sig.items():
            with self.subTest(va=hex(va)):
                want=bytes.fromhex(hexcode)
                self.assertEqual(pe[va-0x400000:va-0x400000+len(want)],want)
