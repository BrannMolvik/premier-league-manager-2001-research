"""First-screen Button states advanced by the source-owned UI update pass.

Ordinary loop 531AF0 -> 531B40 takes the available 877A34 semaphore, calls
5329D0, then releases it. 532A62 -> 6541E0 walks panels; 6538F0 walks visible
update children and dispatches +68 -> 6527F0. There is no fixed hover timer
on that path. An adapter must supply serialized UI passes, not invented ms.
"""
from original_button_frames import OriginalButtonState, BUTTON_GROUP_LENGTHS


class OriginalFirstScreenAnimation:
    def __init__(self):
        self.states = {}

    def observe(self, snapshot, pointer):
        for control in snapshot.controls:
            state = self.states.setdefault((snapshot.screen, control.event), OriginalButtonState())
            inside = pointer is not None and (
                control.rect.x <= pointer[0] < control.rect.right
                and control.rect.y <= pointer[1] < control.rect.bottom
            )
            state.set_pointer_inside(inside)

    def frames(self, snapshot):
        return {control.event: self.states[(snapshot.screen, control.event)].source_frame_index
                for control in snapshot.controls}

    def pending(self, snapshot):
        for control in snapshot.controls:
            state = self.states[(snapshot.screen, control.event)]
            if state.group != state.group_for_flags(state.flags):
                return True
            if state.flags & 8:
                if state.subframe + 1 < BUTTON_GROUP_LENGTHS[state.group]:
                    return True
            elif state.subframe:
                return True
        return False

    def advance(self, snapshot):
        # Every active child receives its update, regardless of an earlier
        # child changing. Do not short-circuit this native ordered traversal.
        changed = False
        for control in snapshot.controls:
            changed |= self.states[(snapshot.screen, control.event)].update()
        return changed
