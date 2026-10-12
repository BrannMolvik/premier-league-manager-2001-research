"""Recovery544 source-owned DBRUser name persistence, NOT live edit UI acceptance."""
from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace as Obj
from unittest import TestCase, main

from game_state import GameState
from gate13_management_source_data import (
    ManagementPresentationError, ManagementSourceDataBridge,
)
from internal_save import dumps_human_gameplay, loads_human_gameplay
from original_human_user_name import (
    OriginalHumanUserName,
    OriginalHumanUserNameError,
    original_fresh_human_name,
)
from test_human_gameplay import coefficient_matrix
from test_original_eamail_live_user_bridge import OriginalManagerMailDatabase, controller


class NamedSourceDatabase(OriginalManagerMailDatabase):
    managers = tuple(
        Obj(
            index=i,
            first_name=("!Spare" if i == 0 else "Prior"),
            surname=("Placeholder" if i == 0 else "Manager"),
            club_id=(-1 if i == 0 else i),
            formation_default=0, formation_class3=2, formation_class1=1,
        )
        for i in range(21)
    )


class OriginalUserNameRecovery544Tests(TestCase):
    def test_source_initial_name_is_previous_club_manager_not_bang_slot(self):
        game = controller(NamedSourceDatabase)
        saved_rng = game.state.rng.state
        prior_club_manager = game.state.clubs[1].manager_id
        game.select_club(1)
        person = game.state.original_current_human_user_name
        self.assertEqual(person, OriginalHumanUserName(1, 0, "Prior", "Manager"))
        self.assertEqual(game.state.clubs[1].manager_id, prior_club_manager)
        self.assertEqual(game.state.native_user_recipient_key, 0)
        self.assertEqual(game.state.rng.state, saved_rng)
        self.assertEqual(
            ManagementSourceDataBridge(game).source_current_human_manager_name(),
            "Prior Manager",
        )

    def test_original_source_fallback_when_club_had_no_valid_manager(self):
        clubs = {1: Obj(manager_id=1), 2: Obj(manager_id=-1)}
        managers = {
            0: Obj(first_name="!Spare"),
            1: Obj(club_id=-1, first_name="Wrong", surname="Person"),
        }
        self.assertEqual(
            original_fresh_human_name(
                club_id=1, rebound_manager_slot=0, clubs=clubs, managers=managers
            ).source_manager_name(), "John Smith",
        )
        self.assertEqual(
            original_fresh_human_name(
                club_id=2, rebound_manager_slot=0, clubs=clubs, managers=managers
            ).source_manager_name(), "John Smith",
        )

    def test_unqualified_name_never_borrows_ai_manager_or_makes_up_name(self):
        game = controller()
        game.select_club(1)
        self.assertIsNone(game.state.original_current_human_user_name)
        with self.assertRaisesRegex(ManagementPresentationError, "name"):
            ManagementSourceDataBridge(game).source_current_human_manager_name()
        self.assertIsNone(original_fresh_human_name(
            club_id=1, rebound_manager_slot=3,
            clubs={1: Obj(manager_id=1)},
            managers={1: Obj(club_id=1, first_name="Old", surname="Surname"),
                      3: Obj(first_name="Not a native slot")},
        ))

    def test_edit_equivalent_first_surname_round_trip_without_claiming_gui(self):
        game = controller(NamedSourceDatabase)
        game.select_club(1)
        original = game.state.original_current_human_user_name
        self.assertIsNotNone(original)
        # Models the source native edit's persisted data values, not a GUI click.
        game.state.original_current_human_user_name = replace(
            original, first_name="Ada", surname="Lovelace",
        )
        saved = dumps_human_gameplay(game)
        copy = loads_human_gameplay(
            NamedSourceDatabase(), coefficient_matrix(), coefficient_matrix(), saved,
        )
        self.assertEqual(copy.state.original_current_human_user_name,
                         game.state.original_current_human_user_name)
        self.assertEqual(
            ManagementSourceDataBridge(copy).source_current_human_manager_name(),
            "Ada Lovelace",
        )

    def test_name_encoding_bounds_and_corrupt_snapshot_fail_closed(self):
        for value in ("A"*32, "First\x00Name", "山田"):
            with self.subTest(value=value):
                with self.assertRaises(OriginalHumanUserNameError):
                    OriginalHumanUserName(1, 0, value, "Last")
        original = OriginalHumanUserName(1, 0, "John", "Smith")
        self.assertEqual(OriginalHumanUserName.restore(original.snapshot()), original)
        for corrupted in (
            {"selected_club_id": 1}, 
            {**original.snapshot(), "rebound_manager_slot": True},
            {**original.snapshot(), "selected_club_id": -1},
        ):
            with self.subTest(corrupted=corrupted):
                with self.assertRaises(OriginalHumanUserNameError):
                    OriginalHumanUserName.restore(corrupted)


if __name__ == "__main__":
    main()
