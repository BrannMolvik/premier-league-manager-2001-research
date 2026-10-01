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

LEAGUE_FIXTURE_STATUS_COMPLETE_BIT = 0x1
LEAGUE_FIXTURE_SCORE_LEFT_OFFSET = 0x3C
LEAGUE_FIXTURE_SCORE_RIGHT_OFFSET = 0x3E
LEAGUE_FIXTURE_STATUS_OFFSET = 0x44
LEAGUE_FIXTURE_DATE_ACCESSOR_VA = 0x510A20
LEAGUE_FIXTURE_SCORE_LEFT_ACCESSOR_VA = 0x513E70
LEAGUE_FIXTURE_SCORE_RIGHT_ACCESSOR_VA = 0x513E80
LEAGUE_FIXTURE_RESULT_COPY_VA = 0x5112A0
LEAGUE_FIXTURE_COMPLETION_VA = 0x511370
LEAGUE_FIXTURE_SCORE_FORMAT_VA = 0x81C504
LEAGUE_FIXTURE_SCORE_FORMAT = "%i:%i"
LEAGUE_FIXTURE_DATE_FORMAT_VA = 0x81C4F8
LEAGUE_FIXTURE_DATE_FORMAT = "%02i.%02i"
LEAGUE_FIXTURES_SELECTED_INDEX_OLD_OFFSET = 0x109B0
LEAGUE_FIXTURES_SELECTED_INDEX_CURRENT_OFFSET = 0x109B4

PLEAGUE_GRID_CLASS = "PLeagueGrid"
PLEAGUE_GRID_TYPE_DESCRIPTOR_VA = 0x81C510
PLEAGUE_GRID_VFTABLE_VA = 0x7C23D0
PLEAGUE_GRID_CONSTRUCTOR_VA = 0x46CBD0
PLEAGUE_GRID_OBJECT_OFFSET = 0x1CF0

LEAGUE_FIXTURES_TOP_HEADER_ARRAY_OFFSET = 0x9A0
LEAGUE_FIXTURES_SIDE_HEADER_ARRAY_OFFSET = 0x15D0
LEAGUE_FIXTURES_HEADER_STRIDE = 0x4C
LEAGUE_FIXTURES_HEADER_IDENTITY_OFFSET = 0x48
LEAGUE_FIXTURES_HEADER_IDENTITY_SETTER_VA = 0x5D5490


def league_fixture_base_box(
    *,
    fixture_present: bool,
    fixture_status_bits: int = 0,
    same_club_diagonal: bool = False,
) -> OriginalLeagueFixturesResource:
    """Mirror the base box-selection rules in the recovered row/update paths.

    For a populated fixture, status bit 0 selects the completed score-display
    path and its original played_fixtures_box; otherwise the date path uses
    date_fixtures_box. For an empty slot, the source compares the club pointers
    stored at +0x48 in the two header controls. Equality is therefore the
    self-fixture diagonal and selects red_fixtures_box.
    """
    if type(fixture_present) is not bool:
        raise OriginalLeagueFixturesResourceError("fixture_present must be boolean")
    if type(fixture_status_bits) is not int or fixture_status_bits < 0:
        raise OriginalLeagueFixturesResourceError(
            "fixture_status_bits must be a non-negative integer"
        )
    if type(same_club_diagonal) is not bool:
        raise OriginalLeagueFixturesResourceError(
            "same_club_diagonal must be boolean"
        )
    if fixture_present:
        return (
            PLAYED_FIXTURES_BOX
            if fixture_status_bits & LEAGUE_FIXTURE_STATUS_COMPLETE_BIT
            else DATE_FIXTURES_BOX
        )
    return RED_FIXTURES_BOX if same_club_diagonal else DATE_FIXTURES_BOX


def league_fixture_box_for_cell(
    *,
    fixture_present: bool,
    fixture_status_bits: int = 0,
    same_club_diagonal: bool = False,
    selected: bool = False,
) -> OriginalLeagueFixturesResource:
    """Apply the source-proven selected-cell overlay after the base box rule."""
    if type(selected) is not bool:
        raise OriginalLeagueFixturesResourceError("selected must be boolean")
    if selected:
        return TOGGLED_FIXTURES_BOX
    return league_fixture_base_box(
        fixture_present=fixture_present,
        fixture_status_bits=fixture_status_bits,
        same_club_diagonal=same_club_diagonal,
    )


def league_fixture_visible_text(
    *,
    fixture_status_bits: int,
    score_left: int | None = None,
    score_right: int | None = None,
    date_day: int | None = None,
    date_month: int | None = None,
) -> str:
    """Mirror the two source format strings selected by fixture status bit 0."""
    if type(fixture_status_bits) is not int or fixture_status_bits < 0:
        raise OriginalLeagueFixturesResourceError(
            "fixture_status_bits must be a non-negative integer"
        )
    if fixture_status_bits & LEAGUE_FIXTURE_STATUS_COMPLETE_BIT:
        if type(score_left) is not int or type(score_right) is not int:
            raise OriginalLeagueFixturesResourceError(
                "completed fixture text requires integer score fields"
            )
        return f"{score_left}:{score_right}"
    if type(date_day) is not int or type(date_month) is not int:
        raise OriginalLeagueFixturesResourceError(
            "scheduled fixture text requires integer day/month fields"
        )
    return f"{date_day:02d}.{date_month:02d}"



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
