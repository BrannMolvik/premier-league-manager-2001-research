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


def _ordinary_entries(report):
    if type(report) is not CompleteFixtureReport or report.metadata.previous_scores is not None:
        return (), (), 0
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
    return events, entries, len(entries) - int(boundary)


def ordinary_report_script_count(report):
    """4872C0 list +60; both ordinary lists use the same eligibility table."""
    return _ordinary_entries(report)[2]


def script_scroll_step(report, first_row, direction):
    """64FF30/64FF90: one entry, clamped by 487520/487550 count-minus-six."""
    maximum = max(ordinary_report_script_count(report) - 6, 0)
    if type(first_row) is not int or not 0 <= first_row <= maximum:
        raise ValueError('Native list offset outside scroll bounds')
    if type(direction) is not int or direction not in (-1, 1):
        raise ValueError('Only source arrow step directions are accepted')
    return max(0, min(maximum, first_row + direction))


def ordinary_report_script_rows(report, *, list_side, first_row=0):
    if type(list_side) is not int or list_side not in (0, 1):
        raise ValueError('Native list side must be 0 or 1')
    if type(report) is not CompleteFixtureReport or report.metadata.previous_scores is not None:
        return ()
    events, entries, count = _ordinary_entries(report)
    # Exact 4872C0 tables filter +4==1 for both concrete default lists.
    # +50 is a row-constructor input, not permission to invent a side filter.
    if type(first_row) is not int or not 0 <= first_row <= max(count - 6, 0):
        raise ValueError('Native list offset outside scroll bounds')
    rows = []
    for slot in range(min(6, count - first_row)):
        logical_index = first_row + slot  # 486EE4: list +3C plus visible slot.
        original_index = entries[logical_index]
        flag78 = int(logical_index > 0 and entries[logical_index - 1] == original_index)
        current = events[original_index]
        if current.kind == 5 and not current.field(0x20) and current.field(0x1C):
            flag78 |= int(any(events[i].kind == 5 and not events[i].field(0x20)
                              and events[i].field(0x14) == current.field(0x14)
                              for i in entries[:logical_index]))
        after_boundary = any(events[i].kind == 9 for i in entries[:logical_index + 1])
        index = entries[logical_index + int(after_boundary)]
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
    from hashlib import sha256
    raw = (Path(repo_root) / 'original_assets/source/FM2001_Art/Generic/GenericButtonsAndBars/scroller_vert.444').read_bytes()
    if sha256(raw).hexdigest() != '3f96ef29d80c7d369f65236c29ae8281b7e490c3c71a65644490daefe5f1f9f7':
        raise ValueError('Original scroll arrow atlas hash mismatch')
    images['_scroll_arrows'] = decode_ea444(raw, tables=tables, quant=quant)
    if (images['_scroll_arrows'].width, images['_scroll_arrows'].height) != (72, 50):
        raise ValueError('Original scroll arrow atlas geometry mismatch')
    return images


