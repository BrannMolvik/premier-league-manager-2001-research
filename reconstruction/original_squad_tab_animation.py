"""PSquadScreen's concrete vft7BE814 update, not Button@ease animation.

652BC0 has lengths (11,1,1); 5D4D70 uses bases (0,11,22).
Call once per serialized visible UI pass. No duration/timer is inferred.
"""
from dataclasses import dataclass

from original_squad_resources import SQUAD_BUTTONS, SQUAD_PANEL_RECT

SQUAD_TAB_GROUP_LENGTHS = (11, 1, 1)
SQUAD_TAB_SOURCE_BASES = (0, 11, 22)


@dataclass
class OriginalSquadTabState:
    flags: int = 0x183
    group: int = 0
    subframe: int = 0

    def _check(self):
        if (type(self.group) is not int or not 0 <= self.group < 3
                or type(self.subframe) is not int
                or not 0 <= self.subframe < SQUAD_TAB_GROUP_LENGTHS[self.group]):
            raise ValueError('Invalid retained native Squad tab group/subframe')

    def target_group(self):
        return 2 if not self.flags & 2 else 1 if self.flags & 0x8000 else 0

    def set_pointer_inside(self, inside):
        self.flags = self.flags | 8 if inside else self.flags & ~8

    def pending(self):
        self._check()
        return (self.group != self.target_group()
                or (self.subframe < SQUAD_TAB_GROUP_LENGTHS[self.group] - 1
                    if self.flags & 8 else bool(self.subframe)))

    def update(self):
        self._check()
        old = self.group, self.subframe
        target = self.target_group()
        if target != self.group:
            self.subframe = (SQUAD_TAB_GROUP_LENGTHS[target] * self.subframe
                             // SQUAD_TAB_GROUP_LENGTHS[self.group])
            self.group = target
        if self.flags & 8:
            if self.subframe + 1 < SQUAD_TAB_GROUP_LENGTHS[self.group]:
                self.subframe += 1
        elif self.subframe:
            self.subframe -= 1
        return old != (self.group, self.subframe)

    @property
    def source_frame(self):
        self._check()
        return SQUAD_TAB_SOURCE_BASES[self.group] + self.subframe


class OriginalSquadTabAnimation:
    """Current combined view only; no unqualified formation-tab activation."""
    def __init__(self):
        self.states = {3: OriginalSquadTabState(flags=0x8183, group=1),
                       4: OriginalSquadTabState(), 5: OriginalSquadTabState()}

    def observe(self, pointer):
        px, py = SQUAD_PANEL_RECT[:2]
        for button in SQUAD_BUTTONS:
            x, y = px + button.origin[0], py + button.origin[1]
            inside = pointer is not None and x <= pointer[0] < x + 73 and y <= pointer[1] < y + 25
            self.states[button.control_id].set_pointer_inside(inside)

    def pending(self):
        return any(state.pending() for state in self.states.values())

    def update(self):
        changed = False
        for state in self.states.values():
            changed |= state.update()  # All three children, no short circuit.
        return changed

    def frames(self):
        return tuple(self.states[button.control_id].source_frame for button in SQUAD_BUTTONS)
