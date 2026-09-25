from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys

from competition_state import PremierLeagueState
from fm2001_data import FM2001Database


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
        len(db.premier_league_rounds) == 38,
        f"Expected 38 Premier League rounds, got {len(db.premier_league_rounds)}",
    )
    require(
        len(db.real_fixtures) == 380,
        f"Expected 380 real fixtures, got {len(db.real_fixtures)}",
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
