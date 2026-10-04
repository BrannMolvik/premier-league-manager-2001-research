"""Fail-closed resolved-only FastView composite.

Cross-component z-order is not recovered. This module therefore never chooses
which component wins an overlapping pixel. It copies a source-backed RGBA pixel
only when exactly one component plane contributes non-zero alpha at that
coordinate. Pixels with multiple contributors stay transparent and are marked
in a separate one-byte-per-pixel unresolved-overlap mask.

The result also records the exact component combinations and bounding rectangles
behind masked overlaps. That topology narrows later native draw-order tracing
without treating component order, alpha, or geometry as z-order evidence.

The result is useful renderer input for the portion of FastView whose ownership
is already unambiguous, but it is deliberately not a complete or flattened
FastView frame.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from gate14_fastview_component_rasters import (
    FastViewComponentRasterPlane,
    FastViewComponentRasterSet,
)
from gate14_fastview_partial_surface import FASTVIEW_SURFACE_SIZE


class FastViewResolvedCompositeError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewUnresolvedOverlapGroup:
    """One exact contributor set behind unresolved FastView pixels."""

    components: tuple[str, ...]
    pixel_count: int
    bounding_rect: tuple[int, int, int, int]

    def __post_init__(self) -> None:
        if (
            type(self.components) is not tuple
            or len(self.components) < 2
            or any(not isinstance(name, str) or not name for name in self.components)
            or len(set(self.components)) != len(self.components)
        ):
            raise FastViewResolvedCompositeError(
                "overlap group must contain at least two unique component names"
            )
        if type(self.pixel_count) is not int or self.pixel_count <= 0:
            raise FastViewResolvedCompositeError(
                "overlap group pixel_count must be positive"
            )
        if (
            type(self.bounding_rect) is not tuple
            or len(self.bounding_rect) != 4
            or any(type(value) is not int for value in self.bounding_rect)
        ):
            raise FastViewResolvedCompositeError(
                "overlap group bounding rect must contain four integers"
            )
        left, top, right, bottom = self.bounding_rect
        width, height = FASTVIEW_SURFACE_SIZE
        if not (0 <= left < right <= width and 0 <= top < bottom <= height):
            raise FastViewResolvedCompositeError(
                "overlap group bounding rect must remain inside FastView"
            )


@dataclass(frozen=True)
class FastViewResolvedOnlyComposite:
    size: tuple[int, int]
    rgba: bytes
    unresolved_overlap_mask: bytes
    resolved_pixel_count: int
    unresolved_overlap_pixel_count: int
    contributing_components: tuple[str, ...]
    source_plane_sha256: tuple[tuple[str, str], ...]
    unresolved_overlap_groups: tuple[FastViewUnresolvedOverlapGroup, ...]
    rgba_sha256: str
    unresolved_overlap_mask_sha256: str
    cross_component_z_order_recovered: bool = False
    flattened_frame_available: bool = False
    complete_fastview_frame: bool = False

    def __post_init__(self) -> None:
        if self.size != FASTVIEW_SURFACE_SIZE:
            raise FastViewResolvedCompositeError(
                "resolved-only FastView composite must remain 800x600"
            )
        width, height = self.size
        pixel_count = width * height
        if len(self.rgba) != pixel_count * 4:
            raise FastViewResolvedCompositeError(
                "resolved-only composite RGBA payload has wrong size"
            )
        if len(self.unresolved_overlap_mask) != pixel_count:
            raise FastViewResolvedCompositeError(
                "resolved-only overlap mask has wrong size"
            )
        if any(value not in (0, 1) for value in self.unresolved_overlap_mask):
            raise FastViewResolvedCompositeError(
                "resolved-only overlap mask must contain only 0/1 bytes"
            )
        if (
            type(self.resolved_pixel_count) is not int
            or self.resolved_pixel_count < 0
            or type(self.unresolved_overlap_pixel_count) is not int
            or self.unresolved_overlap_pixel_count < 0
            or self.resolved_pixel_count + self.unresolved_overlap_pixel_count
            > pixel_count
        ):
            raise FastViewResolvedCompositeError(
                "resolved-only pixel counts are invalid"
            )
        if sum(self.unresolved_overlap_mask) != self.unresolved_overlap_pixel_count:
            raise FastViewResolvedCompositeError(
                "resolved-only overlap count does not match mask"
            )
        if len(set(self.contributing_components)) != len(
            self.contributing_components
        ):
            raise FastViewResolvedCompositeError(
                "resolved-only component identities must be unique"
            )
        if tuple(name for name, _digest in self.source_plane_sha256) != (
            self.contributing_components
        ):
            raise FastViewResolvedCompositeError(
                "resolved-only source hash order must match components"
            )
        for _name, digest in self.source_plane_sha256:
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(char not in "0123456789abcdef" for char in digest)
            ):
                raise FastViewResolvedCompositeError(
                    "resolved-only source plane hash must be lowercase SHA-256"
                )

        if (
            type(self.unresolved_overlap_groups) is not tuple
            or any(
                type(group) is not FastViewUnresolvedOverlapGroup
                for group in self.unresolved_overlap_groups
            )
        ):
            raise FastViewResolvedCompositeError(
                "resolved-only overlap groups must use exact overlap-group records"
            )
        group_keys = tuple(group.components for group in self.unresolved_overlap_groups)
        if len(set(group_keys)) != len(group_keys):
            raise FastViewResolvedCompositeError(
                "resolved-only overlap component sets must be unique"
            )
        component_positions = {
            name: index for index, name in enumerate(self.contributing_components)
        }
        for group in self.unresolved_overlap_groups:
            try:
                positions = tuple(
                    component_positions[name] for name in group.components
                )
            except KeyError as exc:
                raise FastViewResolvedCompositeError(
                    "overlap group references an unknown component"
                ) from exc
            if positions != tuple(sorted(positions)):
                raise FastViewResolvedCompositeError(
                    "overlap group component order must match source plane order"
                )
        if (
            sum(group.pixel_count for group in self.unresolved_overlap_groups)
            != self.unresolved_overlap_pixel_count
        ):
            raise FastViewResolvedCompositeError(
                "overlap group pixel counts must cover every unresolved pixel"
            )

        if sha256(self.rgba).hexdigest() != self.rgba_sha256:
            raise FastViewResolvedCompositeError(
                "resolved-only RGBA SHA-256 does not match payload"
            )
        if (
            sha256(self.unresolved_overlap_mask).hexdigest()
            != self.unresolved_overlap_mask_sha256
        ):
            raise FastViewResolvedCompositeError(
                "resolved-only overlap-mask SHA-256 does not match payload"
            )
        if (
            self.cross_component_z_order_recovered
            or self.flattened_frame_available
            or self.complete_fastview_frame
        ):
            raise FastViewResolvedCompositeError(
                "resolved-only composite cannot promote unresolved frame fidelity"
            )


def _ordered_component_planes(
    rasters: FastViewComponentRasterSet,
) -> tuple[FastViewComponentRasterPlane, ...]:
    if type(rasters) is not FastViewComponentRasterSet:
        raise FastViewResolvedCompositeError(
            "resolved-only composite requires exact FastViewComponentRasterSet"
        )

    planes = [
        rasters.chrome,
        rasters.possession_diagram,
        rasters.possession_figures,
    ]
    for optional in (
        rasters.team_table,
        rasters.league_scores,
        rasters.league_table,
    ):
        if optional is not None:
            planes.append(optional)

    if len({plane.component for plane in planes}) != len(planes):
        raise FastViewResolvedCompositeError(
            "resolved-only component plane identities must be unique"
        )
    return tuple(planes)


def compose_fastview_resolved_only_pixels(
    rasters: FastViewComponentRasterSet,
) -> FastViewResolvedOnlyComposite:
    """Copy only pixels with exactly one source-backed component owner.

    A contributor is any component plane whose stored pixel has non-zero alpha.
    If two or more planes contribute at the same coordinate, no z-order is
    guessed: the output pixel stays transparent and mask byte 1 records the
    unresolved overlap. Exact contributor combinations and their aggregate
    half-open bounding rectangles are retained only as trace-narrowing metadata.
    """

    planes = _ordered_component_planes(rasters)
    width, height = FASTVIEW_SURFACE_SIZE
    pixel_count = width * height
    output = bytearray(pixel_count * 4)
    overlap_mask = bytearray(pixel_count)
    resolved = 0
    overlaps = 0

    # key -> [pixel_count, min_x, min_y, max_x_exclusive, max_y_exclusive]
    overlap_group_stats: dict[tuple[str, ...], list[int]] = {}

    for pixel_index in range(pixel_count):
        offset = pixel_index * 4
        contributors = tuple(
            plane
            for plane in planes
            if plane.rgba[offset + 3] != 0
        )

        if len(contributors) == 1:
            owner = contributors[0]
            output[offset:offset + 4] = owner.rgba[offset:offset + 4]
            resolved += 1
        elif len(contributors) > 1:
            overlap_mask[pixel_index] = 1
            overlaps += 1

            key = tuple(plane.component for plane in contributors)
            x = pixel_index % width
            y = pixel_index // width
            stats = overlap_group_stats.get(key)
            if stats is None:
                overlap_group_stats[key] = [1, x, y, x + 1, y + 1]
            else:
                stats[0] += 1
                stats[1] = min(stats[1], x)
                stats[2] = min(stats[2], y)
                stats[3] = max(stats[3], x + 1)
                stats[4] = max(stats[4], y + 1)

    rgba = bytes(output)
    mask = bytes(overlap_mask)
    components = tuple(plane.component for plane in planes)
    source_hashes = tuple(
        (plane.component, plane.rgba_sha256)
        for plane in planes
    )
    overlap_groups = tuple(
        FastViewUnresolvedOverlapGroup(
            components=key,
            pixel_count=stats[0],
            bounding_rect=(stats[1], stats[2], stats[3], stats[4]),
        )
        for key, stats in overlap_group_stats.items()
    )
    return FastViewResolvedOnlyComposite(
        size=FASTVIEW_SURFACE_SIZE,
        rgba=rgba,
        unresolved_overlap_mask=mask,
        resolved_pixel_count=resolved,
        unresolved_overlap_pixel_count=overlaps,
        contributing_components=components,
        source_plane_sha256=source_hashes,
        unresolved_overlap_groups=overlap_groups,
        rgba_sha256=sha256(rgba).hexdigest(),
        unresolved_overlap_mask_sha256=sha256(mask).hexdigest(),
    )
