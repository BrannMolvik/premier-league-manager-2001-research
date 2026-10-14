"""The original PPreMatch four-way route must not become Quick Match."""
from __future__ import annotations

import unittest

from human_gameplay import HumanGameplayController
from match_detail_mode import MatchDetailMode


class NativeMatchModeTransactionGuardTests(unittest.TestCase):
    def test_nonquick_modes_fail_before_cloning_or_changing_pending_world(self):
        # Use a deliberately incomplete owner: entering the original unsupported
        # presentation branch must not access any state/RNG/match simulation.
        for mode in (
            MatchDetailMode.THREE_D_MATCH,
            MatchDetailMode.THREE_D_HIGHLIGHTS,
            MatchDetailMode.FASTVIEW,
        ):
            with self.subTest(mode=mode):
                human=HumanGameplayController.__new__(HumanGameplayController)
                human.pending_primary_entry=("premier_league", 123)
                sentinel=object()
                human.match_rng=sentinel
                human.state=sentinel
                human.attack_matrix=sentinel
                human.defence_matrix=sentinel
                before=dict(human.__dict__)
                with self.assertRaisesRegex(RuntimeError,
                                            "mode-specific match lifecycle"):
                    human.play_original_user_primary_match(mode)
                self.assertEqual(human.__dict__,before)
                self.assertIs(human.match_rng,sentinel)

    def test_invalid_mode_never_mutates_owner(self):
        human=HumanGameplayController.__new__(HumanGameplayController)
        human.pending_primary_entry=("premier_league",123)
        before=dict(human.__dict__)
        for bad in (-1,4,5,None,True,"2"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    human.play_original_user_primary_match(bad)
                self.assertEqual(human.__dict__,before)

    def test_no_pending_match_rejected_before_mode_processing(self):
        human=HumanGameplayController.__new__(HumanGameplayController)
        human.pending_primary_entry=None
        for mode in range(4):
            with self.subTest(mode=mode):
                with self.assertRaisesRegex(RuntimeError,"advance to"):
                    human.play_original_user_primary_match(mode)


if __name__=="__main__":
    unittest.main()
