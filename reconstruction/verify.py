from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import sys

from competition_materializer import materialize_primary_rng_driven_schedule
from competition_startup import (
    primary_mode0_cup_pairing_draw_count,
    primary_mode0_cup_round_team_counts,
    primary_mode0_dummy_league_sort_draw_count,
    primary_mode0_dummy_league_sort_source_ids,
    primary_mode0_root_initialization_order,
    replay_primary_mode0_ordered_competition_rng,
    replay_primary_mode0_pre_shuffle_state,
)
from competition_state import PremierLeagueState
from fm2001_data import FM2001Database
from match_schedule import MsvcCrtRng


CANONICAL_HASHES = {
    "Master.dat": "183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8",
    "Static.dat": "e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8",
    "English.str": "aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601",
    "Core.str": "b0800475769fa087e69de989388569e5b29f495e5abe5d62687c2acb1d339e06",
}


class VerificationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_canonical_files(game_dir: Path) -> None:
    for filename, expected_hash in CANONICAL_HASHES.items():
        path = game_dir / filename
        require(path.is_file(), f"Missing required canonical file: {path}")
        actual_hash = file_sha256(path)
        require(
            actual_hash == expected_hash,
            (
                f"{filename} does not match the analyzed FM2001 release: "
                f"expected SHA-256 {expected_hash}, got {actual_hash}"
            ),
        )


