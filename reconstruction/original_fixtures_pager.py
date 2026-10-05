"""Source-qualified PLeagueFixtures +D30/+D60 ordinary bitmap controls.

7BE3E8 ->64F7A0/64F860/64FBE0/64FDB0; descriptor +4 is F
(state capability flags, NOT fifteen frames). Both source atlases are 108x18.
Factory47C724 ->47F280 ->653320 gives panel origin0/0 and clip799x599.
"""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from ea444_decoder import decode_ea444
from ea444_tables import tables_from_original_executable
from ea444_quantization import quantization_from_verified_executable


PAGER_RESOURCES = (
    ('toogle_arrow_left.444', 4024,
     '31c0b0c96c5e13c10c4f38f04a47456c178ad87e12eb3381bf9f07010ca86982'),
    ('toogle_arrow_right.444', 3760,
     '125a70a2e4ac36970e592068c8781d9109e9b0518575f97949c24c369d3c7173'),
)
PAGER_PATH = 'FM2001_Art/Generic/GenericButtonsAndBars'


@dataclass(frozen=True)
class FixturesPageControl:
    direction: int
    event_id: int
    rect: tuple[int, int, int, int]
    flags: int

    @property
    def frame(self):
        #64FDB0 descriptor F: disabled wins, then pressed, then hover.
        if not self.flags & 2:
            return 3
        if self.flags & 0x30:
            return 1
        return 2 if self.flags & 8 else 0


def fixtures_page_controls(offset, club_count, flags=None):
    if (type(offset) is not int or type(club_count) is not int
            or club_count < 12 or not 0 <= offset <= club_count - 12):
        raise ValueError('Exact source Fixtures column window required')
    flags = {-1: 0x183, 1: 0x183} if flags is None else flags
    controls = []
    for direction, event, x, enabled in (
            (-1, 39, 351, offset != 0), (1, 40, 721, offset < club_count - 12)):
        value = flags[direction]
        if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
            raise ValueError('Exact native control flags required')
        value = value | 2 if enabled else value & ~2
        controls.append(FixturesPageControl(direction, event, (x, 213, 27, 18), value))
    return tuple(controls)


def fixtures_page_press(controls, x, y):
    if type(x) is not int or type(y) is not int:
        raise ValueError('Integer source pointer coordinates required')
    for control in controls:
        left, top, width, height = control.rect
        if left <= x < left + width and top <= y < top + height:
            #653480 container half-open hit test;64F7A0 requires enabled,
            #not already captured. Parent42DE00 accepts;46E040 dispatches.
            if control.flags & 1 and control.flags & 2 and not control.flags & 0x10:
                return control
    return None


@dataclass(frozen=True)
class OriginalFixturesPagerArt:
    left: tuple[bytes, ...]
    right: tuple[bytes, ...]

    def pixels(self, control):
        frames = self.left if control.direction == -1 else self.right
        if len(frames) != 4 or len(frames[control.frame]) != 27 * 18 * 4:
            raise ValueError('Incomplete original four-frame pager atlas')
        return frames[control.frame]


def load_verified_fixtures_pager_art(source_root, original_executable):
    exe = Path(original_executable).read_bytes()
    tables = tables_from_original_executable(exe)
    quant = quantization_from_verified_executable(exe)
    images = []
    for filename, size, digest in PAGER_RESOURCES:
        raw = Path(source_root).joinpath(*PAGER_PATH.split('/'), filename).read_bytes()
        if len(raw) != size or sha256(raw).hexdigest() != digest:
            raise ValueError('Fixtures arrow source identity mismatch')
        image = decode_ea444(raw, tables=tables, quant=quant)
        if (image.width, image.height) != (108, 18):
            raise ValueError('Fixtures arrow atlas geometry mismatch')
        #64E5D0: source x=descriptor.x + frame*27; no scaled/recolored pixels.
        images.append(tuple(b''.join(image.rgba[(y*108+frame*27)*4:
                        (y*108+(frame+1)*27)*4] for y in range(18)) for frame in range(4)))
    return OriginalFixturesPagerArt(*images)
