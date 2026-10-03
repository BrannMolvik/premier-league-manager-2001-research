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
from hashlib import sha256
from ea_font import EAFont
from original_teamselect_native import TEAMSELECT_LEAGUE_FONT_PATH, TEAMSELECT_LEAGUE_FONT_SHA256


@dataclass(frozen=True)
class PMatchInfoSummaryLine:
    setup_call_va: int
    rect: tuple[int, int, int, int]
    text: str
    style: int = 0x24


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
    attendance = fields[0x30]
    # 4887AE..488865: original fallback is literal 55,241 when <=1.
    # This affects only displayed text, never stored report/context production.
    thousands, remainder = divmod(attendance, 1000) if attendance > 1 else (55, 241)
    caption = report.metadata.caption.decode('cp1252')
    texts = [(0x485091, pmatchinfo_original_english(0x982C40) +
              f' {thousands},{remainder:03d}  {caption}  ')]
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
    measured = font.measure_text(line.text)
    dx = width - measured if line.style & 2 else width // 2 - measured // 2 if line.style & 4 else 0
    dy = height - font.native_line_height() if line.style & 0x10 else (
        height // 2 - font.native_line_height() // 2 if line.style & 0x20 else 0)
    origin = (x + dx, y + dy)
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


def load_pmatchinfo_nested_font(source_root):
    # 60367A -> 9197E0; 6042A8/6042F0 loads original BdXCn18, not BdXCn20.
    data = (source_root / TEAMSELECT_LEAGUE_FONT_PATH).read_bytes()
    if sha256(data).hexdigest() != TEAMSELECT_LEAGUE_FONT_SHA256:
        raise ValueError('PMatchInfo nested font differs from original BdXCn18')
    return EAFont.from_bytes(data)


def ordinary_pmatchinfo_possession_lines(report, snapshot):
    if (type(report) is not CompleteFixtureReport
            or report.metadata.previous_scores is not None
            or snapshot.selected_tab_event_id != PMATCHINFO_DEFAULT_TAB_EVENT_ID):
        return ()
    # 483BCA/C22/C7A consume +22/+21/+20 respectively. %N%% at 81CEE0
    # runs 655F40 -> 6559B0; for these unsigned bytes, flags=0 and the
    # shipped English numeric configuration produce %1.0f followed by '%'.
    return tuple(PMatchInfoSummaryLine(call, (x, 145 + 42, 30, 20), f'{value}%')
        for call, x, value in zip((0x483BCA, 0x483C22, 0x483C7A),
                                 (295, 370, 443), reversed(report.possession.averages)))


def ordinary_pmatchinfo_header_lines(report, clubs):
    if type(report) is not CompleteFixtureReport or report.metadata.previous_scores is not None:
        return ()
    lines = []
    for club_id, call, rect, style in zip(report.metadata.team_ids,
            (0x485388, 0x485421), ((176, 5, 175, 37), (411, 5, 175, 37)), (0x22, 0x21)):
        name = _source_name(clubs.get(club_id), 'name')
        if name is not None:
            lines.append(PMatchInfoSummaryLine(call, rect, name.decode('cp1252'), style))
    # 488ADE reads report +18, supplied by the retained 60BA80 score nibbles.
    # Display is permitted AFTER complete report ownership, not a context fallback.
    packed = report.completion.native_score_nibbles
    lines.append(PMatchInfoSummaryLine(0x4853C0, (354, 18, 55, 14),
                                     f'{packed & 15}    {(packed >> 4) & 15}'))
    return tuple(lines)
