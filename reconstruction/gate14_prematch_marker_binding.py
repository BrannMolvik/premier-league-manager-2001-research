"""Supplied-state binding for the 22 PPreMatch starting-XI marker controls."""
from __future__ import annotations

from dataclasses import dataclass

from original_front_end_layout import OriginalRect
from original_prematch_panel import (
    PREMATCH_PITCH_MARKER_GOALKEEPER_CHILDREN,
    PREMATCH_PITCH_MARKER_OUTFIELD_CHILDREN,
    PREMATCH_PITCH_MARKER_SIZE,
    prematch_pitch_marker_origin,
)
from gate14_prematch_shirt_resources import (
    PrematchGoalkeeperShirt,
    PrematchNumberedShirtAtlas,
    crop_prematch_numbered_shirt_frame,
)


class PrematchMarkerBindingError(ValueError):
    pass


PREMATCH_MARKERS_PER_SIDE = 11
PREMATCH_MARKER_CHILD_STARTS = (10, 21)


@dataclass(frozen=True)
class BoundPrematchStartingXIMarker:
    side: int
    slot_index: int
    child_index: int
    visible: bool
    rect: OriginalRect | None
    source_kind: str | None
    source_path: str | None
    frame_number: int | None
    rgba: bytes | None

    def __post_init__(self) -> None:
        if self.side not in (0, 1):
            raise PrematchMarkerBindingError("marker side must be 0 or 1")
        if not 0 <= self.slot_index < PREMATCH_MARKERS_PER_SIDE:
            raise PrematchMarkerBindingError("marker slot must be in 0..10")
        expected_child = PREMATCH_MARKER_CHILD_STARTS[self.side] + self.slot_index
        if self.child_index != expected_child:
            raise PrematchMarkerBindingError("marker child index drifted")
        if self.visible:
            if self.rect is None or self.rgba is None or not self.source_kind or not self.source_path:
                raise PrematchMarkerBindingError("visible marker requires source pixels and geometry")
            if (self.rect.width, self.rect.height) != PREMATCH_PITCH_MARKER_SIZE:
                raise PrematchMarkerBindingError("visible marker must remain 36x32")
            if len(self.rgba) != 36 * 32 * 4:
                raise PrematchMarkerBindingError("visible marker RGBA geometry mismatch")
            if self.slot_index == 0:
                if self.source_kind != "goalkeeper_original" or self.frame_number is not None:
                    raise PrematchMarkerBindingError("slot zero must use dedicated goalkeeper source")
            elif self.frame_number is None:
                raise PrematchMarkerBindingError("outfield marker requires numbered frame")
        elif any(
            value is not None
            for value in (self.rect, self.source_kind, self.source_path, self.frame_number, self.rgba)
        ):
            raise PrematchMarkerBindingError("hidden marker cannot publish source pixels")


@dataclass(frozen=True)
class BoundPrematchStartingXIMarkers:
    markers: tuple[BoundPrematchStartingXIMarker, ...]
    supplied_state_bound: bool = True
    source_pixels_bound: bool = True
    source_geometry_bound: bool = True
    complete_prematch_frame: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        if len(self.markers) != 22:
            raise PrematchMarkerBindingError("starting-XI binding must contain 22 native controls")
        if tuple(marker.child_index for marker in self.markers) != tuple(range(10, 32)):
            raise PrematchMarkerBindingError("starting-XI marker child order must remain 10..31")
        if not (self.supplied_state_bound and self.source_pixels_bound and self.source_geometry_bound):
            raise PrematchMarkerBindingError("starting-XI binding cannot weaken source state")
        if self.complete_prematch_frame or self.gate14_complete:
            raise PrematchMarkerBindingError(
                "marker binding cannot promote complete-frame or Gate-14 claims"
            )


def _player_source_fields(player):
    try:
        registered_club_id = int(player.club_id)
        primary_number = int(player.shirt_number)
    except (AttributeError, TypeError, ValueError) as exc:
        raise PrematchMarkerBindingError(
            "visible marker player requires source club and shirt-number fields"
        ) from exc
    alternate = getattr(player, "alternate_shirt_number", None)
    if alternate is not None:
        try:
            alternate = int(alternate)
        except (TypeError, ValueError) as exc:
            raise PrematchMarkerBindingError(
                "alternate shirt number must preserve runtime byte state"
            ) from exc
    return registered_club_id, primary_number, alternate


