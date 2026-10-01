"""Source-backed original PLeagueFixtures graphic resources and grid geometry.

All six paths are exact literals from the canonical executable and were
revalidated against the authorized original disc in Recovery 150.  The module
keeps box-resource state semantics neutral beyond the original filenames; the
grid placements are exact calls made by PLeagueFixtures::0x46AA70.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_header import parse_ea444_header
from original_management_navigation import LEAGUE_FIXTURES_PANEL


class OriginalLeagueFixturesResourceError(ValueError):
    pass


LEAGUE_FIXTURES_SETUP_VA = 0x46AA70
LEAGUE_FIXTURES_BITMAP_SETUP_VA = 0x5D5280


@dataclass(frozen=True)
class OriginalLeagueFixturesResource:
    name: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    path_literal_va: int
    load_init_va: int
    raw_handle_va: int
    wrapper_init_va: int
    wrapper_va: int


DATE_FIXTURES_BOX = OriginalLeagueFixturesResource(
    "date_fixtures_box",
    "FM2001_Art/Generic/league_fixtures/date_fixtures_box.444",
    "b02036ae2d37c893e74a60a53eb1cdb514585654773916978e88f11ef66ab142",
    148,
    (24, 13),
    0x836D30,
    0x5F80E0,
    0x944B50,
    0x5F8130,
    0x944B30,
)
PLAYED_FIXTURES_BOX = OriginalLeagueFixturesResource(
    "played_fixtures_box",
    "FM2001_Art/Generic/league_fixtures/played_fixtures_box.444",
    "8c61143070c399477af735683b9e8a7effdfffee25b27d397f321cfe3a7d0db4",
    144,
    (24, 13),
    0x836D6C,
    0x5F8170,
    0x944B10,
    0x5F81C0,
    0x944AF0,
)
RED_FIXTURES_BOX = OriginalLeagueFixturesResource(
    "red_fixtures_box",
    "FM2001_Art/Generic/league_fixtures/red_fixtures_box.444",
    "0acd8300cd9bbb129924270f354e0a7017d3f78729be4ad5311895f9f5064c2e",
    112,
    (24, 13),
    0x836DA8,
    0x5F8200,
    0x944AD0,
    0x5F8250,
    0x944AB0,
)
TOGGLED_FIXTURES_BOX = OriginalLeagueFixturesResource(
    "toggled_fixtures_box",
    "FM2001_Art/Generic/league_fixtures/toggled_fixtures_box.444",
    "d99af52f7c4f20c88bc93f24ac2447febf2250da161a639070af840721c2539e",
    152,
    (24, 13),
    0x836DE0,
    0x5F8290,
    0x944A90,
    0x5F82E0,
    0x944A70,
)
FIXTURES_HORIZONTAL_GRID = OriginalLeagueFixturesResource(
    "fixtures_hori_grid",
    "FM2001_Art/Generic/league_fixtures/fixtures_hori_grid.444",
    "37e94e0eb2420aa498ca98d560ab180f80d1b8b7ffc6d4e8c664c398f7ebf8db",
    2652,
    (132, 52),
    0x836E1C,
    0x5F8320,
    0x944A50,
    0x5F8370,
    0x944A30,
)
FIXTURES_VERTICAL_GRID = OriginalLeagueFixturesResource(
    "fixtures_vert_grid",
    "FM2001_Art/Generic/league_fixtures/fixtures_vert_grid.444",
    "726bbb5df0fb632592a5e9f902fff7ca109b55e07ab433776e8f6973476f0ecb",
    924,
    (24, 528),
    0x836E58,
    0x5F83B0,
    0x944A10,
    0x5F8400,
    0x9449F0,
)

LEAGUE_FIXTURES_RESOURCES = (
    DATE_FIXTURES_BOX,
    PLAYED_FIXTURES_BOX,
    RED_FIXTURES_BOX,
    TOGGLED_FIXTURES_BOX,
    FIXTURES_HORIZONTAL_GRID,
    FIXTURES_VERTICAL_GRID,
)

# Exact first two positional arguments passed to 0x5D5280 by
# PLeagueFixtures::0x46AA70.  They are treated as source x/y coordinates
# because the helper's callers consistently pass screen-space origins.
LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS = tuple(
    (378 + 29 * index, 98) for index in range(12)
)
LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS = tuple(
    (241, 235 + 14 * index) for index in range(24)
)


def validate_original_league_fixtures_resources(
    source_root: Path,
) -> tuple[OriginalLeagueFixturesResource, ...]:
    """Require every exact source-correlated League Fixtures graphic."""
    root = Path(source_root)
    for resource in LEAGUE_FIXTURES_RESOURCES:
        path = root / resource.source_path
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise OriginalLeagueFixturesResourceError(
                f"Missing original League Fixtures resource: {resource.source_path}"
            ) from exc
        if len(data) != resource.byte_size:
            raise OriginalLeagueFixturesResourceError(
                f"League Fixtures byte-size mismatch: {resource.source_path}"
            )
        if sha256(data).hexdigest() != resource.sha256:
            raise OriginalLeagueFixturesResourceError(
                f"League Fixtures checksum mismatch: {resource.source_path}"
            )
        header = parse_ea444_header(data)
        if (header.width, header.height) != resource.size:
            raise OriginalLeagueFixturesResourceError(
                f"League Fixtures geometry mismatch: {resource.source_path}"
            )
    return LEAGUE_FIXTURES_RESOURCES


def assert_league_fixtures_panel_identity() -> None:
    if LEAGUE_FIXTURES_PANEL.panel_class != "PLeagueFixtures":
        raise OriginalLeagueFixturesResourceError(
            "League Fixtures resources require the source-proven PLeagueFixtures panel"
        )
