"""Read-only default script-list projection from a complete captured stream.

633C50/633D00 decode; 4872C0 selects; 486EC0 retains duplicate/boundary
inputs; 485B30 selects report-owned participants. No score/event reconstruction.
Opaque non-row families are consumed, not assigned invented presentation fields.
"""
from dataclasses import dataclass
from complete_fixture_report import CompleteFixtureReport


@dataclass(frozen=True)
class DecodedReportRowEvent:
    minute: int
    kind: int | None
    fields: tuple[tuple[int, int], ...]

    def field(self, offset):
        for key, value in self.fields:
            if key == offset:
                return value
        raise ValueError(f'Unwritten decoded presentation field {offset:#x}')


def decoded_report_row_events(script):
    if type(script) is not bytes or len(script) < 2:
        raise ValueError('Exact captured script bytes required')
    cursor = 0

    def bits(width):
        nonlocal cursor
        if cursor + width > len(script) * 8:
            raise ValueError('Truncated native script')
        value = sum(((script[(cursor + i) // 8] >> ((cursor + i) % 8)) & 1) << i
                    for i in range(width))
        cursor += width
        return value

    count = bits(10)
    events = []
    for _ in range(count):
        minute, fields, kind = bits(8), {}, None
        if bits(1):
            for offset, width in ((4, 1), (8, 5), (12, 5), (0x2C, 1),
                                  (0x24, 3), (0x20, 1)):
                fields[offset] = bits(width)
            kind = (4, 3, 1, 2)[bits(2)]
        elif bits(1):
            if not bits(1):
                bits(21)  # Opaque 6339D0 family; never a default row.
            else:
                tag = bits(2)
                if tag == 1:
                    bits(2)  # FullTime payload, not a default row.
                elif tag == 2 and not bits(1):
                    kind = 9
        elif bits(1):
            if bits(1):
                kind = 5
                fields[4], fields[0x20] = bits(1), bits(1)
                if fields[0x20]:
                    fields[0x10] = bits(5)
                else:
                    fields[0x14] = bits(5)
                    fields[0x18], fields[0x1C] = bits(1), bits(1)
            else:
                bits(1)  # Opaque tactical command side.
                tag = bits(2)
                if tag in (1, 3):
                    bits(3)
                elif tag == 2:
                    bits(2 if bits(1) else 4)
                elif bits(1):
                    bits(5)
                else:
                    bits(5); bits(5); bits(2)
        elif not bits(1):
            kind = 10
            fields[4], fields[8], fields[0x2C] = bits(1), bits(5), bits(5)
        else:
            bits(1); bits(5)
            if bits(1):
                bits(4)
            elif not bits(1):
                bits(4)
            else:
                bits(3); bits(4)
        events.append(DecodedReportRowEvent(minute, kind, tuple(sorted(fields.items()))))
    if len(script) != (cursor + 7) // 8 or bits(len(script) * 8 - cursor):
        raise ValueError('Noncanonical script tail')
    return tuple(events)


@dataclass(frozen=True)
class NativeReportScriptRow:
    list_side: int
    slot: int
    event_index: int
    event: DecodedReportRowEvent
    field_74: int
    field_78: int
    participant_side: int
    participant_index: int
    player_id: int
    shirt_number: int

    @property
    def origin(self):
        return (39 if self.list_side else 411, 145 + 115 + self.slot * 38)


def ordinary_report_script_rows(report, *, list_side):
    if type(list_side) is not int or list_side not in (0, 1):
        raise ValueError('Native list side must be 0 or 1')
    if type(report) is not CompleteFixtureReport or report.metadata.previous_scores is not None:
        return ()
    events = decoded_report_row_events(report.script)
    entries = []
    boundary = False
    for index, event in enumerate(events):
        kind = event.kind
        if kind in (1, 2, 3, 4):
            if event.field(0x24) in (0, 3) and event.field(4) == 1:
                entries.append(index)
        elif kind == 5 and event.field(4) == 1:
            entries.append(index)
        elif kind == 10 and event.field(4) == 1:
            entries.extend((index, index))
        elif kind == 9:
            entries.append(index)
            boundary = True
    # Exact 4872C0 tables filter +4==1 for both concrete default lists.
    # +50 is a row-constructor input, not permission to invent a side filter.
    count = len(entries) - int(boundary)
    rows = []
    for slot in range(min(6, count)):
        original_index = entries[slot]
        flag78 = int(slot > 0 and entries[slot - 1] == original_index)
        current = events[original_index]
        if current.kind == 5 and not current.field(0x20) and current.field(0x1C):
            flag78 |= int(any(events[i].kind == 5 and not events[i].field(0x20)
                              and events[i].field(0x14) == current.field(0x14)
                              for i in entries[:slot]))
        after_boundary = any(events[i].kind == 9 for i in entries[:slot + 1])
        index = entries[slot + int(after_boundary)]
        event = events[index]
        flag74 = list_side
        if event.kind in (1, 2, 3, 4):
            flag74 = event.field(0x20)
            side, participant = (0 if flag74 else 1), event.field(8)
        elif event.kind == 5:
            side = 1
            participant = event.field(0x10 if event.field(0x20) else 0x14)
        elif event.kind == 10:
            side, participant = 1, event.field(0x2C if list_side else 8)
        else:
            raise ValueError('Boundary row lacks a source-backed participant')
        if participant >= len(report.metadata.participants[side]):
            raise ValueError('Native row participant outside captured owner')
        owner = report.metadata.participants[side][participant]
        rows.append(NativeReportScriptRow(list_side, slot, index, event,
                                         flag74, flag78, side, participant,
                                         owner.player_id, owner.shirt_number))
    return tuple(rows)


def script_row_text_lines(row):
    """485F50: written label/decimal buffers; name/shirt have separate owners."""
    from original_pmatchinfo_resources import pmatchinfo_script_incident_selection, pmatchinfo_original_english
    from original_pmatchinfo_summary import PMatchInfoSummaryLine
    event = row.event
    def incident_field(offset):
        # The row producer reads these only in the incident family branch.
        return event.field(offset) if event.kind == 5 and not event.field(0x20) else 0
    selection = pmatchinfo_script_incident_selection(event.kind,
        row_field_74=row.field_74, row_field_78=row.field_78,
        event_field_20=event.field(0x20) if event.kind == 5 else 0,
        event_field_18=incident_field(0x18), event_field_1c=incident_field(0x1C))
    label = '' if selection is None else selection.label
    # 485FFC clears the decimal only in the goal/shootout branch. A
    # duplicated substitution retains its number, without the MINS suffix.
    decimal = str(event.minute)
    if event.kind in (1, 2, 3, 4) and not row.field_74 and row.field_78:
        decimal = ''
    if not row.field_78:
        decimal += pmatchinfo_original_english(0x982010)
    x, y = row.origin
    return (PMatchInfoSummaryLine(0x4836AC, (x + 210, y + 2, 185, 12), label, 0x21),
            PMatchInfoSummaryLine(0x4836E4, (x + 210, y + 18, 185, 12), decimal, 0x21))


def load_script_row_art(repo_root, executable, *, game_dir=None):
    from pathlib import Path
    from original_pmatchinfo_resources import (PMATCHINFO_DYNAMIC_INCIDENT_RESOURCE_NAMES,
        validate_staged_pmatchinfo_presentation_assets, pmatchinfo_import_path)
    from ea444_tables import tables_from_original_executable
    from ea444_quantization import quantization_from_verified_executable
    from ea444_decoder import decode_ea444
    validate_staged_pmatchinfo_presentation_assets(Path(repo_root))
    blob = Path(executable).read_bytes()
    tables, quant = tables_from_original_executable(blob), quantization_from_verified_executable(blob)
    images = {name: decode_ea444(pmatchinfo_import_path(Path(repo_root), name).read_bytes(),
                             tables=tables, quant=quant)
            for name in ('match_name_grid', 'match_incid_grid',
                         *PMATCHINFO_DYNAMIC_INCIDENT_RESOURCE_NAMES)}
    if game_dir is not None:
        images['_shirt_source'] = OriginalScriptShirtSource(repo_root, blob, game_dir)
    return images


class OriginalScriptShirtSource:
    """408320 primary custom atlases; no invented generic/alternate fallback.

    The deliberately imported selection currently covers the genuine Coventry /
    Middlesbrough route. Unstaged families and alternate shirts remain closed.
    """
    HASHES = {
        'Coventry_City': 'a62be2bd04240a2ab85d49b7c263d4c0d6c5f33862eae83541c28d80334ca2f9',
        'Middlesbrough': '55695ac800a7be7058aa23ca0ea44278e5caa37133a74ef521e8f9df84e617f5',
    }

    def __init__(self, repo_root, executable_bytes, game_dir):
        from pathlib import Path
        from verify import verify_canonical_files
        from fm2001_data import FM2001Database
        from gate13_button_source_trace import OriginalPE32
        from ea444_tables import tables_from_original_executable
        from ea444_quantization import quantization_from_verified_executable
        verify_canonical_files(Path(game_dir))
        self.database = FM2001Database(game_dir)
        self.root = Path(repo_root) / 'original_assets/source/FM2001_Art/Generic/Front-End-Shirts/Custom'
        pe = OriginalPE32.parse(executable_bytes)
        self.clashes = pe.read(0x834AF8, 23 * 6)
        self.tables = tables_from_original_executable(executable_bytes)
        self.quant = quantization_from_verified_executable(executable_bytes)
        self.cache = {}

    def _clash(self, left, right):
        # 5EF9E0 compares both six-byte sentinel-terminated color lists.
        if not 0 <= left < 23 or not 0 <= right < 23:
            raise ValueError('Original kit color outside recovered clash table')
        if left == right:
            return True
        for first, second in ((left, right), (right, left)):
            for value in self.clashes[first * 6:first * 6 + 6]:
                if value == 23:
                    break
                if value == second:
                    return True
        return False

    def selected_atlas(self, report, row):
        from hashlib import sha256
        from original_management_background import native_art_component
        from ea444_decoder import decode_ea444
        if type(report) is not CompleteFixtureReport:
            return None
        home, away = report.metadata.team_ids
        if any(not 0 <= i < len(self.database.clubs) for i in (home, away)):
            return None
        records = tuple(self.database.master[4 + i * 181:4 + (i + 1) * 181]
                        for i in (home, away))
        # 4022D0 disk +3A/+46 -> temp +4A/+56; 403660 copies unchanged.
        hp, ap = records[0][0x3A], records[1][0x3A]
        ha, aa = records[0][0x46], records[1][0x46]
        flags = (0, 0)
        if self._clash(hp, ap):
            if hp != aa:
                flags = (0, 1)
            elif ha != ap:
                flags = (1, 0)
            elif ha != aa:
                flags = (1, 1)
        side = row.participant_side  # 485D91 selects constructor's home inversion.
        if flags[side]:
            return None
        key = native_art_component(self.database.clubs[(home, away)[side]].graphics_basename)
        if key not in self.HASHES:
            return None
        if key not in self.cache:
            raw = (self.root / (key + '.444')).read_bytes()
            if sha256(raw).hexdigest() != self.HASHES[key]:
                raise ValueError('Original custom shirt hash mismatch')
            image = decode_ea444(raw, tables=self.tables, quant=self.quant)
            if (image.width, image.height) != (36, 40 * 32):
                raise ValueError('Original shirt atlas geometry mismatch')
            self.cache[key] = image
        return self.cache[key]


def script_row_player_color(row, players):
    """5D6C50 source RGB channels BEFORE the runtime display-format packing.

    Only actual +14 bit4/bit5 states are retained. Unknown +174 states cannot
    fall through to a guessed default color.
    """
    from runtime_state import RuntimePlayer
    player = players.get(row.player_id)
    if type(player) is not RuntimePlayer:
        return None
    if player.match_active:
        return (255, 255, 255)
    if player.match_substitute_available:
        return (0xE8, 0xBF, 0x5E)
    return None


def script_row_player_name(row, players):
    """417AE0 mode0 with the source-backed +14 selection color branches.

    Other current-player color states need their actual +174 bits and native
    color rendering, not a white default. They remain explicitly unavailable.
    """
    from runtime_state import RuntimePlayer
    from original_pmatchinfo_summary import PMatchInfoSummaryLine, _source_name
    player = players.get(row.player_id)
    if type(player) is not RuntimePlayer or script_row_player_color(row, players) is None:
        return None
    first, surname = _source_name(player, 'first_name'), _source_name(player, 'surname')
    if first is None or surname is None:
        return None
    text = surname if first.startswith(b'-') else first[:1] + b'. ' + surname
    x, y = row.origin
    return PMatchInfoSummaryLine(0x483637, (x + 40, y + 2, 185, 14), text.decode('cp1252'), 0x21)


def script_row_pixels(row, images, font, *, players=None, report=None):
    """Owner-local grids/icon and written text, clipped to the native list.

    PlayerText and shirt bitmap remain separate, not guessed substitutes.
    """
    from original_pmatchinfo_resources import pmatchinfo_script_incident_selection
    from gate13_original_pixel_preview import encode_rgba_png
    from original_management_canvas import _clip_text_mask
    x, y = row.origin
    list_x = 39 if row.list_side else 411
    clip = (list_x, 260, list_x + 332, 488)
    layers = []

    def place(px, py, width, height, rgba):
        left, top = max(px, clip[0]), max(py, clip[1])
        right, bottom = min(px + width, clip[2]), min(py + height, clip[3])
        if left >= right or top >= bottom:
            return
        cropped = b''.join(rgba[((ry - py) * width + left - px) * 4:
                               ((ry - py) * width + right - px) * 4]
                           for ry in range(top, bottom))
        layers.append((left, top, right - left, bottom - top,
                       encode_rgba_png(right - left, bottom - top, cropped)))

    for name, dx in (('match_name_grid', 0), ('match_incid_grid', 189)):
        image = images[name]
        expected = (185, 36) if dx == 0 else (142, 36)
        if (image.width, image.height) != expected:
            raise ValueError('Native row grid geometry mismatch')
        place(x + dx, y, image.width, image.height, image.rgba)
    shirts = images.get('_shirt_source')
    if shirts is not None and report is not None:
        atlas = shirts.selected_atlas(report, row)
        # 485F50's native source offset is (captured shirt - 1) * 32.
        if atlas is not None and 1 <= row.shirt_number <= 40:
            start = (row.shirt_number - 1) * 32 * 36 * 4
            place(x, y + 2, 36, 32, atlas.rgba[start:start + 36 * 32 * 4])
    fields = dict(row.event.fields)
    selection = pmatchinfo_script_incident_selection(row.event.kind,
        row_field_74=row.field_74, row_field_78=row.field_78,
        event_field_20=fields.get(0x20, 0), event_field_18=fields.get(0x18, 0),
        event_field_1c=fields.get(0x1C, 0))
    if selection is not None:
        icon = images[selection.resource_name]
        if (icon.width, icon.height) != (14, 14):
            raise ValueError('Native incident icon geometry mismatch')
        place(x + 191, y + 11, 14, 14, icon.rgba)
    # Render text with the native control/list intersection, not a modern row width.
    lines = script_row_text_lines(row)
    name = None if players is None else script_row_player_name(row, players)
    if name is not None:
        lines += (name,)
    for line in lines:
        lx, ly, width, height = line.rect
        mask = font.render_text_alpha(line.text)
        origin = (lx, ly + height // 2 - font.native_line_height() // 2)
        text = _clip_text_mask(mask, line_origin=origin,
            clip_rect=(max(lx, clip[0]), max(ly, clip[1]),
                       min(lx + width, clip[2]), min(ly + height, clip[3])))
        if text is not None:
            from original_management_canvas import _endpoint_text_rgba
            tx, ty, tw, th, alpha = text
            if line is name:
                rgb = script_row_player_color(row, players)
                rgba = b''.join(bytes((*rgb, value)) for value in alpha)
            else:
                rgba = _endpoint_text_rgba(alpha, 0xFFFF)
            layers.append((tx, ty, tw, th,
                encode_rgba_png(tw, th, rgba)))
    return tuple(layers)
