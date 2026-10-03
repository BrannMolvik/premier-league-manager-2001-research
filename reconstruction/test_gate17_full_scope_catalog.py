from types import SimpleNamespace
import unittest

from gate17_full_scope_catalog import (
    Gate17PlayableScopeError,
    derive_original_playable_scope,
    teamselect_visible_league_capacity,
)
from original_front_end_layout import TEAMSELECT_ENGLISH_COUNTRY_ORDER


def country(country_id, name):
    return SimpleNamespace(id=country_id, name=name)


def competition(
    competition_id,
    name,
    country_id,
    order,
    *,
    kind=1,
    parent=None,
):
    return SimpleNamespace(
        id=competition_id,
        name=name,
        country_region_id=country_id,
        initialization_order_value=order,
        runtime_kind_code=kind,
        parent_competition_id=parent,
    )


def club(club_id, name, competition_id):
    return SimpleNamespace(
        index=club_id,
        name=name,
        competition_id=competition_id,
    )


class FakeDatabase:
    def __init__(self, countries, competitions, clubs):
        self.countries = tuple(countries)
        self.competitions = tuple(competitions)
        self.clubs = tuple(clubs)


def full_synthetic_database():
    countries = [
        country(country_id, name)
        for country_id, name in TEAMSELECT_ENGLISH_COUNTRY_ORDER
    ]
    competitions = []
    clubs = []
    next_competition_id = 100
    next_club_id = 1000

    for country_index, (country_id, country_name) in enumerate(
        TEAMSELECT_ENGLISH_COUNTRY_ORDER
    ):
        if country_index == 0:
            root_count = 16
        elif country_index == len(TEAMSELECT_ENGLISH_COUNTRY_ORDER) - 1:
            root_count = 10
        else:
            root_count = 1

        # Reverse source append order while giving unique sort keys. The native
        # filter must still expose initialization-order order.
        local = []
        for league_index in range(root_count):
            competition_id = next_competition_id
            next_competition_id += 1
            local.append(
                competition(
                    competition_id,
                    f"{country_name} League {league_index:02d}",
                    country_id,
                    league_index,
                )
            )
            club_count = 25 if country_index == 0 and league_index == 0 else 2
            for club_index in range(club_count):
                clubs.append(
                    club(
                        next_club_id,
                        f"{country_name} Club {club_index:02d}",
                        competition_id,
                    )
                )
                next_club_id += 1
        competitions.extend(reversed(local))

    # These records are not original TeamSelect root League choices.
    competitions.extend(
        (
            competition(900, "Cup", 26, -100, kind=2),
            competition(901, "Child League", 26, -100, parent=100),
            competition(902, "Foreign League", 200, -100),
        )
    )
    return FakeDatabase(countries, competitions, clubs)


class Gate17FullScopeCatalogTests(unittest.TestCase):
    def test_shared_hierarchy_capacity_matches_original_row_insertion(self):
        self.assertEqual(
            [
                teamselect_visible_league_capacity(index)
                for index in range(len(TEAMSELECT_ENGLISH_COUNTRY_ORDER))
            ],
            [15, 14, 13, 12, 11, 10, 9, 8],
        )
        with self.assertRaises(Gate17PlayableScopeError):
            teamselect_visible_league_capacity(-1)
        with self.assertRaises(Gate17PlayableScopeError):
            teamselect_visible_league_capacity(8)

    def test_catalog_uses_exact_country_order_filters_and_visibility_caps(self):
        scope = derive_original_playable_scope(full_synthetic_database())
        self.assertEqual(
            [(item.country_id, item.name) for item in scope.countries],
            list(TEAMSELECT_ENGLISH_COUNTRY_ORDER),
        )

        england = scope.countries[0]
        self.assertEqual(england.source_root_league_count, 16)
        self.assertEqual(england.visible_league_capacity, 15)
        self.assertEqual(len(england.leagues), 15)
        self.assertEqual(
            [league.name for league in england.leagues[:3]],
            [
                "England League 00",
                "England League 01",
                "England League 02",
            ],
        )
        self.assertFalse(any(league.competition_id in (900, 901, 902) for league in england.leagues))

        belgium = scope.countries[-1]
        self.assertEqual(belgium.source_root_league_count, 10)
        self.assertEqual(belgium.visible_league_capacity, 8)
        self.assertEqual(len(belgium.leagues), 8)

        first_league = england.leagues[0]
        self.assertEqual(first_league.source_club_count, 25)
        self.assertEqual(len(first_league.selectable_club_ids), 24)
        self.assertEqual(
            first_league.selectable_club_names[:3],
            (
                "England Club 00",
                "England Club 01",
                "England Club 02",
            ),
        )

        payload = scope.as_dict()
        self.assertEqual(payload["country_count"], 8)
        self.assertEqual(payload["hierarchy_control_count"], 16)
        self.assertEqual(payload["club_control_count"], 24)
        self.assertEqual(
            payload["visible_league_capacity_by_country"],
            [15, 14, 13, 12, 11, 10, 9, 8],
        )
        self.assertTrue(payload["countries"][0]["league_rows_truncated"])
        self.assertTrue(payload["countries"][0]["leagues"][0]["club_rows_truncated"])

    def test_catalog_digest_is_deterministic(self):
        first = derive_original_playable_scope(full_synthetic_database())
        second = derive_original_playable_scope(full_synthetic_database())
        self.assertEqual(first.catalog_sha256, second.catalog_sha256)
        self.assertEqual(
            first.as_dict()["catalog_sha256"],
            first.catalog_sha256,
        )
        self.assertEqual(len(first.catalog_sha256), 64)

    def test_missing_or_changed_teamselect_country_fails_closed(self):
        database = full_synthetic_database()
        missing = FakeDatabase(
            database.countries[:-1],
            database.competitions,
            database.clubs,
        )
        with self.assertRaisesRegex(
            Gate17PlayableScopeError,
            "canonical TeamSelect country 9 is missing",
        ):
            derive_original_playable_scope(missing)

        changed_countries = list(database.countries)
        changed_countries[0] = country(26, "Changed England")
        changed = FakeDatabase(
            changed_countries,
            database.competitions,
            database.clubs,
        )
        with self.assertRaisesRegex(
            Gate17PlayableScopeError,
            "country name changed",
        ):
            derive_original_playable_scope(changed)

    def test_empty_visible_league_fails_closed(self):
        database = full_synthetic_database()
        # England League 00 is native-order first and therefore visible.
        empty_competition_id = 100
        clubs = [
            item
            for item in database.clubs
            if item.competition_id != empty_competition_id
        ]
        broken = FakeDatabase(database.countries, database.competitions, clubs)
        # The reversed synthetic source makes this league source-visible even
        # though native ordering places it later; derive must reject it rather
        # than emit a catalog entry with no selectable club.
        with self.assertRaisesRegex(
            Gate17PlayableScopeError,
            "has no selectable club",
        ):
            derive_original_playable_scope(broken)


if __name__ == "__main__":
    unittest.main()
