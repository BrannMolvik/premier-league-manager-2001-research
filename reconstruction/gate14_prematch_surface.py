"""Source-backed render boundary for the original FM2001 PPreMatchPanel.

This layer joins the already-recovered Match Detail/pre-match asset model to the
same Team_Backgrounds selector/loader used by FastView. It exposes native
800x600 pixel layers and control resources while preserving the source-closed
182-child forward paint order. It does not invent the unresolved
management-to-match launch transition or claim a complete pixel frame merely
because layer order is known.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Mapping

from gate14_fastview_surfaced_picture_selection import (
    FastViewSurfacedResourceSelection,
    build_fastview_surfaced_resource_selection,
)
from gate14_fastview_surfaced_resource_loader import (
    VerifiedFastViewSurfacedResource,
    load_verified_selected_background,
)
from gate14_prematch_rating_widths import (
    PrematchTeamRatingWidths,
    source_prematch_team_rating_widths,
)
from original_front_end_layout import OriginalRect
from original_prematch_panel import (
    PREMATCH_ACTIVE_LEFT,
    PREMATCH_ACTIVE_RIGHT,
    PREMATCH_DISABLED_LEFT,
    PREMATCH_DISABLED_RIGHT,
    PREMATCH_LIVE_BACKGROUND_RECT,
    PREMATCH_FIXTURE_HEADER_RECT,
    PREMATCH_DATE_WEATHER_RECT,
    PREMATCH_TEAM_IDENTITY_RECTS,
    PREMATCH_HEADER_TEXT_STYLE_WRAPPER_VA,
    PREMATCH_TEAM_TEXT_STYLE_WRAPPER_VAS,
    PREMATCH_RATING_TEXT_STYLE_WRAPPER_VA,
    PREMATCH_RATING_CAPTION_RECTS,
    PREMATCH_RATING_LABELS,
    PREMATCH_FIXTURE_HEADER_BUFFER_OFFSET,
    PREMATCH_DATE_WEATHER_BUFFER_OFFSET,
    PREMATCH_VERSUS_LABEL,
    PREMATCH_RATING_LEFT,
    PREMATCH_RATING_RIGHT,
    PREMATCH_RATING_RIGHT2,
    PREMATCH_RATING_ROWS,
    PREMATCH_SELECTORS,
    PREMATCH_PLAYER_STRIP_ROWS,
    PREMATCH_PLAYER_TEXT_ROWS,
    PREMATCH_PLAYER_ROW_TEXT_STYLE_WRAPPER_VA,
    PREMATCH_PLAYER_NUMBER_AUX_WRAPPER_VA,
    PREMATCH_PLAYER_NUMBER_FORMAT,
    PREMATCH_PLAYER_SHIRT_NUMBER_RUNTIME_OFFSET,
    PREMATCH_PLAYER_NAME_MODE_BY_SIDE,
    PREMATCH_SELECTOR_INITIAL_FLAGS,
    PREMATCH_SELECTOR_GROUP_LENGTHS,
    prematch_player_row_variant,
    PREMATCH_CHILD_COUNT,
    PREMATCH_CHILD_ORDER_RANGES,
    PREMATCH_STATIC_PLACEMENTS,
    OriginalPrematchPanelResources,
    load_verified_original_prematch_resources,
)


class PrematchSurfaceError(ValueError):
    pass


@dataclass(frozen=True)
class PrematchRasterLayer:
    role: str
    rect: OriginalRect
    source_path: str
    rgba: bytes

    def __post_init__(self) -> None:
        if not self.role:
            raise PrematchSurfaceError("pre-match raster role must be non-empty")
        if not self.source_path:
            raise PrematchSurfaceError("pre-match raster source path must be non-empty")
        if len(self.rgba) != self.rect.width * self.rect.height * 4:
            raise PrematchSurfaceError("pre-match raster RGBA geometry mismatch")


@dataclass(frozen=True)
class PrematchTextControlSurface:
    """Source-closed text-control placement with deliberately bounded content."""

    role: str
    rect: OriginalRect
    style_wrapper_va: int
    fixed_text: str | None = None
    source_buffer_offset: int | None = None
    dynamic_text_source_closed: bool = False

    def __post_init__(self) -> None:
        if not self.role:
            raise PrematchSurfaceError("pre-match text-control role must be non-empty")
        if type(self.style_wrapper_va) is not int or self.style_wrapper_va <= 0:
            raise PrematchSurfaceError("pre-match text-control style wrapper must be a VA")
        if self.fixed_text is not None and self.source_buffer_offset is not None:
            raise PrematchSurfaceError(
                "pre-match text control cannot be both fixed and panel-buffer sourced"
            )
        if self.fixed_text is None and self.source_buffer_offset is None:
            if self.role not in ("team_identity_0", "team_identity_1"):
                raise PrematchSurfaceError(
                    "unbound dynamic text is allowed only for source-proven team identities"
                )
        if self.dynamic_text_source_closed and self.fixed_text is None:
            raise PrematchSurfaceError(
                "dynamic pre-match text binding is not source-closed by this surface"
            )


def source_prematch_text_controls() -> tuple[PrematchTextControlSurface, ...]:
    """Expose only exact native text-control geometry/content boundaries."""

    controls = [
        PrematchTextControlSurface(
            role="fixture_header",
            rect=PREMATCH_FIXTURE_HEADER_RECT,
            style_wrapper_va=PREMATCH_HEADER_TEXT_STYLE_WRAPPER_VA,
            source_buffer_offset=PREMATCH_FIXTURE_HEADER_BUFFER_OFFSET,
        ),
        PrematchTextControlSurface(
            role="date_weather",
            rect=PREMATCH_DATE_WEATHER_RECT,
            style_wrapper_va=PREMATCH_HEADER_TEXT_STYLE_WRAPPER_VA,
            source_buffer_offset=PREMATCH_DATE_WEATHER_BUFFER_OFFSET,
        ),
        PrematchTextControlSurface(
            role="team_identity_0",
            rect=PREMATCH_TEAM_IDENTITY_RECTS[0],
            style_wrapper_va=PREMATCH_TEAM_TEXT_STYLE_WRAPPER_VAS[0],
        ),
        PrematchTextControlSurface(
            role="versus",
            rect=PREMATCH_TEAM_IDENTITY_RECTS[1],
            style_wrapper_va=PREMATCH_TEAM_TEXT_STYLE_WRAPPER_VAS[1],
            fixed_text=PREMATCH_VERSUS_LABEL,
        ),
        PrematchTextControlSurface(
            role="team_identity_1",
            rect=PREMATCH_TEAM_IDENTITY_RECTS[2],
            style_wrapper_va=PREMATCH_TEAM_TEXT_STYLE_WRAPPER_VAS[2],
        ),
    ]
    for side_name, rects in (
        ("left", PREMATCH_RATING_CAPTION_RECTS[:4]),
        ("right", PREMATCH_RATING_CAPTION_RECTS[4:]),
    ):
        for label, rect in zip(PREMATCH_RATING_LABELS, rects, strict=True):
            controls.append(
                PrematchTextControlSurface(
                    role=f"rating_{side_name}_{label.lower()}",
                    rect=rect,
                    style_wrapper_va=PREMATCH_RATING_TEXT_STYLE_WRAPPER_VA,
                    fixed_text=label,
                    dynamic_text_source_closed=True,
                )
            )
    return tuple(controls)


@dataclass(frozen=True)
class PrematchSelectorSurface:
    mode: int
    event_id: int
    label: str
    rect: OriginalRect
    atlas: object
    initial_flags: int = PREMATCH_SELECTOR_INITIAL_FLAGS
    group_lengths: tuple[int, ...] = PREMATCH_SELECTOR_GROUP_LENGTHS
    native_visual_state_source_closed: bool = True
    persistent_selected_visual: bool = False

    def __post_init__(self) -> None:
        if self.initial_flags != PREMATCH_SELECTOR_INITIAL_FLAGS:
            raise PrematchSurfaceError("pre-match selector initial flags drifted")
        if self.group_lengths != PREMATCH_SELECTOR_GROUP_LENGTHS:
            raise PrematchSurfaceError("pre-match selector frame groups drifted")
        if not self.native_visual_state_source_closed or self.persistent_selected_visual:
            raise PrematchSurfaceError("pre-match selector cannot invent radio selection state")


@dataclass(frozen=True)
class PrematchPlayerTextSurface:
    side: str
    slot_index: int
    roster_group: str
    number_rect: OriginalRect
    name_rect: OriginalRect
    strip_child_index: int
    number_child_index: int
    name_child_index: int
    disabled_child_index: int | None
    style_wrapper_va: int = PREMATCH_PLAYER_ROW_TEXT_STYLE_WRAPPER_VA
    number_aux_wrapper_va: int = PREMATCH_PLAYER_NUMBER_AUX_WRAPPER_VA
    number_format: str = PREMATCH_PLAYER_NUMBER_FORMAT
    shirt_number_runtime_offset: int = PREMATCH_PLAYER_SHIRT_NUMBER_RUNTIME_OFFSET
    name_mode: int = 0

    def __post_init__(self) -> None:
        if self.side not in ("left", "right"):
            raise PrematchSurfaceError("pre-match player text side must be left/right")
        expected_name_mode = PREMATCH_PLAYER_NAME_MODE_BY_SIDE[0 if self.side == "left" else 1]
        if self.name_mode != expected_name_mode:
            raise PrematchSurfaceError("pre-match player name mode differs from source")
        if self.style_wrapper_va != PREMATCH_PLAYER_ROW_TEXT_STYLE_WRAPPER_VA:
            raise PrematchSurfaceError("pre-match player text style wrapper drifted")
        if self.number_format != PREMATCH_PLAYER_NUMBER_FORMAT:
            raise PrematchSurfaceError("pre-match player number format drifted")

    def strip_variant(self, participant_count: int) -> str:
        return prematch_player_row_variant(self.slot_index, participant_count)


@dataclass(frozen=True)
class PrematchPlayerStripSurface:
    """Source-backed row art without guessing the unresolved reserve variant."""

    side: str
    roster_group: str
    row_index: int
    rect: OriginalRect
    active_source_path: str
    active_rgba: bytes
    disabled_source_path: str | None = None
    disabled_rgba: bytes | None = None
    variant_state_source_closed: bool = True

    def __post_init__(self) -> None:
        if self.side not in ("left", "right"):
            raise PrematchSurfaceError("pre-match player strip side must be left/right")
        if self.roster_group not in ("starter", "reserve"):
            raise PrematchSurfaceError("pre-match player strip group must be starter/reserve")
        if self.row_index < 0:
            raise PrematchSurfaceError("pre-match player strip row index must be non-negative")
        if (self.rect.width, self.rect.height) != (200, 16):
            raise PrematchSurfaceError("pre-match player strip geometry must remain 200x16")
        expected = self.rect.width * self.rect.height * 4
        if len(self.active_rgba) != expected or not self.active_source_path:
            raise PrematchSurfaceError("pre-match active strip source is invalid")
        if self.roster_group == "starter":
            if self.disabled_source_path is not None or self.disabled_rgba is not None:
                raise PrematchSurfaceError("native starter strip cannot invent a disabled layer")
        else:
            if (
                not self.disabled_source_path
                or self.disabled_rgba is None
                or len(self.disabled_rgba) != expected
            ):
                raise PrematchSurfaceError("native reserve strip requires both source variants")
        if not self.variant_state_source_closed:
            raise PrematchSurfaceError(
                "pre-match player-strip variant state must retain source-closed count rule"
            )


@dataclass(frozen=True)
class PrematchRatingSurface:
    native_record_discriminator: int
    native_width_function_va: int
    left_rect: OriginalRect
    right_rect: OriginalRect
    left_dynamic_rgba: bytes
    left_base_rgba: bytes
    right_base_rgba: bytes
    right_dynamic_mask_rgba: bytes

    def __post_init__(self) -> None:
        expected = self.left_rect.width * self.left_rect.height * 4
        if self.left_rect.width != 171 or self.left_rect.height != 16:
            raise PrematchSurfaceError("left rating geometry drifted")
        if self.right_rect.width != 171 or self.right_rect.height != 16:
            raise PrematchSurfaceError("right rating geometry drifted")
        for payload in (
            self.left_dynamic_rgba,
            self.left_base_rgba,
            self.right_base_rgba,
            self.right_dynamic_mask_rgba,
        ):
            if len(payload) != expected:
                raise PrematchSurfaceError("rating source geometry mismatch")


@dataclass(frozen=True)
class BoundPrematchRatingSurface:
    """One source row with exact state-bound left/right dynamic rectangles."""

    source: PrematchRatingSurface
    semantic_group: str
    left_width: int
    right_width: int
    left_dynamic_rect: OriginalRect
    right_dynamic_rect: OriginalRect

    def __post_init__(self) -> None:
        if not self.semantic_group:
            raise PrematchSurfaceError("bound rating group must be named")
        for width in (self.left_width, self.right_width):
            if not 0 <= int(width) <= 171:
                raise PrematchSurfaceError("bound rating width must be in 0..171")
        if (
            self.left_dynamic_rect.x,
            self.left_dynamic_rect.y,
            self.left_dynamic_rect.width,
            self.left_dynamic_rect.height,
        ) != (
            self.source.left_rect.x,
            self.source.left_rect.y,
            self.left_width,
            self.source.left_rect.height,
        ):
            raise PrematchSurfaceError("left dynamic rating rectangle is not native")
        if (
            self.right_dynamic_rect.x,
            self.right_dynamic_rect.y,
            self.right_dynamic_rect.width,
            self.right_dynamic_rect.height,
        ) != (
            self.source.right_rect.x + self.source.right_rect.width - self.right_width,
            self.source.right_rect.y,
            self.right_width,
            self.source.right_rect.height,
        ):
            raise PrematchSurfaceError("right dynamic rating rectangle is not mirrored")


@dataclass(frozen=True)
class BoundPrematchRatingRows:
    rows: tuple[BoundPrematchRatingSurface, ...]
    left_widths: PrematchTeamRatingWidths
    right_widths: PrematchTeamRatingWidths
    source_state_bound: bool = True
    native_mirroring_preserved: bool = True
    complete_prematch_frame: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        if len(self.rows) != 4:
            raise PrematchSurfaceError("bound pre-match rating set must have four rows")
        if not self.source_state_bound or not self.native_mirroring_preserved:
            raise PrematchSurfaceError("bound pre-match ratings cannot weaken source state")
        if self.complete_prematch_frame or self.gate14_complete:
            raise PrematchSurfaceError(
                "rating binding cannot promote complete-frame or Gate-14 claims"
            )


_PREMATCH_RATING_GROUP_NAMES = {
    3: "goalkeeper",
    0: "defence",
    1: "midfield",
    2: "attack",
}


def bind_prematch_rating_widths(
    boundary: "PrematchSurfaceBoundary",
    *,
    left_widths: PrematchTeamRatingWidths,
    right_widths: PrematchTeamRatingWidths,
) -> BoundPrematchRatingRows:
    """Bind exact native width results without mutating the resource boundary.

    Native side 0 grows rightward from x=65. Side 1 is anchored at its right
    edge (x=564+171) and therefore grows leftward by subtracting the width.
    """
    if type(boundary) is not PrematchSurfaceBoundary:
        raise PrematchSurfaceError("rating binding requires exact PrematchSurfaceBoundary")
    if type(left_widths) is not PrematchTeamRatingWidths:
        raise PrematchSurfaceError("left widths require exact PrematchTeamRatingWidths")
    if type(right_widths) is not PrematchTeamRatingWidths:
        raise PrematchSurfaceError("right widths require exact PrematchTeamRatingWidths")

    rows = []
    for source in boundary.rating_rows:
        discriminator = int(source.native_record_discriminator)
        try:
            semantic_group = _PREMATCH_RATING_GROUP_NAMES[discriminator]
        except KeyError as exc:
            raise PrematchSurfaceError(
                f"unsupported native rating discriminator: {discriminator}"
            ) from exc
        left_width = left_widths.by_discriminator(discriminator)
        right_width = right_widths.by_discriminator(discriminator)
        rows.append(
            BoundPrematchRatingSurface(
                source=source,
                semantic_group=semantic_group,
                left_width=left_width,
                right_width=right_width,
                left_dynamic_rect=OriginalRect(
                    source.left_rect.x,
                    source.left_rect.y,
                    left_width,
                    source.left_rect.height,
                ),
                right_dynamic_rect=OriginalRect(
                    source.right_rect.x + source.right_rect.width - right_width,
                    source.right_rect.y,
                    right_width,
                    source.right_rect.height,
                ),
            )
        )
    return BoundPrematchRatingRows(
        rows=tuple(rows),
        left_widths=left_widths,
        right_widths=right_widths,
    )


@dataclass(frozen=True)
class PrematchChildFamilyCoverage:
    """One exact native child-array family and its clean-room frame readiness."""

    role: str
    start_index: int
    end_index: int
    represented_controls: int
    supplied_state_complete: bool
    blocker: str | None = None

    @property
    def source_control_count(self) -> int:
        return self.end_index - self.start_index + 1

    def __post_init__(self) -> None:
        if not self.role or self.start_index < 0 or self.end_index < self.start_index:
            raise PrematchSurfaceError("invalid pre-match child-family range")
        if not 0 <= self.represented_controls <= self.source_control_count:
            raise PrematchSurfaceError(
                "pre-match represented control count exceeds source child family"
            )
        if self.supplied_state_complete:
            if self.represented_controls != self.source_control_count or self.blocker is not None:
                raise PrematchSurfaceError(
                    "complete pre-match family must represent every source control"
                )
        elif not self.blocker:
            raise PrematchSurfaceError(
                "incomplete pre-match family must retain its explicit blocker"
            )


_PREMATCH_CHILD_COVERAGE = {
    "live_background": (1, True, None),
    "pitch": (1, True, None),
    "top_bar": (1, True, None),
    "fixture_header": (1, False, "dynamic fixture-header buffer is not bound"),
    "date_weather_line": (1, False, "dynamic date/weather buffer is not bound"),
    "team_badges": (0, False, "team badge pixels are not staged in the pre-match surface"),
    "team_identity_text": (3, False, "left/right dynamic team identity text is not bound"),
    "starting_xi_pitch_markers": (0, False, "22 pitch-marker placement/state controls are unresolved"),
    "side0_starter_rows": (11, False, "starter row text/content controls remain unresolved"),
    "side0_slots_11_17": (
        14,
        False,
        "reserve row text plus active/disabled runtime selection remain unresolved",
    ),
    "side1_starter_rows": (11, False, "starter row text/content controls remain unresolved"),
    "side1_slots_11_17": (
        14,
        False,
        "reserve row text plus active/disabled runtime selection remain unresolved",
    ),
    "rating_bar_layers": (
        16,
        False,
        "base surface has source pixels but supplied-state dynamic widths are not bound",
    ),
    "rating_captions": (8, True, None),
    "match_detail_selectors": (
        4,
        False,
        "selector atlas/geometry are present but exact runtime visual state is unresolved",
    ),
}


def prematch_child_family_coverage() -> tuple[PrematchChildFamilyCoverage, ...]:
    coverage = tuple(
        PrematchChildFamilyCoverage(
            role=role,
            start_index=start,
            end_index=end,
            represented_controls=_PREMATCH_CHILD_COVERAGE[role][0],
            supplied_state_complete=_PREMATCH_CHILD_COVERAGE[role][1],
            blocker=_PREMATCH_CHILD_COVERAGE[role][2],
        )
        for role, start, end in PREMATCH_CHILD_ORDER_RANGES
    )
    flattened = tuple(
        index
        for family in coverage
        for index in range(family.start_index, family.end_index + 1)
    )
    if flattened != tuple(range(PREMATCH_CHILD_COUNT)):
        raise PrematchSurfaceError("pre-match child coverage no longer partitions 0..181")
    return coverage


@dataclass(frozen=True)
class PrematchSurfaceBoundary:
    selection: FastViewSurfacedResourceSelection
    background: PrematchRasterLayer
    static_layers: tuple[PrematchRasterLayer, ...]
    text_controls: tuple[PrematchTextControlSurface, ...]
    player_text_rows: tuple[PrematchPlayerTextSurface, ...]
    player_strip_rows: tuple[PrematchPlayerStripSurface, ...]
    selectors: tuple[PrematchSelectorSurface, ...]
    rating_rows: tuple[PrematchRatingSurface, ...]
    font: object
    team_backgrounds_contract_reused: bool = True
    source_assets_verified: bool = True
    native_geometry_preserved: bool = True
    rating_dynamic_widths_bound_to_cleanroom_state: bool = False
    full_cross_layer_draw_order_recovered: bool = True
    management_launch_trigger_recovered: bool = False
    complete_prematch_frame: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        if type(self.selection) is not FastViewSurfacedResourceSelection:
            raise PrematchSurfaceError(
                "pre-match boundary requires exact source-backed background selection"
            )
        if self.background.role != "background":
            raise PrematchSurfaceError("pre-match background layer identity mismatch")
        if (
            self.background.rect.x,
            self.background.rect.y,
            self.background.rect.width,
            self.background.rect.height,
        ) != (0, 0, 800, 600):
            raise PrematchSurfaceError("pre-match live background must remain 800x600")
        if len(self.static_layers) != len(PREMATCH_STATIC_PLACEMENTS):
            raise PrematchSurfaceError("pre-match static layer set is incomplete")
        if self.text_controls != source_prematch_text_controls():
            raise PrematchSurfaceError("pre-match native text-control set is incomplete")
        if self.player_text_rows != source_prematch_player_text_rows():
            raise PrematchSurfaceError("pre-match player text row set is incomplete")
        if len(self.player_strip_rows) != len(PREMATCH_PLAYER_STRIP_ROWS):
            raise PrematchSurfaceError("pre-match player strip row set is incomplete")
        if any(not row.variant_state_source_closed for row in self.player_strip_rows):
            raise PrematchSurfaceError(
                "pre-match player strip boundary lost source-closed reserve state"
            )
        if len(self.selectors) != len(PREMATCH_SELECTORS):
            raise PrematchSurfaceError("pre-match selector surface set is incomplete")
        if any(
            not selector.native_visual_state_source_closed
            or selector.persistent_selected_visual
            for selector in self.selectors
        ):
            raise PrematchSurfaceError(
                "pre-match selector surface lost generic Button@ease state"
            )
        if len(self.rating_rows) != len(PREMATCH_RATING_ROWS):
            raise PrematchSurfaceError("pre-match rating row set is incomplete")
        if not (
            self.team_backgrounds_contract_reused
            and self.source_assets_verified
            and self.native_geometry_preserved
        ):
            raise PrematchSurfaceError("pre-match boundary cannot weaken verified source state")
        if not self.full_cross_layer_draw_order_recovered:
            raise PrematchSurfaceError(
                "pre-match boundary must preserve the source-closed child draw order"
            )
        if (
            self.rating_dynamic_widths_bound_to_cleanroom_state
            or self.management_launch_trigger_recovered
            or self.complete_prematch_frame
            or self.gate14_complete
        ):
            raise PrematchSurfaceError(
                "pre-match boundary cannot promote unresolved runtime/fidelity claims"
            )


def source_prematch_player_text_rows() -> tuple[PrematchPlayerTextSurface, ...]:
    return tuple(
        PrematchPlayerTextSurface(
            side=row.side,
            slot_index=row.slot_index,
            roster_group=row.roster_group,
            number_rect=row.number_rect,
            name_rect=row.name_rect,
            strip_child_index=row.strip_child_index,
            number_child_index=row.number_child_index,
            name_child_index=row.name_child_index,
            disabled_child_index=row.disabled_child_index,
            name_mode=PREMATCH_PLAYER_NAME_MODE_BY_SIDE[0 if row.side == "left" else 1],
        )
        for row in PREMATCH_PLAYER_TEXT_ROWS
    )


def _layer_from_decoded(role, rect, spec, decoded) -> PrematchRasterLayer:
    if (decoded.width, decoded.height) != (rect.width, rect.height):
        raise PrematchSurfaceError(f"{role} decoded geometry differs from native rect")
    return PrematchRasterLayer(
        role=role,
        rect=rect,
        source_path=spec.source_path,
        rgba=decoded.rgba,
    )


def bind_prematch_rating_state(
    boundary: "PrematchSurfaceBoundary",
    *,
    left_starters,
    right_starters,
    positions: Mapping[int, object],
) -> BoundPrematchRatingRows:
    """Bind both source XIs through the native rating calculation and geometry."""
    return bind_prematch_rating_widths(
        boundary,
        left_widths=source_prematch_team_rating_widths(left_starters, positions),
        right_widths=source_prematch_team_rating_widths(right_starters, positions),
    )


def build_verified_prematch_surface_boundary(
    *,
    match_date: date,
    clubs: Mapping[int, object],
    countries: Mapping[int, object],
    home_club_id: int,
    away_club_id: int,
    background_club_override_id: int | None,
    source_root,
    original_executable,
) -> PrematchSurfaceBoundary:
    """Resolve and load only the source-proven pre-match presentation slice."""
    selection = build_fastview_surfaced_resource_selection(
        match_date=match_date,
        clubs=clubs,
        countries=countries,
        home_club_id=home_club_id,
        away_club_id=away_club_id,
        background_club_override_id=background_club_override_id,
    )
    background_resource: VerifiedFastViewSurfacedResource = (
        load_verified_selected_background(
            selection,
            source_root=source_root,
            original_executable=original_executable,
        )
    )
    if background_resource.role != "background":
        raise PrematchSurfaceError("shared Team_Backgrounds loader returned wrong role")
    if background_resource.geometry != (800, 600):
        raise PrematchSurfaceError("shared Team_Backgrounds resource is not 800x600")

    resources: OriginalPrematchPanelResources = load_verified_original_prematch_resources(
        source_root=source_root,
        original_executable=original_executable,
    )

    background = PrematchRasterLayer(
        role="background",
        rect=PREMATCH_LIVE_BACKGROUND_RECT,
        source_path=background_resource.source_path,
        rgba=background_resource.rgba,
    )
    static_layers = tuple(
        _layer_from_decoded(
            placement.role,
            placement.rect,
            placement.spec,
            resources.decoded(placement.spec.source_path),
        )
        for placement in PREMATCH_STATIC_PLACEMENTS
    )
    player_strip_rows = []
    for row in PREMATCH_PLAYER_STRIP_ROWS:
        active = resources.decoded(row.active_spec.source_path)
        disabled = (
            resources.decoded(row.disabled_spec.source_path)
            if row.disabled_spec is not None
            else None
        )
        player_strip_rows.append(
            PrematchPlayerStripSurface(
                side=row.side,
                roster_group=row.roster_group,
                row_index=row.row_index,
                rect=row.rect,
                active_source_path=row.active_spec.source_path,
                active_rgba=active.rgba,
                disabled_source_path=(
                    row.disabled_spec.source_path
                    if row.disabled_spec is not None
                    else None
                ),
                disabled_rgba=disabled.rgba if disabled is not None else None,
            )
        )

    selectors = tuple(
        PrematchSelectorSurface(
            mode=int(selector.mode),
            event_id=selector.event_id,
            label=selector.label,
            rect=selector.rect,
            atlas=resources.selector_atlas,
        )
        for selector in PREMATCH_SELECTORS
    )

    left_dynamic = resources.decoded(PREMATCH_RATING_LEFT.source_path)
    left_base = resources.decoded(PREMATCH_RATING_RIGHT.source_path)
    right_base = resources.decoded(PREMATCH_RATING_RIGHT2.source_path)
    right_mask = resources.decoded(PREMATCH_RATING_RIGHT.source_path)
    rating_rows = tuple(
        PrematchRatingSurface(
            native_record_discriminator=row.native_record_discriminator,
            native_width_function_va=row.native_width_function_va,
            left_rect=OriginalRect(row.left_x, row.y, row.full_width, row.height),
            right_rect=OriginalRect(row.right_x, row.y, row.full_width, row.height),
            left_dynamic_rgba=left_dynamic.rgba,
            left_base_rgba=left_base.rgba,
            right_base_rgba=right_base.rgba,
            right_dynamic_mask_rgba=right_mask.rgba,
        )
        for row in PREMATCH_RATING_ROWS
    )

    return PrematchSurfaceBoundary(
        selection=selection,
        background=background,
        static_layers=static_layers,
        text_controls=source_prematch_text_controls(),
        player_text_rows=source_prematch_player_text_rows(),
        player_strip_rows=tuple(player_strip_rows),
        selectors=selectors,
        rating_rows=rating_rows,
        font=resources.font,
    )


def prematch_surface_contract() -> dict:
    return {
        "native_surface": (800, 600),
        "team_backgrounds_selector_reused": True,
        "team_backgrounds_loader_reused": True,
        "dedicated_static_asset_roles": tuple(
            placement.role for placement in PREMATCH_STATIC_PLACEMENTS
        ),
        "text_control_count": len(source_prematch_text_controls()),
        "text_control_roles": tuple(control.role for control in source_prematch_text_controls()),
        "dynamic_fixture_and_date_buffers_bound": False,
        "team_identity_text_bound": False,
        "fixed_versus_and_rating_captions_available": True,
        "player_strip_row_count": len(PREMATCH_PLAYER_STRIP_ROWS),
        "player_strip_rows_source_geometry_available": True,
        "reserve_variant_state_source_closed": False,
        "selector_modes": tuple(int(selector.mode) for selector in PREMATCH_SELECTORS),
        "selector_events": tuple(selector.event_id for selector in PREMATCH_SELECTORS),
        "rating_discriminators": tuple(
            row.native_record_discriminator for row in PREMATCH_RATING_ROWS
        ),
        "rating_width_binding_available": True,
        "rating_state_binding_available": True,
        "rating_dynamic_widths_bound_by_resource_loader": False,
        "rating_dynamic_widths_bound_to_cleanroom_state": False,
        "source_child_count": PREMATCH_CHILD_COUNT,
        "child_order_ranges": PREMATCH_CHILD_ORDER_RANGES,
        "represented_child_controls": sum(
            family.represented_controls for family in prematch_child_family_coverage()
        ),
        "complete_child_families": tuple(
            family.role
            for family in prematch_child_family_coverage()
            if family.supplied_state_complete
        ),
        "unresolved_child_families": tuple(
            family.role
            for family in prematch_child_family_coverage()
            if not family.supplied_state_complete
        ),
        "child_family_coverage": prematch_child_family_coverage(),
        "full_cross_layer_draw_order_recovered": True,
        "management_launch_trigger_recovered": False,
        "complete_prematch_frame": False,
        "gate14_complete": False,
    }
