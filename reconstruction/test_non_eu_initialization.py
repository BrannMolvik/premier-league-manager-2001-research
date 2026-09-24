import unittest
from dataclasses import dataclass
from datetime import date

from game_state import GameState
from runtime_state import (
    GERMANY_COUNTRY_ID,
    PLAYER_EU_STATUS_EU,
    PLAYER_EU_STATUS_NON_EU,
    derive_non_eu_status,
)


@dataclass(frozen=True)
class Country:
    nationality_id: int
    european_index: int
    eu_status_flag: int


class NonEuPredicateTests(unittest.TestCase):
    def test_normal_club_non_eu_status_uses_country_eu_flag(self):
        brazil = Country(11, 0, 0)
        france = Country(31, 4, 1)

        self.assertTrue(
            derive_non_eu_status(26, PLAYER_EU_STATUS_NON_EU, brazil)
        )
        self.assertFalse(
            derive_non_eu_status(26, PLAYER_EU_STATUS_NON_EU, france)
        )

    def test_editor_eu_status_exempts_normal_club_path(self):
        brazil = Country(11, 0, 0)
        self.assertFalse(
            derive_non_eu_status(26, PLAYER_EU_STATUS_EU, brazil)
        )

    def test_unresolved_nationality_is_non_eu_on_normal_non_eu_path(self):
        self.assertTrue(
            derive_non_eu_status(26, PLAYER_EU_STATUS_NON_EU, None)
        )

    def test_germany_uses_broader_european_index(self):
        ukraine = Country(80, 17, 0)
        brazil = Country(11, 0, 0)

        self.assertFalse(
            derive_non_eu_status(
                GERMANY_COUNTRY_ID,
                PLAYER_EU_STATUS_NON_EU,
                ukraine,
            )
        )
        self.assertTrue(
            derive_non_eu_status(
                GERMANY_COUNTRY_ID,
                PLAYER_EU_STATUS_EU,
                brazil,
            )
        )

    def test_germany_missing_nationality_is_rejected_as_unsupported_state(self):
        with self.assertRaises(ValueError):
            derive_non_eu_status(
                GERMANY_COUNTRY_ID,
                PLAYER_EU_STATUS_NON_EU,
                None,
            )


@dataclass(frozen=True)
class DatabasePlayer:
    index: int
    club_id: int
    nationality_id: int
    eu_status_code: int
    first_name: str = "Test"
    surname: str = "Player"
    date_of_birth: date | None = date(1980, 1, 1)
    shirt_number: int = 9
    height_cm: int = 180
    weight_kg: int = 75
    positions: tuple[int, int, int] = (19, 0, 0)
    current_raw: tuple[int, ...] = (100,) * 17
    target_raw: tuple[int, ...] = (150,) * 17


@dataclass(frozen=True)
class Club:
    index: int
    country_id: int


class Database:
    def __init__(self):
        self.players = [
            DatabasePlayer(1, 7, 11, PLAYER_EU_STATUS_NON_EU),
            DatabasePlayer(2, 7, 11, PLAYER_EU_STATUS_EU),
            DatabasePlayer(3, 8, 80, PLAYER_EU_STATUS_NON_EU),
        ]
        self.clubs = [
            Club(7, 26),
            Club(8, GERMANY_COUNTRY_ID),
        ]
        self.countries = [
            Country(11, 0, 0),
            Country(80, 17, 0),
        ]
        self.real_fixtures = ()
        self.premier_league_rounds = ()


class GameStateNonEuInitializationTests(unittest.TestCase):
    def test_database_initialization_applies_original_non_eu_predicate(self):
        state = GameState.from_database(
            Database(),
            date(2000, 7, 1),
            seed=1,
        )

        self.assertTrue(state.players[1].non_eu)
        self.assertFalse(state.players[2].non_eu)
        self.assertFalse(state.players[3].non_eu)


if __name__ == "__main__":
    unittest.main()