class OriginalScriptShirtSource:
    """408320 primary custom atlases; no invented generic/alternate fallback.

    The deliberately imported selection covers all twenty original Premiership
    clubs. Unstaged families and alternate shirts remain closed.
    """
    HASHES = {
        'Arsenal': '0d1a264bcb920eaa984bb115cf681bbeb4e8ff22175e37119e18dc68cfb5fc25',
        'Aston_Villa': '19a55444f7b04b4bbe0df0edaccdb6a484c823554ec37a6a03db1e20a456d5c4',
        'Bradford': '23714003d9b57a9e1f02b6845bd808263fb1ed29e0828d3419ec453b2bc8a50f',
        'Charlton_Ath': 'ca8ec47fb0679ac56c37800962786170e073bcce59e1cd6168a5d8386333cdfe',
        'Chelsea': 'f5000bf4b9aea3f89fb8d3942199ba4743cb63fa10cc3019f84cd1df91cf5be8',
        'Coventry_City': 'a62be2bd04240a2ab85d49b7c263d4c0d6c5f33862eae83541c28d80334ca2f9',
        'Derby_County': 'a4c757e80c95d579b49879e945e01939a83bd4c633753b748861b580cc05d2a5',
        'Everton': 'c0c5efa319249750457437a6c21d147ba0941cd5c239ddd73252ef182596d3b5',
        'Ipswich': 'a5c7cf7547778974c3c5504c257607556c5e79781dcbefb6931d413334a375c2',
        'Leeds_United': '2425431a34b7fd782e1901e06427bae02cf09972258b91ff735782b4c1471126',
        'Leicester_City': 'c6be0ffdcd741e27929fb4c0750850596fe189cee597df2beb1d3a099c8f8bd8',
        'Liverpool': '706cd08bbc58e3b070deee6e0fcf420f440fb4f386d81c058f5a5ae6a1b3a0a3',
        'Man_City': 'f899139c4d8b442ccae8d1cf4b60ce65f091ad456bdde8c005572ee32a37359b',
        'Man_Utd': '46750817de8c5cbe7f77fad34727a0281f2bb92348d92b1ead3de7133c36f693',
        'Middlesbrough': '55695ac800a7be7058aa23ca0ea44278e5caa37133a74ef521e8f9df84e617f5',
        'Newcastle_Utd': '6941ff0088796129ff4a3bd73c0fcd520e79c3e3691d2e3d87487a1d89cce221',
        'Southampton': '54ca100b57ed02f1931fe8023226788aa5222d4ecd27813b896ecc299c17f43e',
        'Sunderland': '77114b42a829c754be0af5b202b17f30bacc56b7decbbba74bc14f3178b1e7d0',
        'Tottenham': 'd724426713975c7f7ded834d93956b3c1dd572e10d2bb5d12e53d090f09ec36e',
        'West_Ham_Utd': 'f482f62d9a8433a63ab96c873c5e5a0e80ab3d3215ecdf4597f25a801b59ea67',
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


def script_list_pixels(report, list_side, images, font, *, players=None, first_row=0):
    """6510F0 creates all six slots; 483750 paints native blank-row grids.

    The viewport offset is the source arrow callback's list +3C value.
    Partial report contexts never receive even empty placeholder rows.
    """
    from gate13_original_pixel_preview import encode_rgba_png
    if type(report) is not CompleteFixtureReport or report.metadata.previous_scores is not None:
        return ()
    rows = ordinary_report_script_rows(report, list_side=list_side, first_row=first_row)
    layers = []
    for slot in range(6):
        if slot < len(rows):
            layers.extend(script_row_pixels(rows[slot], images, font,
                                            players=players, report=report))
        else:
            x, y = (39 if list_side else 411), 260 + slot * 38
            for name, dx, width in (('match_name_grid', 0, 185), ('match_incid_grid', 189, 142)):
                image = images[name]
                if (image.width, image.height) != (width, 36):
                    raise ValueError('Native blank row grid geometry mismatch')
                layers.append((x + dx, y, width, 36,
                               encode_rgba_png(width, 36, image.rgba)))
    return tuple(layers)


def script_arrow_at_point(x, y):
    """483AA0 default child translation: event IDs 3/5 and 6/8."""
    for side, left in ((1, 17), (0, 389)):
        for direction, top in ((-1, 260), (1, 460)):
            if left <= x < left + 18 and top <= y < top + 25:
                return side, direction
    return None


def script_arrow_pixels(report, list_side, images, *, first_row=0, pressed_direction=None):
    """5F2BC0/5F2C00, 64FDB0: idle0, pressed1, disabled3; no fake repeat."""
    from gate13_original_pixel_preview import encode_rgba_png
    if type(report) is not CompleteFixtureReport or report.metadata.previous_scores is not None:
        return ()
    # Validate state even when art is not supplied by a diagnostic host.
    script_scroll_step(report, first_row, 1)
    atlas = images.get('_scroll_arrows')
    if atlas is None:
        return ()
    maximum = max(ordinary_report_script_count(report) - 6, 0)
    layers = []
    for direction, y, source_y in ((-1, 260, 0), (1, 460, 25)):
        enabled = first_row > 0 if direction == -1 else first_row < maximum
        frame = (1 if pressed_direction == direction else 0) if enabled else 3
        sx = frame * 18
        rgba = b''.join(atlas.rgba[(row * 72 + sx) * 4:(row * 72 + sx + 18) * 4]
                        for row in range(source_y, source_y + 25))
        layers.append((17 if list_side else 389, y, 18, 25, encode_rgba_png(18, 25, rgba)))
    return tuple(layers)
