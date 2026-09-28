from match_schedule import MsvcCrtRng
from scouting import (
    MAX_NUM_FOUND,
    MAX_NUM_USED1,
    MAX_NUM_USED2,
    SCOUT_ONE_AGE_BIAS,
    ScoutingReseedState,
    primary_scouting_results,
    scouting_shuffle,
    secondary_scouting_results,
)


def test_scouting_tuning_defaults_match_executable():
    assert SCOUT_ONE_AGE_BIAS == 4
    assert MAX_NUM_USED1 == 80
    assert MAX_NUM_USED2 == 50
    assert MAX_NUM_FOUND == 20


def test_exact_scouting_seed_xors_neutral_panel_fields():
    state = ScoutingReseedState(
        status_control_7738=1,
        status_control_76f8=2,
        status_control_76b8=3,
        value_high_64d0=123.9,
        value_low_64c8=-45.9,
        field_64e4=0x11223344,
        age_high_64dc=35,
        field_64e0=2,
        age_low_64d8=18,
        class_selector_64c0=3,
    )
    expected = 0
    for value in (1, 2, 3, 123, -45, 0x11223344, 35, 2, 18, 3, -1):
        expected ^= value & 0xFFFFFFFF
    assert state.exact_seed(-1) == expected & 0xFFFFFFFF


def test_primary_scouting_shuffle_reseeds_instead_of_using_incoming_game_state():
    state = ScoutingReseedState(
        status_control_7738=1,
        value_high_64d0=1000.0,
        value_low_64c8=10.0,
        age_high_64dc=35,
        age_low_64d8=18,
        class_selector_64c0=2,
    )
    candidates = tuple(range(12))

    first = primary_scouting_results(candidates, state)
    second = primary_scouting_results(candidates, state)

    assert first == second

    rng = MsvcCrtRng(state.exact_seed(-1))
    expected = list(candidates)
    for remaining in range(len(expected), 1, -1):
        selected = rng.randbelow(remaining)
        expected[selected], expected[remaining - 1] = (
            expected[remaining - 1],
            expected[selected],
        )
    assert first == tuple(expected)


def test_secondary_scouting_applies_used_and_found_caps_around_shuffle():
    state = ScoutingReseedState(field_64e4=9, age_low_64d8=16)
    ranked = tuple(range(100))

    result = secondary_scouting_results(
        ranked,
        state,
        caller_argument=7,
    )

    assert len(result) == 20
    assert set(result).issubset(set(range(50)))
    assert result == scouting_shuffle(range(50), state, caller_argument=7)[:20]
