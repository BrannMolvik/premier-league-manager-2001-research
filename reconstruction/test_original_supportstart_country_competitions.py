"""Root competition source projections: original static provenance and safe tie boundary."""
import unittest

from fm2001_data import CompetitionDefinition
from original_supportstart_country_competitions import (
    ORIGINAL_STATIC_COMPETITION_COUNT,
    OriginalCompetitionNativeTieError,
    OriginalCompetitionPoolError,
    source_country_competition_candidates,
)


def competition(
    id, *, kind=1, country=7, parent=None, source_order=0
):
    return CompetitionDefinition(
        id=id, name=f"Source {id}", substitute_quota=3,
        max_non_eu_players=0,
        runtime_kind_code=kind,
        country_region_id=country,
        parent_competition_id=parent,
        initialization_order_value=source_order,
    )


class OriginalCountryRootCandidatesTests(unittest.TestCase):
    def test_original_country_source_membership_and_strict_sort(self):
        defs = (
            competition(0, kind=1, country=7, source_order=12),
            competition(1, kind=2, country=7, source_order=3),
            competition(2, kind=3, country=7, source_order=20),
            competition(3, kind=1, country=7, parent=0, source_order=4),
            competition(4, kind=1, country=7, source_order=5),
            competition(5, kind=3, country=8, source_order=2),
        )
        groups = source_country_competition_candidates(
            defs, require_shipped_count=False, country_count=9
        )
        self.assertEqual(len(groups), 9)
        self.assertEqual(groups[7].all_root_competition_ids, (0, 1, 2, 4))
        self.assertEqual(groups[7].root_league_dummy_ids, (0, 2, 4))
        self.assertEqual(groups[7].require_native_eligible_order(), (4, 0, 2))
        self.assertEqual(groups[8].require_native_eligible_order(), (5,))
        self.assertEqual(groups[0].require_native_eligible_order(), ())
        self.assertEqual(groups[7].unresolved_ties, ())

    def test_native_qsort_ties_are_not_replaced_by_stable_python_order(self):
        defs = (
            competition(0, kind=1, country=7, source_order=9),
            competition(1, kind=1, country=7, source_order=9),
            competition(2, kind=3, country=7, source_order=9),
        )
        group = source_country_competition_candidates(
            defs, require_shipped_count=False, country_count=9
        )[7]
        self.assertEqual(group.root_league_dummy_ids, (0, 1, 2))
        self.assertIsNone(group.strict_eligible_order_ids)
        self.assertEqual(len(group.unresolved_ties), 1)
        tie = group.unresolved_ties[0]
        self.assertEqual((tie.native_kind, tie.source_initialization_order), (1, 9))
        self.assertEqual(tie.competition_ids, (0, 1))
        with self.assertRaises(OriginalCompetitionNativeTieError):
            group.require_native_eligible_order()

    def test_special_competition_id27_uses_normal_league_kind_for_grouping(self):
        defs = [
            competition(i, kind=2, country=7) for i in range(28)
        ]
        defs[27] = competition(27, kind=1, country=7, source_order=-3)
        group = source_country_competition_candidates(
            defs, require_shipped_count=False, country_count=9
        )[7]
        self.assertEqual(group.root_league_dummy_ids, (27,))
        self.assertEqual(group.require_native_eligible_order(), (27,))

    def test_reject_unknown_or_inconsistent_source_records(self):
        valid = (competition(0), competition(1))
        for items, kwargs in (
            ((competition(1),), {}),
            ((competition(0), competition(0)), {}),
            ((competition(0, country=9),), {}),
            ((competition(0, kind=4),), {}),
            ((competition(0, parent=17),), {}),
            ((competition(0, parent=0),), {}),
            ((competition(0, source_order=32768),), {}),
            (valid, {"country_count": 0}),
            ((), {}),
        ):
            with self.subTest(items=items, kwargs=kwargs):
                with self.assertRaises(OriginalCompetitionPoolError):
                    source_country_competition_candidates(
                        items, require_shipped_count=False,
                        country_count=9, **kwargs
                    )

    def test_original_shipped_corpus_count_guard(self):
        with self.assertRaisesRegex(OriginalCompetitionPoolError, "193"):
            source_country_competition_candidates((competition(0),))
        defs = tuple(competition(i, kind=2) for i in range(
            ORIGINAL_STATIC_COMPETITION_COUNT
        ))
        groups = source_country_competition_candidates(defs)
        self.assertEqual(groups[7].all_root_competition_ids,
                         tuple(range(ORIGINAL_STATIC_COMPETITION_COUNT)))
        self.assertEqual(groups[7].require_native_eligible_order(), ())


if __name__ == "__main__":
    unittest.main()
