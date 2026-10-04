"""Source-closed FM2001 chant-bank selection rules.

The canonical executable builds lowercase 8-character bank-name prefixes before
enumerating Data/Audio/Chants/*.bnk. This module records only that selection
logic and the current source-disc family inventory. It does not decode CHANT.eam,
assign chant meanings, bind chants to match events, or recover playback timing.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate14ChantSelectionError(ValueError):
    pass


CHANT_PAIR_SELECTION_VA = 0x722F00
CHANT_DYNAMIC_LOAD_VA = 0x723010
BANK_PREFIX_CLASSIFIER_VA = 0x7230D6
BANK_RECORD_LOWERCASE_VA = 0x7231D0

HOME_CLUB_GLOBAL_VA = 0xAD6060
AWAY_CLUB_GLOBAL_VA = 0xAD6174
CLUB_SOURCE_ID_OFFSET = 0x32

# Five source patterns checked in order at 0x7230D6.
GENERIC_PREFIX = "cgener"
CL_HOME_DEFAULT = "cl000000"
CL_AWAY_DEFAULT = "cl000000"
CLUB_HOME_DEFAULT = "c0000000"
CLUB_AWAY_DEFAULT = "c0000000"

GENERIC_POOL_TYPE = 2
HOME_POOL_TYPE = 0
AWAY_POOL_TYPE = 1

# Exact source-disc inventory shape.
GENERIC_BANK_COUNT = 21
CLUB_BANK_COUNT = 35
CL_FAMILY_BANK_COUNT = 0
CLUB_SOURCE_ID_COUNTS = (
    (0, 1), (1, 1), (2, 1), (4, 3), (5, 1), (6, 1), (7, 1),
    (8, 2), (9, 3), (10, 3), (11, 2), (12, 2), (13, 1), (14, 1),
    (15, 3), (16, 1), (17, 3), (18, 1), (19, 1), (20, 1),
    (90, 1), (94, 1),
)


@dataclass(frozen=True)
class ChantSelectionPatterns:
    home_club_source_id: int
    away_club_source_id: int
    club_same_id_rng_bit: int | None
    cl_home_pattern: str
    cl_away_pattern: str
    club_home_pattern: str
    club_away_pattern: str
    bank_to_club_mapping_recovered: bool = True
    event_binding_recovered: bool = False
    playback_timing_recovered: bool = False

    def __post_init__(self) -> None:
        for value in (self.home_club_source_id, self.away_club_source_id):
            if type(value) is not int or not 0 <= value <= 0xFFFF:
                raise Gate14ChantSelectionError("club source IDs must be uint16")
        if self.club_same_id_rng_bit not in (None, 0, 1):
            raise Gate14ChantSelectionError("same-id RNG bit must be None, 0 or 1")
        for value in (
            self.cl_home_pattern,
            self.cl_away_pattern,
            self.club_home_pattern,
            self.club_away_pattern,
        ):
            if not isinstance(value, str) or not value or value != value.lower():
                raise Gate14ChantSelectionError("chant patterns must be lowercase strings")
        if self.event_binding_recovered or self.playback_timing_recovered:
            raise Gate14ChantSelectionError(
                "bank selection cannot promote event/timing semantics"
            )


def _club_pattern(source_id: int) -> str:
    return f"c0{source_id:04d}"


def chant_selection_patterns(
    home_club_source_id: int,
    away_club_source_id: int,
    *,
    cl_rng_bit: int,
    club_same_id_rng_bit: int | None = None,
) -> ChantSelectionPatterns:
    """Reproduce the exact prefix assignment prepared by 0x722F00.

    The CL family is initialized from two identical value-1 selectors. When the
    values compare equal, one side receives cl000001 and the other cl000000,
    chosen by one private presentation RNG parity bit.

    For club-specific C0 banks, distinct club source IDs map directly to home and
    away prefixes. If both source IDs are equal, one side receives the specific
    prefix and the other receives literal c0000000, again selected by RNG parity.
    """
    for value in (home_club_source_id, away_club_source_id):
        if type(value) is not int or not 0 <= value <= 0xFFFF:
            raise Gate14ChantSelectionError("club source IDs must be uint16")

    if cl_rng_bit not in (0, 1):
        raise Gate14ChantSelectionError("CL RNG bit must be 0 or 1")
    if club_same_id_rng_bit not in (None, 0, 1):
        raise Gate14ChantSelectionError("same-club RNG bit must be None, 0 or 1")

    needs_club_rng = home_club_source_id == away_club_source_id
    if needs_club_rng and club_same_id_rng_bit is None:
        raise Gate14ChantSelectionError(
            "same club source IDs require the separate club RNG parity bit"
        )
    if not needs_club_rng and club_same_id_rng_bit is not None:
        raise Gate14ChantSelectionError(
            "distinct club source IDs do not consume a club RNG parity bit"
        )

    # 0x723350 sets both CL selector globals to 1 before 0x722F00. The equal
    # branch therefore always consumes its own RNG parity draw.
    if cl_rng_bit:
        cl_home, cl_away = "cl000001", CL_AWAY_DEFAULT
    else:
        cl_home, cl_away = CL_HOME_DEFAULT, "cl000001"

    if home_club_source_id != away_club_source_id:
        club_home = _club_pattern(home_club_source_id)
        club_away = _club_pattern(away_club_source_id)
    elif club_same_id_rng_bit:
        club_home = _club_pattern(home_club_source_id)
        club_away = CLUB_AWAY_DEFAULT
    else:
        club_home = CLUB_HOME_DEFAULT
        club_away = _club_pattern(away_club_source_id)

    return ChantSelectionPatterns(
        home_club_source_id=home_club_source_id,
        away_club_source_id=away_club_source_id,
        club_same_id_rng_bit=(club_same_id_rng_bit if needs_club_rng else None),
        cl_home_pattern=cl_home,
        cl_away_pattern=cl_away,
        club_home_pattern=club_home,
        club_away_pattern=club_away,
    )


def classify_chant_bank_basename(
    basename: str,
    patterns: ChantSelectionPatterns,
) -> int | None:
    """Return the exact source pool type selected by 0x7230D6.

    The executable lowercases the first eight basename bytes and checks the five
    patterns in source order using substring matching.
    """
    if not isinstance(basename, str) or not basename:
        raise Gate14ChantSelectionError("chant basename must be non-empty")
    if type(patterns) is not ChantSelectionPatterns:
        raise Gate14ChantSelectionError("patterns must be exact ChantSelectionPatterns")

    name = basename.lower()[:8]
    checks = (
        (GENERIC_PREFIX, GENERIC_POOL_TYPE),
        (patterns.cl_home_pattern, HOME_POOL_TYPE),
        (patterns.cl_away_pattern, AWAY_POOL_TYPE),
        (patterns.club_home_pattern, HOME_POOL_TYPE),
        (patterns.club_away_pattern, AWAY_POOL_TYPE),
    )
    for pattern, pool_type in checks:
        if pattern in name:
            return pool_type
    return None
