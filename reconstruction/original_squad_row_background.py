"""Source-qualified populated PSquadPlayerRow solid cells, not a grid swap.

The modern display retains the original RGB8 intent, like Squad text. Native
packed16 format/expansion and the unproven alternate-palette producer are not
inferred here. Selection/name-colour flags remain independent of pointer hover.
"""
from dataclasses import dataclass

from original_squad_presenter import OriginalSquadViewportSnapshot
from original_squad_resources import (
    SQUAD_FIRST_ROSTER_RECT, SQUAD_RESERVE_ROSTER_RECT, SQUAD_PANEL_RECT,
)

SQUAD_CELL_SETUP_VA = 0x489530
SQUAD_CELL_PALETTE_SETUP_VA = 0x4B5078
SQUAD_CELL_DRAW_VA = 0x5D6720
SQUAD_CELL_FRAME_VA = 0x64FDB0
SQUAD_ROW_INITIAL_PICTURE_FLAGS = 0x183
SQUAD_CELL_NORMAL_RGB = (57, 130, 171)
SQUAD_CELL_HOVER_RGB = (16, 95, 162)
SQUAD_CELL_RECTS = ((1, 1, 22, 14), (28, 1, 38, 14), (71, 1, 154, 14))


def squad_cell_frame(flags: int) -> int:
    """64FDB0 with owner descriptor5: no pressed/selection frame exists."""
    if type(flags) is not int or not 0 <= flags <= 0xFFFFFFFF:
        raise ValueError('Squad picture flags must be uint32')
    return 2 if flags & 2 and flags & 8 else 0


@dataclass(frozen=True)
class OriginalSquadRowBackground:
    owner: int
    visible_index: int
    row_origin: tuple[int, int]
    cells: tuple[tuple[int, int, int, int], ...]

    @property
    def key(self):
        return self.owner, self.visible_index

    def contains(self, x, y):
        left, top = self.row_origin
        return (top <= y < top + 17
                and (left <= x < left + 226 or left + 239 <= x < left + 328))


def build_squad_row_backgrounds(first, reserve=None):
    """Keep populated native slots only, with the original parent transforms."""
    backgrounds = []
    for owner_id, (snapshot, owner) in enumerate(((first, SQUAD_FIRST_ROSTER_RECT),
                                                 (reserve, SQUAD_RESERVE_ROSTER_RECT))):
        if snapshot is None and owner_id == 1:
            continue
        if not isinstance(snapshot, OriginalSquadViewportSnapshot):
            raise ValueError('Original Squad viewport is required for populated cells')
        seen = set()
        for row in snapshot.rows:
            index = row.visible_index
            if (type(index) is not int or not 0 <= index < 20 or index in seen
                    or row.y != 154 + 17 * index):
                raise ValueError('Squad populated slot lost its native geometry')
            seen.add(index)
            x = SQUAD_PANEL_RECT[0] + owner.x
            y = SQUAD_PANEL_RECT[1] + owner.y + row.y
            backgrounds.append(OriginalSquadRowBackground(owner_id, index, (x, y),
                tuple((x + dx, y + dy, w, h) for dx, dy, w, h in SQUAD_CELL_RECTS)))
    return tuple(backgrounds)


def squad_row_at_point(backgrounds, x, y):
    """650F60/6515C0 paired main+SCF pointer ownership, half-open geometry."""
    return next((row.key for row in backgrounds if row.contains(x, y)), None)
