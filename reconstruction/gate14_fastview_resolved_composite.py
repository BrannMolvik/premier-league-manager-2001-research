"""Fail-closed resolved-only FastView composite.

Cross-component z-order is not recovered. This module therefore never chooses
which component wins an overlapping pixel. It copies a source-backed RGBA pixel
only when exactly one component plane contributes non-zero alpha at that
coordinate. Pixels with multiple contributors stay transparent and are marked
in a separate one-byte-per-pixel unresolved-overlap mask.

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
class FastViewResolvedOnlyComposite:
    size: tuple[int, int]
    rgba: bytes
    unresolved_overlap_mask: bytes
    resolved_pixel_count: int
    unresolved_overlap_pixel_count: int
    contributing_components: tuple[str, ...]
    source_plane_sha256: tuple[tuple[str, str], ...]
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
    unresolved overlap.
    """

    planes = _ordered_component_planes(rasters)
    width, height = FASTVIEW_SURFACE_SIZE
    pixel_count = width * height
    output = bytearray(pixel_count * 4)
    overlap_mask = bytearray(pixel_count)
    resolved = 0
    overlaps = 0

    for pixel_index in range(pixel_count):
        offset = pixel_index * 4
        owner: FastViewComponentRasterPlane | None = None
        contributor_count = 0

        for plane in planes:
            if plane.rgba[offset + 3] == 0:
                continue
            contributor_count += 1
            if contributor_count == 1:
                owner = plane
            else:
                owner = None
                # More contributors cannot make this pixel resolvable.
                break

        if contributor_count == 1 and owner is not None:
            output[offset:offset + 4] = owner.rgba[offset:offset + 4]
            resolved += 1
        elif contributor_count > 1:
            overlap_mask[pixel_index] = 1
            overlaps += 1

    rgba = bytes(output)
    mask = bytes(overlap_mask)
    components = tuple(plane.component for plane in planes)
    source_hashes = tuple(
        (plane.component, plane.rgba_sha256)
        for plane in planes
    )
    return FastViewResolvedOnlyComposite(
        size=FASTVIEW_SURFACE_SIZE,
        rgba=rgba,
        unresolved_overlap_mask=mask,
        resolved_pixel_count=resolved,
        unresolved_overlap_pixel_count=overlaps,
        contributing_components=components,
        source_plane_sha256=source_hashes,
        rgba_sha256=sha256(rgba).hexdigest(),
        unresolved_overlap_mask_sha256=sha256(mask).hexdigest(),
    )