def verify_database(db: FM2001Database) -> None:
    require(len(db.clubs) == 1246, f"Expected 1246 clubs, got {len(db.clubs)}")
    require(len(db.players) == 30064, f"Expected 30064 players, got {len(db.players)}")
    require(len(db.managers) == 1612, f"Expected 1612 managers, got {len(db.managers)}")
    require(len(db.positions) == 20, f"Expected 20 positions, got {len(db.positions)}")
    require(len(db.rounds) == 1053, f"Expected 1053 rounds, got {len(db.rounds)}")
    require(
        len(db.cup_allocation_instructions) == 238,
        (
            "Expected 238 Cup allocation instructions, got "
            f"{len(db.cup_allocation_instructions)}"
        ),
    )
    require(
        tuple(instruction.id for instruction in db.cup_allocation_instructions)
        == tuple(range(238)),
        "Cup allocation instruction IDs are not canonical source order 0..237",
    )
    allocation_type_counts = Counter(
        int(instruction.instruction_type)
        for instruction in db.cup_allocation_instructions
    )
    require(
        allocation_type_counts == {1: 11, 2: 2, 3: 148, 4: 11, 5: 66},
        f"Unexpected Cup allocation instruction type counts: {allocation_type_counts}",
    )
    require(
        len(db.premier_league_rounds) == 38,
        f"Expected 38 Premier League rounds, got {len(db.premier_league_rounds)}",
    )
    require(
        len(db.real_fixtures) == 380,
        f"Expected 380 real fixtures, got {len(db.real_fixtures)}",
    )

    primary_cup_ids = {
        int(competition.id)
        for competition in db.competitions
        if int(competition.runtime_kind_code) == 2
        and int(competition.schedule_container_code) not in (2, 3)
    }
    primary_cup_rounds = tuple(
        round_definition
        for round_definition in db.rounds
        if int(round_definition.competition_id) in primary_cup_ids
    )
    require(
        len(primary_cup_ids) == 27,
        f"Expected 27 primary Cups, got {len(primary_cup_ids)}",
    )
    require(
        len(primary_cup_rounds) == 115,
        f"Expected 115 primary Cup rounds, got {len(primary_cup_rounds)}",
    )
    require(
        {
            round_type: sum(
                int(round_definition.type_code) == round_type
                for round_definition in primary_cup_rounds
            )
            for round_type in (1, 2, 3)
        }
        == {1: 80, 2: 32, 3: 3},
        "Primary Cup round classes do not match canonical 80/32/3 split",
    )
    require(
        primary_mode0_cup_pairing_draw_count(db.competitions, db.rounds) == 1737,
        "Expected 1737 mandatory primary Cup pairing RNG calls",
    )
    require(
        len(
            primary_mode0_cup_round_team_counts(
                db.competitions,
                db.rounds,
            )
        )
        == 115,
        "Primary Cup RNG round-count helper does not cover all 115 rounds",
    )
    dummy_sort_sources = primary_mode0_dummy_league_sort_source_ids(
        db.competitions,
        db.cup_allocation_instructions,
    )
    require(
        dummy_sort_sources == (89, 25, 93, 104, 168, 162, 148, 139, 102, 131, 120),
        f"Unexpected primary DummyLeague lazy-sort sources: {dummy_sort_sources}",
    )
    require(
        primary_mode0_dummy_league_sort_draw_count(
            db.competitions,
            db.cup_allocation_instructions,
            db.clubs,
        )
        == 124,
        "Expected 124 primary DummyLeague lazy-sort RNG calls",
    )
    cup_subset_state_replay = replay_primary_mode0_pre_shuffle_state(
        MsvcCrtRng(0x4B68DE28),
        db.competitions,
        db.rounds,
        db.clubs,
        db.countries,
        db.cup_allocation_instructions,
    )
    require(
        cup_subset_state_replay.total_draw_count == 1863,
        f"Expected 1863 Cup/DummyLeague/selector subset draws, got {cup_subset_state_replay.total_draw_count}",
    )
    require(
        cup_subset_state_replay.dummy_league_sort_draw_count == 124,
        "Cup-focused subset did not include 124 DummyLeague lazy-sort draws",
    )
    require(
        cup_subset_state_replay.state_entering_primary_shuffle == 0x00523131,
        (
            "Cup-focused subset checkpoint mismatch: "
            f"0x{cup_subset_state_replay.state_entering_primary_shuffle:08X}"
        ),
    )

    spanish_root_order = tuple(
        int(competition.id)
        for competition in primary_mode0_root_initialization_order(
            db.competitions,
            tuple(int(country.id) for country in db.countries),
        )
        if int(competition.country_region_id) == 73
    )
    require(
        spanish_root_order == (33, 34, 31, 32, 95),
        f"Unexpected canonical Spain root initialization order: {spanish_root_order}",
    )

    ordered_competition_rng = replay_primary_mode0_ordered_competition_rng(
        MsvcCrtRng(0x4B68DE28),
        db.competitions,
        db.rounds,
        db.clubs,
        db.countries,
        db.cup_allocation_instructions,
        db.players,
    )
    require(
        len(ordered_competition_rng.events) == 128,
        (
            "Expected 128 primary competition RNG events, got "
            f"{len(ordered_competition_rng.events)}"
        ),
    )
    require(
        ordered_competition_rng.primary_cup_round_count == 115,
        "Ordered replay does not contain all 115 primary Cup rounds",
    )
    require(
        ordered_competition_rng.cup_pairing_draw_count == 1737,
        "Ordered replay does not contain exactly 1737 Cup shuffle draws",
    )
    require(
        ordered_competition_rng.europe_selector_draw_count == 2,
        "Ordered replay does not contain exactly two Europe selector draws",
    )
    require(
        ordered_competition_rng.total_draw_count == 1863,
        "Ordered replay does not contain exactly 1863 total competition draws",
    )

    selector_event_indices = tuple(
        index
        for index, event in enumerate(ordered_competition_rng.events)
        if event.kind == "europe_selector"
    )
    require(
        selector_event_indices == (110, 119),
        f"Unexpected Europe selector event positions: {selector_event_indices}",
    )
    dummy_event_indices = tuple(
        index
        for index, event in enumerate(ordered_competition_rng.events)
        if event.kind == "dummy_league_lazy_sort"
    )
    require(
        dummy_event_indices == (20, 47, 60, 98, 99, 100, 101, 102, 103, 104, 105),
        f"Unexpected DummyLeague lazy-sort event positions: {dummy_event_indices}",
    )
    require(
        sum(
            len(event.bounds)
            for event in ordered_competition_rng.events
            if event.kind == "dummy_league_lazy_sort"
        )
        == 124,
        "Ordered replay does not contain exactly 124 DummyLeague sort draws",
    )

    ordered_bounds = tuple(
        bound
        for event in ordered_competition_rng.events
        for bound in event.bounds
    )
    bounds_blob = b"".join(
        int(bound).to_bytes(2, "little")
        for bound in ordered_bounds
    )
    bounds_sha256 = sha256(bounds_blob).hexdigest()
    require(
        bounds_sha256
        == "a6675e77b8256fcb8d5834efa6a9d006182078c12f27887c8228a14eca889711",
        f"Primary competition ordered-bound digest mismatch: {bounds_sha256}",
    )
    require(
        ordered_competition_rng.champions_league_club_id == 1137,
        (
            "Synthetic ordered replay selected unexpected Champions League "
            f"candidate {ordered_competition_rng.champions_league_club_id}"
        ),
    )
    require(
        ordered_competition_rng.uefa_cup_club_id == 1143,
        (
            "Synthetic ordered replay selected unexpected UEFA Cup candidate "
            f"{ordered_competition_rng.uefa_cup_club_id}"
        ),
    )
    require(
        ordered_competition_rng.state_entering_primary_shuffle == 0x00523131,
        (
            "Corrected ordered primary competition state mismatch: "
            f"0x{ordered_competition_rng.state_entering_primary_shuffle:08X}"
        ),
    )

    actual_competition_runtime = materialize_primary_rng_driven_schedule(
        MsvcCrtRng(0x4B68DE28),
        db.competitions,
        db.rounds,
        db.clubs,
        db.countries,
        db.cup_allocation_instructions,
        db.players,
        real_fixtures=db.real_fixtures,
    )
    require(
        actual_competition_runtime.rng_plan_event_count == 168,
        (
            "Expected 168 actual competition traversal events including the "
            "zero-RNG fixed League marker, got "
            f"{actual_competition_runtime.rng_plan_event_count}"
        ),
    )
    require(
        sum(
            event.kind == "procedural_league_round_robin"
            for event in actual_competition_runtime.rng_events
        )
        == 39,
        "Expected 39 procedural League runtime instances",
    )
    require(
        sum(
            len(event.bounds)
            for event in actual_competition_runtime.rng_events
            if event.kind == "procedural_league_round_robin"
        )
        == 3982,
        "Actual replay lost the 3982 procedural League RNG calls",
    )
    require(
        sum(
            len(event.bounds)
            for event in actual_competition_runtime.rng_events
            if event.kind == "cup_round_shuffle"
        )
        == 1728,
        "Expected 1728 actual-count Cup participant-shuffle calls",
    )
    require(
        sum(
            len(event.bounds)
            for event in actual_competition_runtime.rng_events
            if event.kind == "dummy_league_lazy_sort"
        )
        == 124,
        "Actual replay lost the 124 DummyLeague lazy-sort calls",
    )
    require(
        sum(
            len(event.bounds)
            for event in actual_competition_runtime.rng_events
            if event.kind == "europe_selector"
        )
        == 2,
        "Actual replay lost the two Europe-root selector calls",
    )
    require(
        actual_competition_runtime.rng_plan_total_draw_count == 5836,
        (
            "Expected 5836 actual primary competition calls, got "
            f"{actual_competition_runtime.rng_plan_total_draw_count}"
        ),
    )
    require(
        actual_competition_runtime.rng_bounds_sha256
        == "3fb0ad9c8b9d21f55916e36c82d22762a0c45e37045f264ccb01a7dfc5415196",
        (
            "Actual primary competition ordered-bound digest mismatch: "
            f"{actual_competition_runtime.rng_bounds_sha256}"
        ),
    )
    actual_selector_event_indices = tuple(
        index
        for index, event in enumerate(actual_competition_runtime.rng_events)
        if event.kind == "europe_selector"
    )
    require(
        actual_selector_event_indices == (138, 159),
        (
            "Unexpected actual Europe selector event positions: "
            f"{actual_selector_event_indices}"
        ),
    )
    require(
        actual_competition_runtime.cup_runtime.champions_league_club_id == 1118,
        (
            "Actual replay selected unexpected Champions League candidate "
            f"{actual_competition_runtime.cup_runtime.champions_league_club_id}"
        ),
    )
    require(
        actual_competition_runtime.cup_runtime.uefa_cup_club_id == 1139,
        (
            "Actual replay selected unexpected UEFA Cup candidate "
            f"{actual_competition_runtime.cup_runtime.uefa_cup_club_id}"
        ),
    )
    require(
        actual_competition_runtime.state_entering_primary_shuffle == 0x4F5CF274,
        (
            "Actual primary pre-shuffle state mismatch: "
            f"0x{actual_competition_runtime.state_entering_primary_shuffle:08X}"
        ),
    )
    require(
        actual_competition_runtime.cup_runtime.participant_sha256
        == "dd1f880d75aa63ff6bad1276cbac971c9a5ef568fe7fe0474401e690c12128ca",
        "Canonical Cup participant digest mismatch",
    )
    require(
        actual_competition_runtime.cup_runtime.pairing_sha256
        == "f8654c52f03bdefde67ed0421d54eeed1e2cc77209dc92d167dae3329817895b",
        "Canonical Cup pairing digest mismatch",
    )
    require(
        actual_competition_runtime.cup_runtime.cup_schedule_sha256
        == "b8705d885dd4d3be6a40df33744746884c074678032add21da1b1001c22bfe33",
        "Canonical Cup schedule-node digest mismatch",
    )
    require(
        actual_competition_runtime.schedule_sha256
        == "d2645b5973e0c6e41d8775724c3632239664331dbdb86eb7b435051f6b5cc058",
        "Canonical complete schedule-node digest mismatch",
    )
    require(
        len(actual_competition_runtime.cup_runtime.cup_schedule_nodes) == 1226,
        "Expected 1226 canonical Cup schedule nodes",
    )
    require(
        actual_competition_runtime.schedule_node_count == 9346,
        "Expected 9346 canonical primary schedule nodes",
    )
    require(
        actual_competition_runtime.cup_runtime.dropped_ref_count == 3,
        "Expected three canonical allocation refs dropped after round capacity",
    )
    require(
        actual_competition_runtime.cup_runtime.type2_injected_ref_count == 24,
        "Expected 24 canonical Champions-League-to-UEFA type-2 refs",
    )

    uefa_cup = next(
        cup
        for cup in actual_competition_runtime.cup_runtime.cups
        if int(cup.competition_id) == 10
    )
    require(
        tuple(
            len(runtime_round.participant_refs)
            for runtime_round in uefa_cup.runtime.rounds
        )
        == (80, 95, 47, 31, 15, 7, 3, 1),
        "Canonical UEFA Cup runtime underfill chain changed",
    )

    require(
        len({f.round_index for f in db.real_fixtures}) == 38,
        "Real fixtures do not span exactly 38 round indices",
    )
    require(
        all(len(db.fixtures_for_round(r)) == 10 for r in range(38)),
        "At least one Premier League round does not contain exactly 10 fixtures",
    )

    pl_clubs = {
        club_id
        for fixture in db.real_fixtures
        for club_id in (fixture.home_club_id, fixture.away_club_id)
    }
    require(len(pl_clubs) == 20, f"Expected 20 Premier League clubs, got {len(pl_clubs)}")
    require(
        all(
            sum(1 for fixture in db.real_fixtures if fixture.home_club_id == club_id) == 19
            for club_id in pl_clubs
        ),
        "At least one Premier League club does not have exactly 19 home fixtures",
    )
    require(
        all(
            sum(1 for fixture in db.real_fixtures if fixture.away_club_id == club_id) == 19
            for club_id in pl_clubs
        ),
        "At least one Premier League club does not have exactly 19 away fixtures",
    )

    league = PremierLeagueState(db.real_fixtures, db.premier_league_rounds, 2000)
    expected_dates = {
        0: "2000-08-19",
        1: "2000-08-23",
        18: "2000-12-26",
        20: "2001-01-01",
        37: "2001-05-20",
    }
    for round_index, expected in expected_dates.items():
        actual = league.round_date(round_index).isoformat()
        require(
            actual == expected,
            f"Round {round_index} date mismatch: expected {expected}, got {actual}",
        )

    require(db.clubs[0].name == "Arsenal", f"Club 0 mismatch: {db.clubs[0].name!r}")
    require(
        db.players[0].full_name == "David Seaman",
        f"Player 0 mismatch: {db.players[0].full_name!r}",
    )
    require(db.players[0].club_id == 0, f"Player 0 club mismatch: {db.players[0].club_id}")
    require(
        db.players[2].full_name == "Nigel Winterburn",
        f"Player 2 mismatch: {db.players[2].full_name!r}",
    )
    require(
        db.clubs[db.players[2].club_id].name == "West Ham United",
        "Player 2 club does not resolve to West Ham United",
    )
    require(
        db.managers[10].full_name == "Alex Ferguson",
        f"Manager 10 mismatch: {db.managers[10].full_name!r}",
    )
    require(
        db.managers[10].date_of_birth is not None
        and db.managers[10].date_of_birth.isoformat() == "1941-12-31",
        f"Manager 10 date of birth mismatch: {db.managers[10].date_of_birth}",
    )
    require(
        db.managers[204].full_name == "Arsène Wenger",
        f"Manager 204 mismatch: {db.managers[204].full_name!r}",
    )
    require(
        db.managers[204].club_id == 0,
        f"Manager 204 club mismatch: {db.managers[204].club_id}",
    )


def main() -> int:
    game_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Games\FM2001")

    try:
        verify_canonical_files(game_dir)
        db = FM2001Database(game_dir)
        verify_database(db)
    except (OSError, ValueError, VerificationError) as exc:
        print(f"FM2001 verification FAILED: {exc}", file=sys.stderr)
        return 1

    print("FM2001 canonical release and clean-room parser verification passed")
    print(db.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
