"""Source-closed PPreMatch control composition modes.

The canonical FM2001 executable paints PPreMatch children in native order
0..181 through generic panel traversal 0x6533A0. PictureControl virtual slot
+0x64 is 0x64F6D0; it delegates to style draw 0x64E5D0 and common DirectDraw
wrapper 0x6556C0.

PPreMatch constructs 93 PictureControls. The constructor stream binds 72 to
style wrapper 0x87BF00, whose static initializer 0x603510 sets DDBLT_KEYSRC
(0x8000), and 21 to wrapper 0x87BF10, whose 0x6034E0 initializer carries no
source-key flag. Both use the source wrapper alpha endpoint 0x100, so
0x6556C0 takes the native DirectDraw blit path rather than its software alpha
blend path. The wrapper adds DDBLT_WAIT (0x01000000).

The four selector controls are Button@ease instances. Their shared atlas wrapper
0x946350 is initialized at 0x5F4A10 with alpha 0x100 and no source-key flag.
The button then draws its centered Zurich caption over that opaque frame. Caption
style/color behavior is the already recovered generic Button@ease contract:
style 0x2000, normal/group-2 color 0xFFFF, alternate group-1 color 0x0000.

TextControl glyphs are not flattened here. Their source path reaches packed-16
font blit 0x658BC0, which requires the runtime native RGB masks captured from
the DirectDraw surface. Those masks are deliberately not guessed as RGB555 or
RGB565.
"""
from __future__ import annotations

from original_button_frames import button_group_subframe_for_source_index

PREMATCH_PANEL_TRAVERSAL_VA = 0x6533A0
PREMATCH_CONTROL_DRAW_VTABLE_OFFSET = 0x64
PREMATCH_PICTURE_DRAW_VA = 0x64F6D0
PREMATCH_PICTURE_STYLE_DRAW_VA = 0x64E5D0
PREMATCH_DIRECTDRAW_BLT_WRAPPER_VA = 0x6556C0

PREMATCH_PICTURE_KEYED_STYLE_WRAPPER_VA = 0x87BF00
PREMATCH_PICTURE_OPAQUE_STYLE_WRAPPER_VA = 0x87BF10
PREMATCH_PICTURE_KEYED_STYLE_INIT_VA = 0x603510
PREMATCH_PICTURE_OPAQUE_STYLE_INIT_VA = 0x6034E0
PREMATCH_DDBLT_KEYSRC = 0x00008000
PREMATCH_DDBLT_WAIT = 0x01000000
PREMATCH_DIRECT_BLT_ALPHA_ENDPOINT = 0x100

PREMATCH_SELECTOR_ATLAS_WRAPPER_VA = 0x946350
PREMATCH_SELECTOR_ATLAS_INIT_VA = 0x5F4A10
PREMATCH_SELECTOR_CHILD_INDICES = (178, 179, 180, 181)
PREMATCH_SELECTOR_CAPTION_STYLE = 0x2000
PREMATCH_SELECTOR_CAPTION_NORMAL_COLOR_16 = 0xFFFF
PREMATCH_SELECTOR_CAPTION_ALTERNATE_COLOR_16 = 0x0000

# Exact constructor-order mapping recovered from 0x4967F0..0x499818.
PREMATCH_KEYED_PICTURE_CHILD_INDICES = (
    *range(10, 32),
    32, 35, 38, 41, 44, 47, 50, 53, 56, 59, 62,
    65, 68, 69, 72, 73, 76, 77, 80, 81, 84, 85, 88, 89, 92,
    93, 96, 99, 102, 105, 108, 111, 114, 117, 120, 123,
    126, 129, 130, 133, 134, 137, 138, 141, 142, 145, 146,
    149, 150, 153,
)
PREMATCH_OPAQUE_PICTURE_CHILD_INDICES = (
    0, 1, 2, 5, 6,
    *range(154, 170),
)
PREMATCH_PICTURE_CHILD_INDICES = tuple(
    sorted(PREMATCH_KEYED_PICTURE_CHILD_INDICES + PREMATCH_OPAQUE_PICTURE_CHILD_INDICES)
)
PREMATCH_TEXT_CHILD_INDICES = tuple(
    index
    for index in range(182)
    if index not in set(PREMATCH_PICTURE_CHILD_INDICES)
    and index not in set(PREMATCH_SELECTOR_CHILD_INDICES)
)


def prematch_picture_write_mode(child_index: int) -> str:
    """Return the source-proven native write mode for one PictureControl."""
    if child_index in PREMATCH_KEYED_PICTURE_CHILD_INDICES:
        return "source_color_key"
    if child_index in PREMATCH_OPAQUE_PICTURE_CHILD_INDICES:
        return "opaque"
    raise ValueError("child is not a source-proven PPreMatch PictureControl")


def prematch_selector_caption_color16(source_frame_index: int) -> int:
    """Return Button@ease caption endpoint color for an exact atlas frame."""
    group, _subframe = button_group_subframe_for_source_index(source_frame_index)
    return (
        PREMATCH_SELECTOR_CAPTION_ALTERNATE_COLOR_16
        if group == 1
        else PREMATCH_SELECTOR_CAPTION_NORMAL_COLOR_16
    )


def prematch_composition_source_contract() -> dict:
    return {
        "panel_traversal_va": PREMATCH_PANEL_TRAVERSAL_VA,
        "child_draw_vtable_offset": PREMATCH_CONTROL_DRAW_VTABLE_OFFSET,
        "picture_draw_va": PREMATCH_PICTURE_DRAW_VA,
        "picture_style_draw_va": PREMATCH_PICTURE_STYLE_DRAW_VA,
        "directdraw_blt_wrapper_va": PREMATCH_DIRECTDRAW_BLT_WRAPPER_VA,
        "picture_alpha_endpoint": PREMATCH_DIRECT_BLT_ALPHA_ENDPOINT,
        "keyed_style_wrapper_va": PREMATCH_PICTURE_KEYED_STYLE_WRAPPER_VA,
        "opaque_style_wrapper_va": PREMATCH_PICTURE_OPAQUE_STYLE_WRAPPER_VA,
        "keyed_style_flags": PREMATCH_DDBLT_WAIT | PREMATCH_DDBLT_KEYSRC,
        "opaque_style_flags": PREMATCH_DDBLT_WAIT,
        "keyed_picture_child_indices": PREMATCH_KEYED_PICTURE_CHILD_INDICES,
        "opaque_picture_child_indices": PREMATCH_OPAQUE_PICTURE_CHILD_INDICES,
        "selector_child_indices": PREMATCH_SELECTOR_CHILD_INDICES,
        "selector_atlas_wrapper_va": PREMATCH_SELECTOR_ATLAS_WRAPPER_VA,
        "selector_atlas_init_va": PREMATCH_SELECTOR_ATLAS_INIT_VA,
        "selector_frame_write_mode": "opaque",
        "selector_caption_style": PREMATCH_SELECTOR_CAPTION_STYLE,
        "selector_caption_normal_color_16": PREMATCH_SELECTOR_CAPTION_NORMAL_COLOR_16,
        "selector_caption_alternate_color_16": PREMATCH_SELECTOR_CAPTION_ALTERNATE_COLOR_16,
        "text_requires_runtime_native_masks": True,
        "fixed_rgb555_or_rgb565_claim": False,
        "flattened_frame_available": False,
        "gate14_complete": False,
    }
