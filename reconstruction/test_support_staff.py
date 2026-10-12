import unittest

from match_schedule import MsvcCrtRng
from support_staff import (
    SupportStaffState,
    ORIGINAL_SUPPORT_START_SLOT_COUNT,
    OriginalSupportStartSourceSlot,
    original_teamselect_support_slots,
    generate_fresh_user_support_staff,
    initial_staff_rating_base,
    training_quality_multiplier,
)


class SupportStaffTrainingTests(unittest.TestCase):
    def test_initial_rating_tiers_match_4c9d40(self):
        self.assertEqual(
            [initial_staff_rating_base(value) for value in range(7)],
            [4, 3, 2, 1, 1, 1, 1],
        )

    def test_fresh_premier_league_staff_uses_exact_type_order_and_draws(self):
        rng = MsvcCrtRng(1)

        staff = generate_fresh_user_support_staff(rng, competition_context=6)

        self.assertEqual(
            [(item.staff_type, item.age_like, item.rating) for item in staff],
            [
                (1, 25, 2),
                (2, 29, 2),
                (3, 39, 1),
                (4, 33, 2),
                (5, 45, 2),
                (13, 29, 2),
            ],
        )
        self.assertEqual(rng.state, 0x6DF109FD)
        self.assertTrue(all(item.status == 1 for item in staff))

    def test_youth_coach_precedes_assistant_and_maps_rating_to_quality(self):
        staff = (
            SupportStaffState(2, 35, 5, 1),
            SupportStaffState(3, 40, 2, 1),
        )
        self.assertAlmostEqual(training_quality_multiplier(staff), 1.30)

    def test_status_two_forces_youth_rating_one(self):
        staff = (SupportStaffState(3, 40, 5, 2),)
        self.assertAlmostEqual(training_quality_multiplier(staff), 1.25)

    def test_assistant_fallback_and_training_centre_bonus(self):
        staff = (SupportStaffState(2, 35, 5, 1),)
        self.assertAlmostEqual(training_quality_multiplier(staff), 1.25)
        self.assertAlmostEqual(
            training_quality_multiplier(staff, has_training_centre=True),
            1.50,
        )


    def test_source_teamselect_six_generated_staff_into_seven_selector_records(self):
        # Source 0x4C9CD0 generates 6 and 0x4DA4F0 stages 7 editor rows.
        generated = generate_fresh_user_support_staff(MsvcCrtRng(1), 6)
        staged = original_teamselect_support_slots(generated)
        self.assertEqual(len(generated), 6)
        self.assertEqual(ORIGINAL_SUPPORT_START_SLOT_COUNT, 7)
        self.assertEqual(len(staged), 7)
        self.assertEqual(tuple(row.index for row in staged), tuple(range(7)))
        self.assertEqual(tuple(row.staff is source for row, source in zip(staged, generated)),
                         (True,) * 6)
        self.assertEqual(tuple(row.original_selected_byte for row in staged),
                         (1, 1, 1, 1, 1, 1, None))
        self.assertIsNone(staged[6].staff)

    def test_original_source_list_order_preserved_without_staff_mutation(self):
        first = SupportStaffState(13, 36, 4)
        second = SupportStaffState(2, 31, 5)
        source = (first, second)
        stage = original_teamselect_support_slots(source)
        self.assertIs(stage[0].staff, first)
        self.assertIs(stage[1].staff, second)
        self.assertEqual(tuple(row.staff for row in stage[2:]), (None,) * 5)

    def test_all_seven_source_staff_records_staged_with_no_invented_eighth(self):
        staff = tuple(SupportStaffState(i + 1, 30, 2) for i in range(7))
        slots = original_teamselect_support_slots(staff)
        self.assertEqual([row.staff.staff_type for row in slots], list(range(1, 8)))
        self.assertEqual([row.original_selected_byte for row in slots], [1] * 7)
        with self.assertRaisesRegex(ValueError, "seven pointer"):
            original_teamselect_support_slots(staff + (SupportStaffState(13, 30, 3),))

    def test_native_empty_flags_are_unknown_not_guessed_zero(self):
        empty = original_teamselect_support_slots(())
        self.assertEqual(tuple(row.staff for row in empty), (None,) * 7)
        self.assertEqual(tuple(row.original_selected_byte for row in empty), (None,) * 7)
        with self.assertRaisesRegex(ValueError, "unqualified"):
            OriginalSupportStartSourceSlot(6, None, 0)
        with self.assertRaisesRegex(ValueError, "byte 1"):
            OriginalSupportStartSourceSlot(0, SupportStaffState(2, 31, 2), 0)
        with self.assertRaisesRegex(ValueError, "outside"):
            OriginalSupportStartSourceSlot(7, None, None)

    def test_staff_pointer_is_not_duplicated_or_invented(self):
        person = SupportStaffState(2, 31, 2)
        with self.assertRaisesRegex(ValueError, "multiple selector"):
            original_teamselect_support_slots((person, person))
        with self.assertRaisesRegex(TypeError, "native-list"):
            original_teamselect_support_slots((object(),))

    def test_no_staff_is_neutral_before_facility_bonus(self):
        self.assertAlmostEqual(training_quality_multiplier(()), 1.0)
        self.assertAlmostEqual(
            training_quality_multiplier((), has_training_centre=True),
            1.25,
        )


if __name__ == "__main__":
    unittest.main()
