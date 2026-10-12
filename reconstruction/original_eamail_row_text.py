"""Final Inbox eCText color/advance/clip path, not the generic mask seam.

Canonical final vtable 7BFAC8, paint 5D7360/5D75B0, advance 5D7500.
See research/GATE13_ORIGINAL_INBOX_LIST_MILESTONE.md for source limits.
"""
from __future__ import annotations

from original_eamail_native_row_fields import OriginalEAMNativeVisibleRowsSource
from original_eamail_source_contract import ORIGINAL_EAMAIL_TEXT_CHILDREN
from original_eamail_tagged_player_masks import native_player_markup_fragment_masks
from original_management_text import OriginalManagementTextResources


def original_eamail_text_rgba(text, resources, *, width, height, tagged, selected):
    """Qualified T templates only; top-left pen, native word wrap, child clip."""
    if (type(resources) is not OriginalManagementTextResources
            or type(text) is not str or not text
            or type(tagged) is not bool or type(selected) is not bool
            or type(width) is not int or type(height) is not int
            or width <= 0 or height <= 0):
        raise ValueError("Original Inbox text/control/font required")
    raw = text.encode('cp1252', 'strict')
    if any(value < 32 for value in raw):
        raise ValueError("Original Inbox row text contains control bytes")
    if tagged:
        native_player_markup_fragment_masks(text, resources)  # exact template gate
    elif '<' in text or '>' in text:
        raise ValueError("Unqualified Inbox text markup")
    font = resources.league_tables_row_font
    normal = (0, 0, 0) if selected else (255, 255, 255)
    link = (11, 37, 13) if selected else (120, 238, 130)
    color = normal
    output = bytearray(width * height * 4)
    x = y = i = 0
    start_word = False
    while i < len(raw):
        if raw[i] == ord('<'):
            token = next((token for token in (b'<T+P>', b'<T+C>', b'<T->')
                          if raw.startswith(token, i)), None)
            if token is None:
                raise ValueError("Unqualified native Inbox tag")
            color = normal if token == b'<T->' else link
            i += len(token)
            start_word = True
            continue
        value = raw[i]
        glyph = font.glyph_for_byte(value)
        if value == 32:
            start_word = True
        elif start_word:
            # 6574E0 flags0: initial space width, current-record/previous pair.
            word_width = font.glyph_for_byte(32).width
            previous = None
            for byte in raw[i:]:
                if byte in (32, ord('<')):
                    break
                current = font.glyph_for_byte(byte)
                word_width += current.width
                if previous is not None:
                    word_width += current.pair_adjustment(previous)
                previous = byte
            if x + word_width > width:
                x = 0
                y += font.atlas_height * 3 // 2  # native float 1.5, truncation
            start_word = False
        if value != 32:
            alpha = font.glyph_alpha(value)
            for gy in range(glyph.height):
                py = y + glyph.draw_y + gy
                if not 0 <= py < height:
                    continue
                for gx in range(glyph.width):
                    px = x + gx
                    if not 0 <= px < width:
                        continue
                    a = alpha[gy * glyph.width + gx]
                    pos = (py * width + px) * 4
                    if a > output[pos + 3]:
                        output[pos:pos + 4] = bytes((*color, a))
        # Draw FIRST. The next pen includes the CURRENT glyph's pair with
        # previous RAW byte (including the closing '>' of a native tag).
        x += glyph.width
        if i:
            x += glyph.pair_adjustment(raw[i - 1])
        i += 1
    return bytes(output)


def original_eamail_row_text_layers(visible, resources, *, selected_node_serial=None):
    """Source (x,y,width,height,RGBA) layers; unknown legacy names stay absent."""
    if type(visible) is not OriginalEAMNativeVisibleRowsSource:
        raise ValueError("Original delivered Inbox viewport required")
    if len(visible.native_rows) > 8:
        raise ValueError("Original Inbox has eight row owners")
    layers = []
    seen = set()
    for row in visible.native_rows:
        serial = row.original_internal_node_serial
        if serial in seen or len(row.original_text_fields) != 3:
            raise ValueError("Original Inbox row ownership drifted")
        seen.add(serial)
        rx, ry, width, height = row.row_screen_rect
        if (width, height) != (532, 18):
            raise ValueError("Original Inbox row geometry drifted")
        for field, (child_id, rect, _) in zip(row.original_text_fields, ORIGINAL_EAMAIL_TEXT_CHILDREN):
            x, y, w, h = rect
            expected = (rx + x, ry + y, w, h)
            if (field.child_id != child_id or field.source_rect_in_row != rect
                    or field.screen_rect != expected):
                raise ValueError("Original Inbox child placement drifted")
            text = field.source_verified_visible_text
            if text is None:
                continue
            rgba = original_eamail_text_rgba(
                text, resources, width=w, height=h, tagged=child_id == 2,
                selected=serial == selected_node_serial,
            )
            layers.append((*expected, rgba))
    if selected_node_serial is not None and selected_node_serial not in seen:
        raise ValueError("Original Inbox selected row is outside viewport")
    return tuple(layers)
