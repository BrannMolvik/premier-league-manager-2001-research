"""Exact coverage accounting for the fail-closed FastView composite.

This diagnostic distinguishes three exhaustive pixel classes:

* exactly one verified visible/non-zero-alpha component contributor -> resolved;
* two or more verified contributors -> unresolved cross-component overlap;
* no currently verified visible contributor -> no_verified_visible_contributor.

The third class is intentionally not called "missing artwork": transparent pixels
inside verified resources and still-unbound source layers can both contribute to
that count. The audit quantifies the current renderer boundary without inventing
background ownership or z-order.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_fastview_resolved_composite import (
    FastViewResolvedOnlyComposite,
    FastViewUnresolvedOverlapGroup,
)


class FastViewFrameCoverageError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewFrameCoverage:
    size: tuple[int, int]
    total_pixel_count: int
    resolved_pixel_count: int
    unresolved_overlap_pixel_count: int
    no_verified_visible_contributor_pixel_count: int
    resolved_basis_points: int
    unresolved_overlap_basis_points: int
    no_verified_visible_contributor_basis_points: int
    contributing_components: tuple[str, ...]
    unresolved_overlap_groups: tuple[FastViewUnresolvedOverlapGroup, ...]
    source_composite_rgba_sha256: str
    source_overlap_mask_sha256: str
    exhaustive_partition_verified: bool = True
    cross_component_z_order_recovered: bool = False
    background_binding_recovered: bool = False
    complete_fastview_frame: bool = False

    def __post_init__(self) -> None:
        if self.size != (800, 600):
            raise FastViewFrameCoverageError("FastView coverage must remain 800x600")
        expected_total = self.size[0] * self.size[1]
        if self.total_pixel_count != expected_total:
            raise FastViewFrameCoverageError("FastView coverage total pixel count mismatch")
        counts = (
            self.resolved_pixel_count,
            self.unresolved_overlap_pixel_count,
            self.no_verified_visible_contributor_pixel_count,
        )
        if any(type(value) is not int or value < 0 for value in counts):
            raise FastViewFrameCoverageError("FastView coverage counts must be non-negative")
        if sum(counts) != self.total_pixel_count:
            raise FastViewFrameCoverageError(
                "FastView coverage classes must partition the full surface"
            )
        basis_points = (
            self.resolved_basis_points,
            self.unresolved_overlap_basis_points,
            self.no_verified_visible_contributor_basis_points,
        )
        if any(type(value) is not int or not 0 <= value <= 10000 for value in basis_points):
            raise FastViewFrameCoverageError(
                "FastView coverage basis points must be integers in 0..10000"
            )
        if not self.exhaustive_partition_verified:
            raise FastViewFrameCoverageError(
                "FastView coverage cannot weaken exhaustive partition verification"
            )
        if len(set(self.contributing_components)) != len(self.contributing_components):
            raise FastViewFrameCoverageError(
                "FastView coverage component identities must be unique"
            )
        if (
            type(self.unresolved_overlap_groups) is not tuple
            or any(
                type(group) is not FastViewUnresolvedOverlapGroup
                for group in self.unresolved_overlap_groups
            )
        ):
            raise FastViewFrameCoverageError(
                "FastView coverage must preserve exact overlap groups"
            )
        if (
            sum(group.pixel_count for group in self.unresolved_overlap_groups)
            != self.unresolved_overlap_pixel_count
        ):
            raise FastViewFrameCoverageError(
                "FastView coverage overlap groups must cover every overlap pixel"
            )
        for digest in (
            self.source_composite_rgba_sha256,
            self.source_overlap_mask_sha256,
        ):
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(char not in "0123456789abcdef" for char in digest)
            ):
                raise FastViewFrameCoverageError(
                    "FastView coverage source hashes must be lowercase SHA-256"
                )
        if (
            self.cross_component_z_order_recovered
            or self.background_binding_recovered
            or self.complete_fastview_frame
        ):
            raise FastViewFrameCoverageError(
                "coverage audit cannot promote unresolved FastView fidelity"
            )


def _basis_points(count: int, total: int) -> int:
    # Integer floor is deliberate and deterministic. Counts remain authoritative.
    return (int(count) * 10000) // int(total)


def audit_fastview_frame_coverage(
    composite: FastViewResolvedOnlyComposite,
) -> FastViewFrameCoverage:
    """Build an exhaustive accounting from one exact resolved-only composite."""
    if type(composite) is not FastViewResolvedOnlyComposite:
        raise FastViewFrameCoverageError(
            "coverage audit requires exact FastViewResolvedOnlyComposite"
        )

    width, height = composite.size
    total = width * height
    resolved = int(composite.resolved_pixel_count)
    overlap = int(composite.unresolved_overlap_pixel_count)
    no_contributor = total - resolved - overlap
    if no_contributor < 0:
        raise FastViewFrameCoverageError(
            "resolved composite counts exceed the FastView surface"
        )

    return FastViewFrameCoverage(
        size=composite.size,
        total_pixel_count=total,
        resolved_pixel_count=resolved,
        unresolved_overlap_pixel_count=overlap,
        no_verified_visible_contributor_pixel_count=no_contributor,
        resolved_basis_points=_basis_points(resolved, total),
        unresolved_overlap_basis_points=_basis_points(overlap, total),
        no_verified_visible_contributor_basis_points=_basis_points(
            no_contributor, total
        ),
        contributing_components=composite.contributing_components,
        unresolved_overlap_groups=composite.unresolved_overlap_groups,
        source_composite_rgba_sha256=composite.rgba_sha256,
        source_overlap_mask_sha256=composite.unresolved_overlap_mask_sha256,
    )
