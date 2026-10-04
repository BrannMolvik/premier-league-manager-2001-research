"""Explicit retained allocation bytes, never a fresh-club zero default.

0x5DA538 maps +134/+138 to home/visiting seating, +13C/+140 to
home/visiting terrace. The latter unsigned dwords clamp to zero above 200000.
The Windows adapter retains actual non-zeroing allocation bytes; missing
producer inputs remain unknown. It does not replay original heap history.
"""
from dataclasses import dataclass
import hashlib
import json

SOURCE_SHA256 = '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3'


@dataclass(frozen=True)
class RetainedClubAllocationCapacities:
    plus13c: int
    plus140: int
    evidence_sha256: str
    allocation_kind: str = 'observed-original-lifecycle'

    def __post_init__(self):
        if any(type(v) is not int or not 0 <= v <= 0xFFFFFFFF
               for v in (self.plus13c, self.plus140)):
            raise ValueError('Capacity allocation bytes must be exact unsigned dwords')
        if (type(self.evidence_sha256) is not str or len(self.evidence_sha256) != 64
                or any(c not in '0123456789abcdef' for c in self.evidence_sha256)):
            raise ValueError('Retained allocation requires its exact evidence identity')
        if self.allocation_kind not in ('observed-original-lifecycle', 'windows-heapalloc-flags0'):
            raise ValueError('Unknown allocation producer')

    @property
    def home_terrace(self):
        return self.plus13c if self.plus13c <= 200000 else 0

    @property
    def visiting_terrace(self):
        return self.plus140 if self.plus140 <= 200000 else 0


def retained_capacity_lifecycle(raw: bytes):
    """Import only a completed gap-free selected user-thread lifecycle receipt.

    This supplies ONE observed object's bytes, not other clubs/worlds/defaults.
    It is not original execution, and creates no report or fixture link.
    """
    if type(raw) is not bytes:
        raise ValueError('Exact receipt bytes required')
    data = json.loads(raw)
    coverage = data.get('write_watch_coverage', {})
    if (data.get('source_sha256') != SOURCE_SHA256
            or data.get('stop_reason') != 'selected_club_uncontrolled_read'
            or data.get('selected_club_import_observed') is not True
            or data.get('capacity_initializer_proven') is not False
            or coverage.get('broken') is not False
            or coverage.get('continuous_all_user_thread_write_watch_coverage_proven') is not True
            or coverage.get('debug_events_checked_without_gap') is not True):
        raise ValueError('No qualified unchanged-allocation lifecycle')
    start, end = coverage.get('start_debug_event_number'), coverage.get('stop_debug_event_number')
    if (type(start) is not int or type(end) is not int or end < start
            or coverage.get('checks') != end - start + 1
            or coverage.get('resumed_events_checked') != end - start):
        raise ValueError('Coverage event ledger has a gap')
    checkpoints = coverage.get('checkpoints', [])
    if not checkpoints or any(any(r.get(k) is not True for k in (
            'all_live_threads_armed', 'native_all_live_threads_armed',
            'wow64_all_live_threads_armed')) for r in checkpoints):
        raise ValueError('Both context views must retain all live-thread watches')
    events = data.get('events', [])
    allocations = [e for e in events if e.get('kind') == 'allocation_before_constructor']
    if len(allocations) != 1 or any(e.get('kind') == 'hardware_dword_write_after_instruction' for e in events):
        raise ValueError('Unchanged-allocation import does not adjudicate writers')
    receiver = events[-1].get('attendance_receiver', {})
    allocation = allocations[0]
    club_id = receiver.get('plus4_word_u16')
    values = receiver.get('capacity_u32')
    if (events[-1].get('source_va') != 0x5DA538
            or receiver.get('vftable_u32') != 0x7BD614
            or receiver.get('address') != allocation.get('club_address')
            or events[-1].get('identity_import_observed') is not True
            or events[-1].get('observed_club_plus4_word_u16') != club_id
            or type(club_id) is not int or not 0 <= club_id <= 0xFFFF
            or type(values) is not list or len(values) != 2
            or allocation.get('visiting_capacity_u32') != values):
        raise ValueError('Exact allocation/import/selected receiver identity required')
    return club_id, RetainedClubAllocationCapacities(*values, hashlib.sha256(raw).hexdigest())


def fresh_windows_club_array_capacity_bytes(club_count: int, *, kernel=None):
    """Preserve actual allocation bytes using the recovered large-array API.

    66AB1E pushes 1 into 66E746: HeapCreate(0, 4096, 0).
    669CDE rounds size to 16; 669CEE uses HeapAlloc(heap, 0, size).
    40BBE0's array has a four-byte cookie and 2A8-byte objects.
    The port's private heap/history is NOT the original process's history.
    Byte values are explicitly OS-produced, never promised zero or replayed
    from the one original receipt. Only these two dwords are retained; other
    simulation state remains supplied by recovered constructors/importers.
    """
    if type(club_count) is not int or not 7 <= club_count <= 0xFFFF:
        raise ValueError('This adapter requires a qualified large club array')
    import ctypes as c
    import os
    import struct
    if kernel is None:
        if os.name != 'nt':
            return {}
        kernel = c.WinDLL('kernel32', use_last_error=True)
        for name, arguments, result in (
                ('HeapCreate', [c.c_uint32, c.c_size_t, c.c_size_t], c.c_void_p),
                ('HeapAlloc', [c.c_void_p, c.c_uint32, c.c_size_t], c.c_void_p),
                ('HeapDestroy', [c.c_void_p], c.c_int)):
            fn = getattr(kernel, name)
            fn.argtypes, fn.restype = arguments, result
    size = (4 + club_count * 0x2A8 + 15) & ~15
    heap = kernel.HeapCreate(0, 0x1000, 0)
    if not heap:
        raise OSError('Source-qualified private HeapCreate failed')
    try:
        pointer = kernel.HeapAlloc(heap, 0, size)
        if not pointer:
            raise MemoryError('Source-qualified non-zeroing club-array allocation failed')
        values = {}
        for index in range(club_count):
            raw = c.string_at(pointer + 4 + index * 0x2A8 + 0x13C, 8)
            identity = hashlib.sha256(b'windows-heapalloc-flags0\0'
                + struct.pack('<II', size, index) + raw).hexdigest()
            values[index] = RetainedClubAllocationCapacities(
                *struct.unpack('<II', raw), identity, 'windows-heapalloc-flags0')
        return values
    finally:
        if not kernel.HeapDestroy(heap):
            raise OSError('Owned club-allocation heap cleanup failed')
