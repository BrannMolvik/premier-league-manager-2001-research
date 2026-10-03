from pathlib import Path
from types import SimpleNamespace
import unittest

from gate14_fastview_playerrow_from_result import (
    FastViewRetainedPlayerRowError,
    FastViewRetainedPlayerRowIdentity,
    build_fastview_player_rows_from_retained_histories,
)


def history(side_index, player_index, samples):
    return SimpleNamespace(
        side_index=side_index,
        player_index=player_index,
        samples=tuple(samples),
    )


def retained_result():
    condition = (
        history(0, 3, (80,) * 24),
        history(1, 4, (70,) * 24),
    )
    form = (
        history(1, 4, (5, 5, 6) + (6,) * 21),
        history(0, 3, (5, 6, 7) + (7,) * 21),
    )
    return SimpleNamespace(
        fastview_condition_histories=condition,
        fastview_form_histories=form,
    )


def row(
    side_index=0,
    player_index=3,
    row_index=0,
    *,
    surname="Striker",
    first_name_initial="A",
):
    return FastViewRetainedPlayerRowIdentity(
        side_index=side_index,
        player_index=player_index,
        row_index=row_index,
        shirt_number=9,
        source_position_code=19,
        surname=surname,
        first_name_initial=first_name_initial,
    )


class FastViewRetainedPlayerRowTests(unittest.TestCase):
    def test_builds_rows_from_retained_histories_without_replaying_state(self):
        result = retained_result()
        rows = (
            row(0, 3, 0),
            row(1, 4, 1, surname="Keeper", first_name_initial="B"),
        )

        snapshots = build_fastview_player_rows_from_retained_histories(
            result,
            rows,
            global_tick=10,
            energy_rng6_rolls={(0, 3): 3, (1, 4): 3},
        )

        self.assertEqual(
            [(item.side_index, item.row_index) for item in snapshots],
            [(0, 0), (1, 1)],
        )
        self.assertEqual(snapshots[0].form.text, "7")
        self.assertEqual(snapshots[0].energy.energy_value, 76)
        self.assertEqual(snapshots[1].form.text, "6")
        self.assertEqual(snapshots[1].energy.energy_value, 70)
        self.assertEqual(snapshots[0].player_name.text, "A Striker")
        self.assertEqual(snapshots[1].player_name.text, "B Keeper")

    def test_goal_counter_values_are_only_used_when_explicitly_supplied(self):
        result = retained_result()
        identity = FastViewRetainedPlayerRowIdentity(
            side_index=0,
            player_index=3,
            row_index=0,
            shirt_number=10,
            source_position_code=19,
            surname="Forward",
            first_name_initial="C",
            displayed_goal_count=2,
            displayed_own_goal_count=1,
        )

        snapshot = build_fastview_player_rows_from_retained_histories(
            result,
            (identity,),
            global_tick=5,
            energy_rng6_rolls={(0, 3): 0},
        )[0]

        self.assertEqual(snapshot.goal_count.text, "(2)")
        self.assertEqual(snapshot.own_goal_count.text, "(1)")

    def test_result_history_identity_sets_must_match_exactly(self):
        result = retained_result()
        result.fastview_form_histories = result.fastview_form_histories[:1]
        with self.assertRaisesRegex(
            FastViewRetainedPlayerRowError,
            "identities differ",
        ):
            build_fastview_player_rows_from_retained_histories(
                result,
                (row(),),
                global_tick=0,
                energy_rng6_rolls={(0, 3): 0},
            )

    def test_duplicate_retained_history_identity_fails_closed(self):
        result = retained_result()
        duplicate = result.fastview_condition_histories[0]
        result.fastview_condition_histories = (
            duplicate,
            duplicate,
            result.fastview_condition_histories[1],
        )
        with self.assertRaisesRegex(
            FastViewRetainedPlayerRowError,
            "duplicate retained FastView Condition",
        ):
            build_fastview_player_rows_from_retained_histories(
                result,
                (row(),),
                global_tick=0,
                energy_rng6_rolls={(0, 3): 0},
            )

    def test_requested_rows_require_unique_source_players_and_visible_slots(self):
        result = retained_result()
        with self.assertRaisesRegex(
            FastViewRetainedPlayerRowError,
            "source player",
        ):
            build_fastview_player_rows_from_retained_histories(
                result,
                (row(0, 3, 0), row(0, 3, 1)),
                global_tick=0,
                energy_rng6_rolls={(0, 3): 0},
            )

        with self.assertRaisesRegex(
            FastViewRetainedPlayerRowError,
            "visible slot",
        ):
            build_fastview_player_rows_from_retained_histories(
                result,
                (row(0, 3, 0), row(0, 4, 0)),
                global_tick=0,
                energy_rng6_rolls={(0, 3): 0, (0, 4): 1},
            )

    def test_energy_roll_mapping_must_exactly_cover_requested_source_players(self):
        result = retained_result()
        for rolls in (
            {},
            {(0, 3): 1, (1, 4): 2},
            {(0, 3): True},
            {(0, 3): 6},
        ):
            with self.subTest(rolls=rolls):
                with self.assertRaises(FastViewRetainedPlayerRowError):
                    build_fastview_player_rows_from_retained_histories(
                        result,
                        (row(),),
                        global_tick=0,
                        energy_rng6_rolls=rolls,
                    )

    def test_missing_or_invalid_retained_histories_fail_closed(self):
        with self.assertRaisesRegex(
            FastViewRetainedPlayerRowError,
            "does not retain",
        ):
            build_fastview_player_rows_from_retained_histories(
                SimpleNamespace(),
                (row(),),
                global_tick=0,
                energy_rng6_rolls={(0, 3): 0},
            )

        result = retained_result()
        result.fastview_condition_histories = (
            history(0, 3, (80,) * 23),
            result.fastview_condition_histories[1],
        )
        with self.assertRaisesRegex(
            FastViewRetainedPlayerRowError,
            "are invalid",
        ):
            build_fastview_player_rows_from_retained_histories(
                result,
                (row(),),
                global_tick=0,
                energy_rng6_rolls={(0, 3): 0},
            )

    def test_adapter_does_not_import_simulation_gameplay_or_rng_modules(self):
        source = Path(__file__).with_name(
            "gate14_fastview_playerrow_from_result.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "match_simulation",
            "human_gameplay",
            "game_state",
            "match_engine_rng",
            "match_calculator",
            "random",
        ):
            self.assertNotIn(f"import {forbidden}", source)
            self.assertNotIn(f"from {forbidden}", source)


if __name__ == "__main__":
    unittest.main()