def bind_prematch_starting_xi_markers(
    *,
    side0_players,
    side1_players,
    side0_coordinates,
    side1_coordinates,
    side0_team_club_id: int,
    side1_team_club_id: int,
    side0_atlas: PrematchNumberedShirtAtlas,
    side1_atlas: PrematchNumberedShirtAtlas,
    goalkeeper: PrematchGoalkeeperShirt,
) -> BoundPrematchStartingXIMarkers:
    """Bind supplied XI slots and normalized native formation coordinates.

    The coordinate producer itself is already source-closed at 0x499A50. This
    seam accepts those normalized outputs rather than deriving a modern
    formation approximation.
    """
    if type(side0_atlas) is not PrematchNumberedShirtAtlas or type(side1_atlas) is not PrematchNumberedShirtAtlas:
        raise PrematchMarkerBindingError("both sides require exact numbered-shirt atlases")
    if type(goalkeeper) is not PrematchGoalkeeperShirt:
        raise PrematchMarkerBindingError("dedicated goalkeeper source is required")
    for name, value in (
        ("side0_team_club_id", side0_team_club_id),
        ("side1_team_club_id", side1_team_club_id),
    ):
        if type(value) is not int or value < 0:
            raise PrematchMarkerBindingError(f"{name} must be non-negative integer")

    players_by_side = (tuple(side0_players), tuple(side1_players))
    coords_by_side = (tuple(side0_coordinates), tuple(side1_coordinates))
    atlases = (side0_atlas, side1_atlas)
    team_ids = (side0_team_club_id, side1_team_club_id)

    for side in (0, 1):
        if len(players_by_side[side]) > 11 or len(coords_by_side[side]) > 11:
            raise PrematchMarkerBindingError("starting-XI side cannot exceed eleven slots")

    markers = []
    for side in (0, 1):
        players = players_by_side[side]
        coords = coords_by_side[side]
        atlas = atlases[side]
        team_club_id = team_ids[side]
        for slot in range(11):
            player = players[slot] if slot < len(players) else None
            coord = coords[slot] if slot < len(coords) else None
            child = PREMATCH_MARKER_CHILD_STARTS[side] + slot
            if player is None:
                markers.append(
                    BoundPrematchStartingXIMarker(
                        side=side,
                        slot_index=slot,
                        child_index=child,
                        visible=False,
                        rect=None,
                        source_kind=None,
                        source_path=None,
                        frame_number=None,
                        rgba=None,
                    )
                )
                continue
            if (
                type(coord) not in (tuple, list)
                or len(coord) != 2
            ):
                raise PrematchMarkerBindingError(
                    "visible marker requires one source normalized coordinate pair"
                )
            px, py = prematch_pitch_marker_origin(side, coord[0], coord[1])
            rect = OriginalRect(px, py, 36, 32)

            if slot == 0:
                source_kind = "goalkeeper_original"
                source_path = goalkeeper.source_path
                frame_number = None
                rgba = goalkeeper.rgba
            else:
                registered_club_id, primary_number, alternate_number = _player_source_fields(player)
                frame = crop_prematch_numbered_shirt_frame(
                    atlas,
                    player_registered_club_id=registered_club_id,
                    team_club_id=team_club_id,
                    primary_shirt_number=primary_number,
                    alternate_shirt_number=alternate_number,
                )
                source_kind = frame.source_kind
                source_path = frame.source_path
                frame_number = frame.frame_number
                rgba = frame.rgba

            markers.append(
                BoundPrematchStartingXIMarker(
                    side=side,
                    slot_index=slot,
                    child_index=child,
                    visible=True,
                    rect=rect,
                    source_kind=source_kind,
                    source_path=source_path,
                    frame_number=frame_number,
                    rgba=rgba,
                )
            )

    bound = BoundPrematchStartingXIMarkers(markers=tuple(markers))
    if tuple(marker.child_index for marker in bound.markers if marker.slot_index == 0) != PREMATCH_PITCH_MARKER_GOALKEEPER_CHILDREN:
        raise PrematchMarkerBindingError("goalkeeper marker ownership drifted")
    outfield = tuple(
        tuple(marker.child_index for marker in bound.markers if marker.side == side and marker.slot_index > 0)
        for side in (0, 1)
    )
    if outfield != PREMATCH_PITCH_MARKER_OUTFIELD_CHILDREN:
        raise PrematchMarkerBindingError("outfield marker ownership drifted")
    return bound


def prematch_marker_binding_contract() -> dict:
    return {
        "marker_count": 22,
        "child_range": (10, 31),
        "goalkeeper_children": PREMATCH_PITCH_MARKER_GOALKEEPER_CHILDREN,
        "outfield_children": PREMATCH_PITCH_MARKER_OUTFIELD_CHILDREN,
        "marker_size": PREMATCH_PITCH_MARKER_SIZE,
        "formation_coordinates_must_be_source_outputs": True,
        "player_visibility_bound_from_supplied_slots": True,
        "source_shirt_pixels_bound": True,
        "complete_prematch_frame": False,
        "gate14_complete": False,
    }
