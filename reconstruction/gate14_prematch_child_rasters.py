"""Native-order child raster ledger for one supplied PPreMatch state.

This layer assigns visible/hidden state, exact control rectangles and original
pixel payloads to all 182 PPreMatch children. It intentionally stops before
flattening the children because the legacy Picture/Text/Button cross-control
blend rule is a separate source contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from gate14_prematch_supplied_state import BoundPrematchSuppliedState
from gate14_prematch_compositor_source import (
    PREMATCH_SELECTOR_CAPTION_STYLE,
    prematch_selector_caption_color16,
)
from gate14_prematch_text_raster import PrematchTextRasterSet
from original_front_end_layout import OriginalRect
from original_prematch_panel import PREMATCH_CHILD_COUNT, PREMATCH_CHILD_ORDER_RANGES


class PrematchChildRasterError(ValueError):
    pass


@dataclass(frozen=True)
class PrematchChildRaster:
    child_index: int
    role: str
    visible: bool
    rect: OriginalRect | None
    rgba: bytes | None
    rgba_sha256: str | None
    source_identity: str | None
    caption_text: str | None = None
    caption_alpha: bytes | None = None
    caption_alpha_sha256: str | None = None
    caption_size: tuple[int, int] | None = None
    caption_origin: tuple[int, int] | None = None
    caption_native_color_16: int | None = None
    caption_native_style: int | None = None

    def __post_init__(self) -> None:
        if type(self.child_index) is not int or not 0 <= self.child_index < PREMATCH_CHILD_COUNT:
            raise PrematchChildRasterError("child index must remain native 0..181")
        if not self.role:
            raise PrematchChildRasterError("child raster role must be non-empty")
        if self.visible:
            if self.rect is None or self.rgba is None:
                raise PrematchChildRasterError("visible child requires geometry and pixels")
            if len(self.rgba) != self.rect.width * self.rect.height * 4:
                raise PrematchChildRasterError("visible child RGBA geometry mismatch")
            digest = sha256(self.rgba).hexdigest()
            if self.rgba_sha256 != digest:
                raise PrematchChildRasterError("visible child RGBA checksum mismatch")
            if not self.source_identity:
                raise PrematchChildRasterError("visible child requires source identity")
            caption_fields = (
                self.caption_text,
                self.caption_alpha,
                self.caption_alpha_sha256,
                self.caption_size,
                self.caption_origin,
                self.caption_native_color_16,
                self.caption_native_style,
            )
            if any(value is not None for value in caption_fields):
                if any(value is None for value in caption_fields):
                    raise PrematchChildRasterError(
                        "selector caption metadata must be complete or absent"
                    )
                width, height = self.caption_size
                if width <= 0 or height <= 0 or len(self.caption_alpha) != width * height:
                    raise PrematchChildRasterError("selector caption alpha geometry mismatch")
                if sha256(self.caption_alpha).hexdigest() != self.caption_alpha_sha256:
                    raise PrematchChildRasterError("selector caption alpha checksum mismatch")
                origin_x, origin_y = self.caption_origin
                if (
                    origin_x < self.rect.x
                    or origin_y < self.rect.y
                    or origin_x + width > self.rect.right
                    or origin_y + height > self.rect.bottom
                ):
                    raise PrematchChildRasterError("selector caption exceeds native control rect")
                if self.caption_native_color_16 not in (0x0000, 0xFFFF):
                    raise PrematchChildRasterError("selector caption endpoint color drifted")
                if self.caption_native_style != PREMATCH_SELECTOR_CAPTION_STYLE:
                    raise PrematchChildRasterError("selector caption style drifted")
        elif any(
            value is not None
            for value in (
                self.rect,
                self.rgba,
                self.rgba_sha256,
                self.source_identity,
                self.caption_text,
                self.caption_alpha,
                self.caption_alpha_sha256,
                self.caption_size,
                self.caption_origin,
                self.caption_native_color_16,
                self.caption_native_style,
            )
        ):
            raise PrematchChildRasterError("hidden child cannot publish pixels or geometry")


@dataclass(frozen=True)
class PrematchChildRasterLedger:
    children: tuple[PrematchChildRaster, ...]
    source_child_count: int = PREMATCH_CHILD_COUNT
    native_order_preserved: bool = True
    all_child_visibility_bound: bool = True
    all_visible_child_pixels_bound: bool = True
    cross_control_blend_recovered: bool = False
    flattened_frame_available: bool = False
    complete_prematch_frame: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        if len(self.children) != PREMATCH_CHILD_COUNT:
            raise PrematchChildRasterError("ledger must contain all 182 native children")
        if tuple(child.child_index for child in self.children) != tuple(range(PREMATCH_CHILD_COUNT)):
            raise PrematchChildRasterError("ledger order must remain exact native 0..181")
        if self.source_child_count != PREMATCH_CHILD_COUNT:
            raise PrematchChildRasterError("ledger source child count drifted")
        if not (
            self.native_order_preserved
            and self.all_child_visibility_bound
            and self.all_visible_child_pixels_bound
        ):
            raise PrematchChildRasterError("child ledger cannot weaken supplied source state")
        if (
            self.cross_control_blend_recovered
            or self.flattened_frame_available
            or self.complete_prematch_frame
            or self.gate14_complete
        ):
            raise PrematchChildRasterError(
                "child raster ledger cannot promote unresolved blend/frame/gate claims"
            )


def _visible(
    index,
    role,
    rect,
    rgba,
    source_identity,
    *,
    caption_text=None,
    caption_alpha=None,
    caption_size=None,
    caption_origin=None,
    caption_native_color_16=None,
    caption_native_style=None,
):
    payload = bytes(rgba)
    return PrematchChildRaster(
        child_index=index,
        role=role,
        visible=True,
        rect=rect,
        rgba=payload,
        rgba_sha256=sha256(payload).hexdigest(),
        source_identity=source_identity,
        caption_text=caption_text,
        caption_alpha=(bytes(caption_alpha) if caption_alpha is not None else None),
        caption_alpha_sha256=(
            sha256(bytes(caption_alpha)).hexdigest()
            if caption_alpha is not None
            else None
        ),
        caption_size=caption_size,
        caption_origin=caption_origin,
        caption_native_color_16=caption_native_color_16,
        caption_native_style=caption_native_style,
    )


def _hidden(index, role):
    return PrematchChildRaster(
        child_index=index,
        role=role,
        visible=False,
        rect=None,
        rgba=None,
        rgba_sha256=None,
        source_identity=None,
    )


def _crop_left(rgba: bytes, source_width: int, source_height: int, width: int) -> bytes:
    if not 0 <= width <= source_width:
        raise PrematchChildRasterError("crop width is outside source bounds")
    if len(rgba) != source_width * source_height * 4:
        raise PrematchChildRasterError("crop source geometry mismatch")
    rows = []
    stride = source_width * 4
    take = width * 4
    for y in range(source_height):
        start = y * stride
        rows.append(rgba[start:start + take])
    return b"".join(rows)


def _static_layer(boundary, role):
    for layer in boundary.static_layers:
        if layer.role == role:
            return layer
    raise PrematchChildRasterError(f"missing source static layer: {role}")


def build_prematch_child_raster_ledger(
    supplied: BoundPrematchSuppliedState,
    *,
    text_rasters: PrematchTextRasterSet,
) -> PrematchChildRasterLedger:
    if type(supplied) is not BoundPrematchSuppliedState:
        raise PrematchChildRasterError(
            "child raster ledger requires exact BoundPrematchSuppliedState"
        )
    if type(text_rasters) is not PrematchTextRasterSet:
        raise PrematchChildRasterError(
            "child raster ledger requires exact PrematchTextRasterSet"
        )

    boundary = supplied.boundary
    if supplied.dynamic_text.selection != boundary.selection:
        raise PrematchChildRasterError("supplied text state differs from boundary selection")

    text_by_index = {child.child_index: child for child in text_rasters.children}
    hidden_text = set(text_rasters.hidden_text_child_indices)

    children: list[PrematchChildRaster | None] = [None] * PREMATCH_CHILD_COUNT

    # 0..9: background, fixed art, dynamic text and team badges.
    children[0] = _visible(
        0, "live_background", boundary.background.rect, boundary.background.rgba,
        boundary.background.source_path,
    )
    pitch = _static_layer(boundary, "pitch")
    top_bar = _static_layer(boundary, "top_bar")
    children[1] = _visible(1, "pitch", pitch.rect, pitch.rgba, pitch.source_path)
    children[2] = _visible(2, "top_bar", top_bar.rect, top_bar.rgba, top_bar.source_path)

    for index in (3, 4):
        text = text_by_index[index]
        children[index] = _visible(
            index, text.role, text.rect, text.rgba,
            f"text:{text.style_wrapper_va:#x}:{text.text}",
        )
    for index, badge in zip((5, 6), boundary.team_badges, strict=True):
        children[index] = _visible(index, badge.role, badge.rect, badge.rgba, badge.source_path)
    for index in (7, 8, 9):
        text = text_by_index[index]
        children[index] = _visible(
            index, text.role, text.rect, text.rgba,
            f"text:{text.style_wrapper_va:#x}:{text.text}",
        )

    # 10..31: supplied XI marker controls.
    for marker in supplied.starting_xi_markers.markers:
        if marker.visible:
            children[marker.child_index] = _visible(
                marker.child_index,
                f"starting_xi_{marker.side}_{marker.slot_index}",
                marker.rect,
                marker.rgba,
                marker.source_path,
            )
        else:
            children[marker.child_index] = _hidden(
                marker.child_index,
                f"starting_xi_{marker.side}_{marker.slot_index}",
            )

    # 32..153: row strip/text/disabled controls.
    for row in supplied.player_rows.rows:
        source = row.source
        strip = row.strip
        if row.variant == "active":
            children[source.strip_child_index] = _visible(
                source.strip_child_index,
                f"{source.side}_player_{source.slot_index}_active_strip",
                strip.rect,
                strip.active_rgba,
                strip.active_source_path,
            )
            for index in (source.number_child_index, source.name_child_index):
                text = text_by_index[index]
                children[index] = _visible(
                    index, text.role, text.rect, text.rgba,
                    f"text:{text.style_wrapper_va:#x}:{text.text}",
                )
            if source.disabled_child_index is not None:
                children[source.disabled_child_index] = _hidden(
                    source.disabled_child_index,
                    f"{source.side}_player_{source.slot_index}_disabled_strip",
                )
        elif row.variant == "disabled":
            children[source.strip_child_index] = _hidden(
                source.strip_child_index,
                f"{source.side}_player_{source.slot_index}_active_strip",
            )
            for index in (source.number_child_index, source.name_child_index):
                if index not in hidden_text:
                    raise PrematchChildRasterError(
                        "disabled player row text is not hidden in text raster state"
                    )
                children[index] = _hidden(index, f"{source.side}_player_{source.slot_index}_text")
            if source.disabled_child_index is None:
                raise PrematchChildRasterError("disabled row lacks native disabled child")
            children[source.disabled_child_index] = _visible(
                source.disabled_child_index,
                f"{source.side}_player_{source.slot_index}_disabled_strip",
                strip.rect,
                strip.disabled_rgba,
                strip.disabled_source_path,
            )
        else:
            children[source.strip_child_index] = _hidden(
                source.strip_child_index,
                f"{source.side}_player_{source.slot_index}_active_strip",
            )
            for index in (source.number_child_index, source.name_child_index):
                if index not in hidden_text:
                    raise PrematchChildRasterError(
                        "hidden starter text is not hidden in text raster state"
                    )
                children[index] = _hidden(index, f"{source.side}_player_{source.slot_index}_text")
            if source.disabled_child_index is not None:
                children[source.disabled_child_index] = _hidden(
                    source.disabled_child_index,
                    f"{source.side}_player_{source.slot_index}_disabled_strip",
                )

    # 154..169: four rows x left base/right base/left overlay/right shrinking mask.
    for row_index, bound in enumerate(supplied.rating_rows.rows):
        source = bound.source
        left_base_i = 154 + row_index
        right_base_i = 158 + row_index
        left_overlay_i = 162 + row_index
        right_mask_i = 166 + row_index
        children[left_base_i] = _visible(
            left_base_i,
            f"rating_{bound.semantic_group}_left_base",
            source.left_rect,
            source.left_base_rgba,
            "rating_bar_right.444",
        )
        children[right_base_i] = _visible(
            right_base_i,
            f"rating_{bound.semantic_group}_right_base",
            source.right_rect,
            source.right_base_rgba,
            "rating_bar_right2.444",
        )

        if bound.left_width:
            left_rgba = _crop_left(
                source.left_dynamic_rgba,
                source.left_rect.width,
                source.left_rect.height,
                bound.left_width,
            )
            children[left_overlay_i] = _visible(
                left_overlay_i,
                f"rating_{bound.semantic_group}_left_overlay",
                bound.left_dynamic_rect,
                left_rgba,
                "rating_bar_left.444",
            )
        else:
            children[left_overlay_i] = _hidden(
                left_overlay_i,
                f"rating_{bound.semantic_group}_left_overlay",
            )

        mask_width = bound.right_mask_rect.width
        if mask_width:
            mask_rgba = _crop_left(
                source.right_dynamic_mask_rgba,
                source.right_rect.width,
                source.right_rect.height,
                mask_width,
            )
            children[right_mask_i] = _visible(
                right_mask_i,
                f"rating_{bound.semantic_group}_right_mask",
                bound.right_mask_rect,
                mask_rgba,
                "rating_bar_right.444",
            )
        else:
            children[right_mask_i] = _hidden(
                right_mask_i,
                f"rating_{bound.semantic_group}_right_mask",
            )

    # 170..177: rating captions.
    for index in range(170, 178):
        text = text_by_index[index]
        children[index] = _visible(
            index, text.role, text.rect, text.rgba,
            f"text:{text.style_wrapper_va:#x}:{text.text}",
        )

    # 178..181: native child order is modes 3,2,1,0.
    selector_by_mode = {item.source.mode: item for item in supplied.selector_frames.selectors}
    for child_index, mode in zip(range(178, 182), (3, 2, 1, 0), strict=True):
        item = selector_by_mode[mode]
        frame = item.frame
        rgba = getattr(frame, "rgba", None)
        width = getattr(frame, "width", None)
        height = getattr(frame, "height", None)
        if rgba is None or (width, height) != (item.source.rect.width, item.source.rect.height):
            raise PrematchChildRasterError(
                "selector frame pixels do not match native PPreMatch control"
            )
        font = boundary.font
        label = item.source.label
        mask = font.render_text_alpha(label)
        measured_width = font.measure_text(label)
        line_height = font.native_line_height()
        if mask.width != measured_width:
            raise PrematchChildRasterError(
                "selector Zurich glyph mask differs from native text measure"
            )
        origin = (
            item.source.rect.x + (item.source.rect.width - measured_width) // 2,
            item.source.rect.y + (item.source.rect.height - line_height) // 2,
        )
        children[child_index] = _visible(
            child_index,
            f"match_detail_selector_mode_{mode}",
            item.source.rect,
            rgba,
            f"selector_frame:{item.source_frame_index}:caption:{label}",
            caption_text=label,
            caption_alpha=mask.alpha,
            caption_size=(mask.width, mask.height),
            caption_origin=origin,
            caption_native_color_16=prematch_selector_caption_color16(
                item.source_frame_index
            ),
            caption_native_style=PREMATCH_SELECTOR_CAPTION_STYLE,
        )

    if any(child is None for child in children):
        missing = tuple(i for i, child in enumerate(children) if child is None)
        raise PrematchChildRasterError(f"native child raster ledger has gaps: {missing}")

    ledger = PrematchChildRasterLedger(children=tuple(children))
    flattened_ranges = tuple(
        index
        for _role, start, end in PREMATCH_CHILD_ORDER_RANGES
        for index in range(start, end + 1)
    )
    if flattened_ranges != tuple(range(PREMATCH_CHILD_COUNT)):
        raise PrematchChildRasterError("source child family partition drifted")
    return ledger


def prematch_child_raster_contract() -> dict:
    return {
        "source_child_count": PREMATCH_CHILD_COUNT,
        "native_order": tuple(range(PREMATCH_CHILD_COUNT)),
        "all_child_visibility_binding_available": True,
        "all_visible_child_pixel_binding_available": True,
        "rating_right_layer_semantics": "full_right2_base_plus_shrinking_right_mask",
        "selector_child_modes": (3, 2, 1, 0),
        "selector_caption_planes_bound": True,
        "selector_caption_style": PREMATCH_SELECTOR_CAPTION_STYLE,
        "cross_control_blend_recovered": False,
        "flattened_frame_available": False,
        "complete_prematch_frame": False,
        "gate14_complete": False,
    }
