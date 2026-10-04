import unittest
from gate14_fastview_nested_order import *

class NestedOrderTests(unittest.TestCase):
    def test_league_table_parameterized_counts(self):
        self.assertEqual(league_table_display_row_count(1),1)
        self.assertEqual(league_table_display_row_count(12),12)
        self.assertEqual(league_table_display_row_count(13),7)
        self.assertEqual(league_table_display_row_count(24),12)
        self.assertEqual(league_table_visible_control_count(12),128)
        self.assertEqual(league_table_visible_control_count(13),78)

    def test_team_table_parameterized_counts(self):
        self.assertEqual(team_table_playerrow_count(0),11)
        self.assertEqual(team_table_playerrow_count(11),11)
        self.assertEqual(team_table_playerrow_count(16),16)
        self.assertEqual(team_table_visible_control_count(11),105)
        self.assertEqual(team_table_visible_control_count(16),150)

    def test_phase_tail_is_dynamic_and_appended_as_two_controls(self):
        s=ScoreCompositePhaseTail()
        self.assertEqual(s.visible_controls,5)
        s=s.set_phase()
        self.assertEqual((s.phase_controls,s.visible_controls,s.mutation_generation),(2,7,1))
        s=s.set_phase()
        self.assertEqual((s.phase_controls,s.visible_controls,s.mutation_generation),(2,7,2))
        s=s.clear()
        self.assertEqual((s.phase_controls,s.visible_controls,s.mutation_generation),(0,5,3))

    def test_source_anchors(self):
        self.assertEqual(LEAGUE_TABLE_COMPOSITE_CONSTRUCTOR_VA,0x51E000)
        self.assertEqual(TEAM_TABLE_CONSTRUCTOR_VA,0x524EC0)
        self.assertEqual(TEAM_PLAYERROW_CONSTRUCTOR_VA,0x525DB0)
        self.assertEqual(SCORE_COMPOSITE_FACTORY_VA,0x523CC0)
        self.assertEqual(SCORE_COMPOSITE_NORMAL_CONSTRUCTOR_VA,0x51B740)
        self.assertEqual(SCORE_PHASE_SET_VA,0x51BA30)
        self.assertEqual(SCORE_PHASE_CLEAR_VA,0x51BBE0)

    def test_contract_stays_fail_closed(self):
        c=nested_order_contract()
        self.assertTrue(c["score_phase_tail_runtime_mutation_recovered"])
        self.assertFalse(c["single_immutable_nested_order"])
        self.assertFalse(c["global_fastview_z_order_recovered"])
        self.assertFalse(c["complete_fastview_frame_recovered"])

if __name__=="__main__":
    unittest.main()
