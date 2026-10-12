"""SHA-verified FM2001 MyWindow source-only pointer window routing.

Original 0x532680 -> 0x653B40 -> 0x653480. Owner+0 nonzero
selects first virtual+0x44-eligible window in REVERSE stack order,
tests that ONE window's bounds, and otherwise follows a separate
external fallback. When owner+0 is zero it checks ALL windows
in FORWARD order, independently of virtual+0x44. The original
PSupportStart virtual+0x44 is 0x628060, returning 1.
This does not accept a real mouse click or mutate live game state.
"""
from __future__ import annotations
from dataclasses import dataclass


class NativeWindowStackError(ValueError):
    pass


@dataclass(frozen=True)
class NativeWindow:
    source_identity: int
    bounds: tuple[int, int, int, int]
    virtual44_eligible: bool

    def __post_init__(self):
        if type(self.source_identity) is not int or self.source_identity < 0:
            raise NativeWindowStackError("Need source-native window identity")
        if (type(self.bounds) is not tuple or len(self.bounds) != 4
                or any(type(v) is not int or not -(1 << 31) <= v < (1 << 31)
                       for v in self.bounds)
                or self.bounds[0] >= self.bounds[2]
                or self.bounds[1] >= self.bounds[3]):
            raise NativeWindowStackError("Need valid native half-open window bounds")
        if type(self.virtual44_eligible) is not bool:
            raise NativeWindowStackError("Require observed native virtual44 Boolean")

    def contains(self, point: tuple[int, int]) -> bool:
        x, y = point
        left, top, right, bottom = self.bounds
        return left <= x < right and top <= y < bottom


@dataclass(frozen=True)
class NativeWindowRoute:
    owner_capture_branch: bool
    checked_vft44_indices: tuple[int, ...]
    selected_index: int | None
    dispatched_indices: tuple[int, ...]
    external_fallback_branch: bool


def project_original_native_window_route(
    windows: tuple[NativeWindow, ...],
    *,
    source_point: tuple[int, int],
    owner_capture_flag_nonzero: bool,
) -> NativeWindowRoute:
    """Bounded 0x653B40 routing only; 0x653480 can still reject input.

    The actual native manager flag, window identities, origin and pixel
    coordinate must be supplied. Do not invent missing virtual results
    or a fallback Win32 callback. A captured stack with no eligible
    window is not a proven original successful path and fails closed.
    """
    if (type(windows) is not tuple or
            any(type(w) is not NativeWindow for w in windows) or
            len({w.source_identity for w in windows}) != len(windows)):
        raise NativeWindowStackError("Require original registered distinct windows")
    if (type(source_point) is not tuple or len(source_point) != 2 or
            any(type(x) is not int or not -(1 << 31) <= x < (1 << 31)
                for x in source_point)):
        raise NativeWindowStackError("Require original signed source screen point")
    if type(owner_capture_flag_nonzero) is not bool:
        raise NativeWindowStackError("Require original manager+0 branch flag")
    if owner_capture_flag_nonzero:
        checked = []
        for index in range(len(windows) - 1, -1, -1):
            checked.append(index)
            if windows[index].virtual44_eligible:
                inside = windows[index].contains(source_point)
                return NativeWindowRoute(
                    True, tuple(checked), index, (index,) if inside else (), not inside
                )
        raise NativeWindowStackError("No original vft+0x44 eligible captured window")
    return NativeWindowRoute(
        False, (), None,
        tuple(i for i, w in enumerate(windows) if w.contains(source_point)),
        False,
    )
