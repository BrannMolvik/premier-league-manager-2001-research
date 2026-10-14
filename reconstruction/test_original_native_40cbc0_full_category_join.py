"""Complete original source chain: 40CBC0 club -> 4FA510 group -> 4FA520."""
from unittest import TestCase
from original_native_40cbc0_full_category_join import (
    Original40CBC0FullCategoryError,source_original_40cbc0_full_linked_category,
)
from test_original_native_40cbc0_query_category_join import fixture as route_fixture
from test_original_native_4fa510_group_source import fixture as group_fixture

def reached(matches=(3,)):
    route=route_fixture()
    group=group_fixture(matches=matches)
    group['original_4fa510_ecx_object_pointer']=0x30100
    group['original_4fa510_object_bytes']=route['original_4fa520_category_input']['original_4fa520_object_record']
    return dict(original_40cbc0_reached_query_category_inputs=route,
                original_4fa510_group_source_inputs=group)

class SourceOriginalFullCategoryTests(TestCase):
    def test_reached_native_group_category_three_remaps_to_two(self):
        result=source_original_40cbc0_full_linked_category(**reached())
        self.assertEqual(result.source_native_group.original_4fa510_returned_eax,3)
        self.assertEqual(result.source_first_side_route_and_category.original_source_category.original_4fa520_returned_category,2)
        self.assertFalse(result.original_coefficients_written)
        self.assertFalse(result.live_game_state_updated)

    def test_changed_native_group_member_index_cannot_fake_category(self):
        good=reached(matches=(1,))
        with self.assertRaisesRegex(Original40CBC0FullCategoryError,'does not own'):
            source_original_40cbc0_full_linked_category(**good)

    def test_same_numeric_index_from_different_object_fails_closed(self):
        base=reached()
        group=base['original_4fa510_group_source_inputs']
        changed=group|{'original_4fa510_ecx_object_pointer':0x30000}
        with self.assertRaisesRegex(Original40CBC0FullCategoryError,'does not own'):
            source_original_40cbc0_full_linked_category(**(base|{'original_4fa510_group_source_inputs':changed}))
        changed=group|{'original_global_876c50_base_pointer':0x200000,
                       'original_reached_876c50_index_slot_pointer':0x200024}
        with self.assertRaisesRegex(Original40CBC0FullCategoryError,'does not own'):
            source_original_40cbc0_full_linked_category(**(base|{'original_4fa510_group_source_inputs':changed}))

    def test_absent_group_member_produces_negative_one_not_fake_category_three(self):
        state=reached(matches=())
        with self.assertRaisesRegex(Original40CBC0FullCategoryError,'does not own'):
            source_original_40cbc0_full_linked_category(**state)
