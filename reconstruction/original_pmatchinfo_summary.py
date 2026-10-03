"""Ordinary PL popup summary, from complete native report fields only.

4885A0 / 60BEB0 supply text; 485091/C9/5101 set flag 24 and color FFFF.
64F090's font callback centers each half independently and preserves native
18px line height inside 16px controls. This does not place nested script rows.
"""
from dataclasses import dataclass

from complete_fixture_report import CompleteFixtureReport
from original_pmatchinfo_resources import PMATCHINFO_TEXT_PLACEMENTS, pmatchinfo_original_english
from original_management_canvas import _clip_text_mask, _endpoint_text_rgba
from gate13_original_pixel_preview import encode_rgba_png
from original_pmatchinfo_resources import PMATCHINFO_DEFAULT_TAB_EVENT_ID


@dataclass(frozen=True)
class PMatchInfoSummaryLine:
    setup_call_va: int
    rect: tuple[int, int, int, int]
    text: str


def _source_name(player, field):
    value = getattr(player, field, None)
    if type(value) is not str:
        return None
    try:
        encoded = value.encode('cp1252')
    except UnicodeError:
        return None
    return encoded if encoded and all(c >= 32 for c in encoded) else None


def ordinary_pmatchinfo_summary_lines(report, players):
    if type(report) is not CompleteFixtureReport or report.metadata.previous_scores is not None:
        return ()  # Partial reports and aggregate/secondary contexts are not ordinary PL.
    fields = {s.report_offset: int.from_bytes(s.value, 'little')
              for s in report.metadata.scalar_copies}
    texts = [(0x485091, pmatchinfo_original_english(0x982C40) + ' ' + format(fields[0x30], ',d'))]
    first = _source_name(players.get(fields[0x98]), 'first_name')
    surname = _source_name(players.get(fields[0x9A]), 'surname')
    if first is not None and surname is not None:
        # 60BEB0 formats the FIRST BYTE from one identity plus the other surname.
        ref = (first[:1] + b' ' + surname).decode('cp1252')
        texts.append((0x4850C9, pmatchinfo_original_english(0x98200C) + ' ' + ref))
    if report.selected_player_id != -1:
        selected = players.get(report.selected_player_id)
        first, surname = _source_name(selected, 'first_name'), _source_name(selected, 'surname')
        if first is not None and surname is not None:
            text = pmatchinfo_original_english(0x981EA4) % (
                pmatchinfo_original_english(0x9826B8), first.decode('cp1252'), surname.decode('cp1252'))
            texts.append((0x485101, text))
    slots = {s.setup_call_va: s.rect for s in PMATCHINFO_TEXT_PLACEMENTS}
    return tuple(PMatchInfoSummaryLine(call, slots[call], text) for call, text in texts)


def summary_line_pixels(line, font):
    x, y, width, height = line.rect
    mask = font.render_text_alpha(line.text)
    # 64F21C..22C / 64F269..279: floor(control/2) - floor(font/2),
    # NOT floor((control-font)/2); y=49 for the 50px,16px-high first line.
    origin = (x + width // 2 - font.measure_text(line.text) // 2,
              y + height // 2 - font.native_line_height() // 2)
    clipped = _clip_text_mask(mask, line_origin=origin,
                             clip_rect=(x, y, x + width, y + height))
    if clipped is None:
        return None
    px, py, w, h, alpha = clipped
    return px, py, w, h, encode_rgba_png(w, h, _endpoint_text_rgba(alpha, 0xFFFF))


def ordinary_pmatchinfo_pitch_pixels(report, snapshot):
    """Project the default subpanel's proven pitch control, not row owners.

    485471 -> 650B20 -> 653320 gives child (0,145,800,500).
    650BB0 translates the incoming clip to child coordinates; 6533A0
    intersects it with each child control. Local y=-2 loses two source
    rows; it is not moved down or stretched.
    """
    if (type(report) is not CompleteFixtureReport
            or report.metadata.previous_scores is not None
            or snapshot.selected_tab_event_id != PMATCHINFO_DEFAULT_TAB_EVENT_ID):
        return None
    matches = [item for item in snapshot.art if item.resource_name == 'pitch_normal']
    if len(matches) != 1:
        return None
    pitch = matches[0]
    if pitch.rect != (233, -2, 294, 78):
        return None
    rgba = pitch.rgba[2 * 294 * 4:]
    return 233, 145, 294, 76, encode_rgba_png(294, 76, rgba)
