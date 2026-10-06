"""Exact source-backed PPreMatchPanel team-rating bar widths.

The four native PPreMatchPanel width functions iterate exactly eleven starter
pointers, classify each player's current assigned role through the Position
table broad class byte, sum the exact current-role rating returned by
RuntimePlayer.current_role_rating()/0x41E1B0 -> 0x41C7E0, scale the group total,
and cap the result at the 171-pixel source bar width.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


PREMATCH_RATING_BAR_FULL_WIDTH = 171

# Native functions, Position.lineup_group discriminator, scale, display meaning.
# The semantic mapping is source-closed by Static.dat Position +6 and the
# canonical runtime Position+0x11 parser.
PREMATCH_RATING_GROUPS = (
    (0x49A3D0, 3, 1.71, "goalkeeper"),
    (0x49A460, 0, 0.342, "defence"),
    (0x49A4F0, 1, 0.342, "midfield"),
    (0x49A580, 2, 0.57, "attack"),
)


class PrematchRatingWidthError(ValueError):
    pass


@dataclass(frozen=True)
class PrematchTeamRatingWidths:
    goalkeeper: int
    defence: int
    midfield: int
    attack: int

    def __post_init__(self) -> None:
        for value in (
            self.goalkeeper,
            self.defence,
            self.midfield,
            self.attack,
        ):
            if not 0 <= int(value) <= PREMATCH_RATING_BAR_FULL_WIDTH:
                raise PrematchRatingWidthError(
                    "pre-match rating width must be in 0..171"
                )

    def by_discriminator(self, discriminator: int) -> int:
        lookup = {
            3: self.goalkeeper,
            0: self.defence,
            1: self.midfield,
            2: self.attack,
        }
        try:
            return int(lookup[int(discriminator)])
        except KeyError as exc:
            raise PrematchRatingWidthError(
                f"unsupported pre-match rating discriminator: {discriminator}"
            ) from exc


def _position_group_for_player(player, positions: Mapping[int, object]) -> int:
    role = int(getattr(player, "current_position"))
    try:
        position = positions[role]
    except KeyError as exc:
        raise PrematchRatingWidthError(
            f"position metadata for current role {role} is unavailable"
        ) from exc
    group = int(getattr(position, "lineup_group"))
    if not 0 <= group <= 255:
        raise PrematchRatingWidthError("Position.lineup_group must be a byte")
    return group


def source_prematch_team_rating_widths(
    starters: Sequence[object],
    positions: Mapping[int, object],
) -> PrematchTeamRatingWidths:
    """Reproduce native 0x49A3D0/460/4F0/580 for one starting XI.

    The original functions receive one of the two eleven-pointer starter
    arrays. RF/LF Position records have broad class 255 in Static.dat and
    therefore contribute to none of the four bars, matching the native
    discriminator comparisons exactly.
    """
    starters = tuple(starters)
    if len(starters) != 11:
        raise PrematchRatingWidthError(
            "PPreMatch rating source requires exactly 11 starters"
        )

    totals = {3: 0, 0: 0, 1: 0, 2: 0}
    for player in starters:
        group = _position_group_for_player(player, positions)
        if group not in totals:
            # Static.dat uses 255 for None/RF/LF. Native code simply fails all
            # four equality tests, so these roles contribute to no rating row.
            continue
        rating_method = getattr(player, "current_role_rating", None)
        if not callable(rating_method):
            raise PrematchRatingWidthError(
                "starter does not expose source-backed current_role_rating()"
            )
        rating = int(rating_method())
        if not 0 <= rating <= 99:
            raise PrematchRatingWidthError(
                "current role rating must remain in native 0..99 range"
            )
        totals[group] += rating

    widths = {}
    for _, discriminator, scale, name in PREMATCH_RATING_GROUPS:
        width = int(totals[discriminator] * scale)
        widths[name] = min(width, PREMATCH_RATING_BAR_FULL_WIDTH)

    return PrematchTeamRatingWidths(
        goalkeeper=widths["goalkeeper"],
        defence=widths["defence"],
        midfield=widths["midfield"],
        attack=widths["attack"],
    )


def prematch_rating_width_contract() -> dict:
    return {
        "starter_count": 11,
        "bar_width": PREMATCH_RATING_BAR_FULL_WIDTH,
        "groups": tuple(PREMATCH_RATING_GROUPS),
        "rating_source": "RuntimePlayer.current_role_rating",
        "position_group_source": "Position.lineup_group",
        "unclassified_group_255_excluded": True,
        "source_functions": (0x49A3D0, 0x49A460, 0x49A4F0, 0x49A580),
        "native_conversion": "truncate_scaled_sum_then_cap_171",
    }
