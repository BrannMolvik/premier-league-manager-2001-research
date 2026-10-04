"""Fail-closed readiness audit for unresolved FastView overlap pixels.

The resolved-only compositor deliberately masks every pixel with two or more
source-backed component contributors. Some overlap groups now have a narrower
reason for remaining masked than others: native draw order is source-closed for
PossessionDiagram -> PossessionFigures text, while the anti-aliased native font
blend rule is still unresolved.

This module classifies that distinction without changing a single composite
pixel. Known pairwise order is imported only from gate14_fastview_draw_order;
unknown relations stay unknown, cross-component blend remains unresolved, and
no overlap group is promoted to raster-resolvable.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from gate14_fastview_draw_order import (
    FastViewDrawOrderError,
    source_closed_pairwise_order,
)
from gate14_fastview_resolved_composite import (
    FastViewResolvedOnlyComposite,
    FastViewUnresolvedOverlapGroup,
)


class FastViewOverlapReadinessError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewRecoveredPairwiseOrder:
    earlier_component: str
    later_component: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.earlier_component, str)
            or not self.earlier_component
            or not isinstance(self.later_component, str)
            or not self.later_component
            or self.earlier_component == self.later_component
        ):
            raise FastViewOverlapReadinessError(
                "recovered pairwise order requires distinct component names"
            )


@dataclass(frozen=True)
class FastViewOverlapGroupReadiness:
    components: tuple[str, ...]
    pixel_count: int
    bounding_rect: tuple[int, int, int, int]
    recovered_pairwise_order: tuple[FastViewRecoveredPairwiseOrder, ...]
    required_pairwise_relation_count: int
    recovered_pairwise_relation_count: int
    complete_draw_order_recovered: bool
    cross_component_blend_rule_recovered: bool
    pixels_resolvable: bool
    blockers: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            type(self.components) is not tuple
            or len(self.components) < 2
            or any(not isinstance(name, str) or not name for name in self.components)
            or len(set(self.components)) != len(self.components)
        ):
            raise FastViewOverlapReadinessError(
                "overlap readiness requires at least two unique components"
            )
        if type(self.pixel_count) is not int or self.pixel_count <= 0:
            raise FastViewOverlapReadinessError(
                "overlap readiness pixel_count must be positive"
            )
        if (
            type(self.bounding_rect) is not tuple
            or len(self.bounding_rect) != 4
            or any(type(value) is not int for value in self.bounding_rect)
        ):
            raise FastViewOverlapReadinessError(
                "overlap readiness bounding_rect must contain four integers"
            )
        if type(self.recovered_pairwise_order) is not tuple or any(
            type(item) is not FastViewRecoveredPairwiseOrder
            for item in self.recovered_pairwise_order
        ):
            raise FastViewOverlapReadinessError(
                "recovered pairwise relations must use exact records"
            )

        expected_required = len(self.components) * (len(self.components) - 1) // 2
        if self.required_pairwise_relation_count != expected_required:
            raise FastViewOverlapReadinessError(
                "required pairwise relation count does not match component count"
            )
        if self.recovered_pairwise_relation_count != len(
            self.recovered_pairwise_order
        ):
            raise FastViewOverlapReadinessError(
                "recovered pairwise relation count does not match records"
            )
        if not (
            0
            <= self.recovered_pairwise_relation_count
            <= self.required_pairwise_relation_count
        ):
            raise FastViewOverlapReadinessError(
                "recovered pairwise relation count is invalid"
            )
        if self.complete_draw_order_recovered != (
            self.recovered_pairwise_relation_count
            == self.required_pairwise_relation_count
        ):
            raise FastViewOverlapReadinessError(
                "complete draw-order flag does not match pairwise evidence"
            )
        if self.cross_component_blend_rule_recovered or self.pixels_resolvable:
            raise FastViewOverlapReadinessError(
                "overlap readiness cannot promote unresolved blend/pixels"
            )

        expected_blockers = (
            ("cross_component_blend_rule",)
            if self.complete_draw_order_recovered
            else ("cross_component_draw_order", "cross_component_blend_rule")
        )
        if self.blockers != expected_blockers:
            raise FastViewOverlapReadinessError(
                "overlap readiness blockers do not match recovered evidence"
            )

        known_components = set(self.components)
        seen_pairs: set[frozenset[str]] = set()
        for relation in self.recovered_pairwise_order:
            if (
                relation.earlier_component not in known_components
                or relation.later_component not in known_components
            ):
                raise FastViewOverlapReadinessError(
                    "recovered pairwise relation references another overlap group"
                )
            key = frozenset(
                (relation.earlier_component, relation.later_component)
            )
            if key in seen_pairs:
                raise FastViewOverlapReadinessError(
                    "recovered pairwise relation is duplicated"
                )
            seen_pairs.add(key)


@dataclass(frozen=True)
class FastViewOverlapReadinessAudit:
    source_composite_rgba_sha256: str
    source_overlap_mask_sha256: str
    unresolved_overlap_pixel_count: int
    draw_order_resolved_overlap_pixel_count: int
    draw_order_unresolved_overlap_pixel_count: int
    blend_unresolved_overlap_pixel_count: int
    raster_resolvable_overlap_pixel_count: int
    groups: tuple[FastViewOverlapGroupReadiness, ...]
    cross_component_blend_rule_recovered: bool = False
    all_overlap_pixels_resolvable: bool = False
    complete_fastview_frame: bool = False

    def __post_init__(self) -> None:
        for label, digest in (
            ("source composite", self.source_composite_rgba_sha256),
            ("source overlap mask", self.source_overlap_mask_sha256),
        ):
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(char not in "0123456789abcdef" for char in digest)
            ):
                raise FastViewOverlapReadinessError(
                    f"{label} SHA-256 must be lowercase hexadecimal"
                )

        counts = (
            self.unresolved_overlap_pixel_count,
            self.draw_order_resolved_overlap_pixel_count,
            self.draw_order_unresolved_overlap_pixel_count,
            self.blend_unresolved_overlap_pixel_count,
            self.raster_resolvable_overlap_pixel_count,
        )
        if any(type(value) is not int or value < 0 for value in counts):
            raise FastViewOverlapReadinessError(
                "overlap readiness counts must be non-negative integers"
            )
        if (
            self.draw_order_resolved_overlap_pixel_count
            + self.draw_order_unresolved_overlap_pixel_count
            != self.unresolved_overlap_pixel_count
        ):
            raise FastViewOverlapReadinessError(
                "draw-order readiness counts must partition unresolved pixels"
            )
        if (
            self.blend_unresolved_overlap_pixel_count
            != self.unresolved_overlap_pixel_count
        ):
            raise FastViewOverlapReadinessError(
                "every current cross-component overlap remains blend-unresolved"
            )
        if self.raster_resolvable_overlap_pixel_count != 0:
            raise FastViewOverlapReadinessError(
                "no current unresolved overlap pixels may be promoted"
            )
        if type(self.groups) is not tuple or any(
            type(group) is not FastViewOverlapGroupReadiness
            for group in self.groups
        ):
            raise FastViewOverlapReadinessError(
                "overlap readiness groups must use exact records"
            )
        if (
            sum(group.pixel_count for group in self.groups)
            != self.unresolved_overlap_pixel_count
        ):
            raise FastViewOverlapReadinessError(
                "overlap readiness groups must cover all unresolved pixels"
            )
        if (
            sum(
                group.pixel_count
                for group in self.groups
                if group.complete_draw_order_recovered
            )
            != self.draw_order_resolved_overlap_pixel_count
        ):
            raise FastViewOverlapReadinessError(
                "draw-order-resolved pixel count does not match groups"
            )
        if (
            self.cross_component_blend_rule_recovered
            or self.all_overlap_pixels_resolvable
            or self.complete_fastview_frame
        ):
            raise FastViewOverlapReadinessError(
                "readiness audit cannot promote unresolved FastView fidelity"
            )


def _known_pairwise_relations(
    group: FastViewUnresolvedOverlapGroup,
) -> tuple[FastViewRecoveredPairwiseOrder, ...]:
    if type(group) is not FastViewUnresolvedOverlapGroup:
        raise FastViewOverlapReadinessError(
            "overlap readiness requires exact compositor overlap groups"
        )

    relations = []
    for first, second in combinations(group.components, 2):
        try:
            source = source_closed_pairwise_order(first, second)
        except FastViewDrawOrderError:
            continue
        relations.append(
            FastViewRecoveredPairwiseOrder(
                earlier_component=source.earlier_component,
                later_component=source.later_component,
            )
        )
    return tuple(relations)


def classify_fastview_overlap_group(
    group: FastViewUnresolvedOverlapGroup,
) -> FastViewOverlapGroupReadiness:
    """Classify why one exact unresolved contributor group remains masked."""
    relations = _known_pairwise_relations(group)
    required = len(group.components) * (len(group.components) - 1) // 2
    complete_order = len(relations) == required
    return FastViewOverlapGroupReadiness(
        components=group.components,
        pixel_count=group.pixel_count,
        bounding_rect=group.bounding_rect,
        recovered_pairwise_order=relations,
        required_pairwise_relation_count=required,
        recovered_pairwise_relation_count=len(relations),
        complete_draw_order_recovered=complete_order,
        cross_component_blend_rule_recovered=False,
        pixels_resolvable=False,
        blockers=(
            ("cross_component_blend_rule",)
            if complete_order
            else ("cross_component_draw_order", "cross_component_blend_rule")
        ),
    )


def audit_fastview_overlap_readiness(
    composite: FastViewResolvedOnlyComposite,
) -> FastViewOverlapReadinessAudit:
    """Partition masked pixels by the remaining source-fidelity blocker."""
    if type(composite) is not FastViewResolvedOnlyComposite:
        raise FastViewOverlapReadinessError(
            "overlap readiness requires exact FastViewResolvedOnlyComposite"
        )

    groups = tuple(
        classify_fastview_overlap_group(group)
        for group in composite.unresolved_overlap_groups
    )
    order_resolved = sum(
        group.pixel_count for group in groups if group.complete_draw_order_recovered
    )
    order_unresolved = composite.unresolved_overlap_pixel_count - order_resolved

    return FastViewOverlapReadinessAudit(
        source_composite_rgba_sha256=composite.rgba_sha256,
        source_overlap_mask_sha256=composite.unresolved_overlap_mask_sha256,
        unresolved_overlap_pixel_count=composite.unresolved_overlap_pixel_count,
        draw_order_resolved_overlap_pixel_count=order_resolved,
        draw_order_unresolved_overlap_pixel_count=order_unresolved,
        blend_unresolved_overlap_pixel_count=composite.unresolved_overlap_pixel_count,
        raster_resolvable_overlap_pixel_count=0,
        groups=groups,
    )
