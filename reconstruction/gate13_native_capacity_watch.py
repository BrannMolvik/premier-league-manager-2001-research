"""Bounded, private Windows/WOW64 observation of canonical club capacity state.

This debugger launches ONLY the checksum-qualified original in a private working
directory. It never attaches to an existing process or supplies capacity values.
INT3 probes are in-memory only; two hardware dword WRITE watches are armed at
the allocation return, before array construction. A receipt is observational
evidence, NEVER a report input or automatic proof of an initializer.

Capacity/positive-control launches require the exact-stage windowed runtime
receipt. A separate ten-second bounded display-only qualification is permitted.
Daniel handles audio manually; no audio/signing prerequisite or unsafe override.

Win32 ABI references: Microsoft DEBUG_EVENT, WOW64_CONTEXT, WaitForDebugEvent,
Wow64GetThreadContext and Wow64SetThreadContext documentation. No GUI input is
generated. The launched process is terminated on every bounded exit.
"""
from __future__ import annotations

import argparse
import ctypes as c
from hashlib import sha256
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import struct
import time

from gate13_button_source_trace import OriginalPE32, OriginalPETraceError, require_private_output_path
from gate13_native_probe_safety import check_private_stage, ProbeSafetyError
from gate13_native_display_watch import DisplayWatch, DisplayWatchError
from gate13_native_dxgi_evidence import MODE as DXGI_MODE, windowed_dxgi_proof

U32, U16, PTR = c.c_uint32, c.c_uint16, c.c_void_p
CONTEXT_FLAGS = 0x1001F  # WOW64 control/integer/segments/FPU/debug registers
ALLOC_RETURN, CONSTRUCTED, IMPORTED, UNCONTROLLED_READ = 0x40BC14, 0x40BC43, 0x40BA2C, 0x5DA538
STRIDE, CAPACITY_OFFSETS = 0x2A8, (0x13C, 0x140)
GRAPHICS_SUCCESS, CREATE_WINDOW_CALL = 0x6153A0, 0x6A6363
FOREGROUND_REQUEST, FOREGROUND_RETURN = 0x6A6016, 0x6A601C
WINDOW_CREATED = 0x6A6369
STARTUP_SURFACE_RETURNS = {0x5EE232: 0x1C, 0x5EE252: 0x88}
CREATE_WINDOW_INSTRUCTION = bytes.fromhex('ff1584d27b00')
PRESENTATION_SHIM = 'createwindowexa-6a6363-clear-topmost-v1'
STARTUP_SITES = (0x66AB26, 0x66AB37, 0x66AB74, 0x530DAB, 0x530DD9, 0x66ABA7, 0x66ABF4,
                 0x515C11, 0x515C17, 0x53078D, 0x5307F8, 0x53085F,
                 0x53093A, 0x5309DC, 0x530A79, 0x50D630,
                 0x530E29, 0x530E47, 0x615188, GRAPHICS_SUCCESS, CREATE_WINDOW_CALL, WINDOW_CREATED, FOREGROUND_REQUEST, FOREGROUND_RETURN, 0x6A93FB, 0x6A941E,
                 0x530EEE, 0x530F02, 0x530F3B, 0x530F9E, 0x530FB8, 0x531079,
                 0x531088, 0x53108D, 0x530F6E, 0x461E20, 0x461F31, 0x461F36,
                 0x6154CC, 0x6154CF, 0x531092, 0x531097, 0x5310B7, 0x5310BC,
                 0x53120A, 0x53120F)
ONE_SHOT_SITES = frozenset((0x6154CC, 0x6154CF))
INSTALL_QUERY_RETURNS = {0x53078D: 'CD Drive', 0x5307F8: 'Install Dir', 0x53085F: 'art',
                         0x53093A: 'fmv', 0x5309DC: 'matchengine', 0x530A79: 'stadia'}
RESOURCE_SELECTOR_RETURNS = frozenset((0x53085F, 0x53093A, 0x5309DC, 0x530A79))


class CapacityWatchError(OriginalPETraceError):
    pass


class Wow64Context(c.Structure):
    _fields_ = [(n, U32) for n in ('ContextFlags', 'Dr0', 'Dr1', 'Dr2', 'Dr3', 'Dr6', 'Dr7')]
    _fields_ += [('FloatSave', c.c_ubyte * 112)]
    _fields_ += [(n, U32) for n in ('SegGs', 'SegFs', 'SegEs', 'SegDs', 'Edi', 'Esi', 'Ebx',
                                  'Edx', 'Ecx', 'Eax', 'Ebp', 'Eip', 'SegCs', 'EFlags', 'Esp', 'SegSs')]
    _fields_ += [('ExtendedRegisters', c.c_ubyte * 512)]


class ExceptionRecord(c.Structure):
    _fields_ = [('code', U32), ('flags', U32), ('record', PTR), ('address', PTR),
                ('count', U32), ('information', c.c_size_t * 15)]


class ExceptionInfo(c.Structure):
    _fields_ = [('record', ExceptionRecord), ('first_chance', U32)]


class ProcessInfo(c.Structure):
    _fields_ = [('file', PTR), ('process', PTR), ('thread', PTR), ('base', PTR),
                ('offset', U32), ('size', U32), ('tls', PTR), ('start', PTR), ('name', PTR), ('unicode', U16)]


class ThreadInfo(c.Structure):
    _fields_ = [('thread', PTR), ('tls', PTR), ('start', PTR)]


class DllInfo(c.Structure):
    _fields_ = [('file', PTR), ('base', PTR), ('offset', U32), ('size', U32),
                ('name', PTR), ('unicode', U16)]


class DebugUnion(c.Union):
    _fields_ = [('exception', ExceptionInfo), ('process', ProcessInfo), ('thread', ThreadInfo),
                ('exit_code', U32), ('dll_file', PTR), ('dll', DllInfo)]


class DebugEvent(c.Structure):
    _fields_ = [('code', U32), ('pid', U32), ('tid', U32), ('u', DebugUnion)]


class StartupInfo(c.Structure):
    _fields_ = [('size', U32), ('reserved', c.c_wchar_p), ('desktop', c.c_wchar_p), ('title', c.c_wchar_p)]
    _fields_ += [(n, U32) for n in ('x', 'y', 'width', 'height', 'xchars', 'ychars', 'fill', 'flags')]
    _fields_ += [('show', U16), ('reserved_size', U16), ('reserved_bytes', PTR),
                ('stdin', PTR), ('stdout', PTR), ('stderr', PTR)]


class CreatedProcess(c.Structure):
    _fields_ = [('process', PTR), ('thread', PTR), ('pid', U32), ('tid', U32)]


@dataclass(frozen=True)
class WatchPlan:
    club_index: int = 5
    seconds: int = 30
    max_events: int = 512

    def __post_init__(self):
        for value, lo, hi in ((self.club_index, 0, 4095), (self.seconds, 1, 60), (self.max_events, 1, 4096)):
            if type(value) is not int or not lo <= value <= hi:
                raise CapacityWatchError('Invalid bounded watch plan')

    def club_address(self, allocation: int, count: int) -> int:
        if type(allocation) is not int or type(count) is not int or not 0 < allocation < 2**32 or not self.club_index < count <= 4096:
            raise CapacityWatchError('Allocation/count does not qualify the selected array index')
        address = allocation + 4 + self.club_index * STRIDE
        if address + STRIDE > 2**32 or address % 4:
            raise CapacityWatchError('Invalid/alignment-overflow club address')
        return address


@dataclass(frozen=True)
class SupervisedWatchPlan(WatchPlan):
    """Separately human-approved five-minute run; ordinary CLI retains 60s limit."""
    seconds: int = 300
    max_events: int = 4096

    def __post_init__(self):
        WatchPlan(self.club_index, 60, self.max_events)
        if type(self.seconds) is not int or self.seconds != 300:
            raise CapacityWatchError('Supervised watch requires the exact approved five-minute bound')


def arm_writes(context: Wow64Context, club_address: int) -> None:
    if type(club_address) is not int or not 0 < club_address <= 2**32 - STRIDE or club_address % 4:
        raise CapacityWatchError('Invalid watch receiver')
    context.Dr0, context.Dr1 = (club_address + off for off in CAPACITY_OFFSETS)
    context.Dr2 = context.Dr3 = context.Dr6 = 0
    context.Dr7 = 0xDD0005  # local DR0/1, each RW=01(write), LEN=11(dword)


def write_watch_observation(context: Wow64Context, club_address: int) -> dict:
    """Read-back witness, not a claim of continuous/all-thread watch coverage."""
    registers = {name: int(getattr(context, name)) for name in ('Dr0', 'Dr1', 'Dr2', 'Dr3', 'Dr6', 'Dr7')}
    return dict(registers=registers,
                selected_capacity_watches_present=(
                    registers['Dr0'] == club_address + CAPACITY_OFFSETS[0]
                    and registers['Dr1'] == club_address + CAPACITY_OFFSETS[1]
                    and registers['Dr7'] & 0xFFFF00FF == 0xDD0005),
                continuous_all_thread_coverage_proven=False)


def all_thread_write_watch_readback(contexts: dict[int, Wow64Context], club_address: int) -> dict:
    """Exact suspended-event read-back across every debugger-owned live thread.

    This proves one debugger-event boundary only. Continuous coverage requires
    the runtime to perform this check before every ContinueDebugEvent from the
    allocation breakpoint through the selected uncontrolled read.
    """
    if (type(contexts) is not dict or not contexts
            or any(type(tid) is not int or type(ctx) is not Wow64Context
                   for tid, ctx in contexts.items())):
        raise CapacityWatchError('All-thread write-watch read-back requires exact live thread contexts')
    rows = []
    for tid in sorted(contexts):
        observed = write_watch_observation(contexts[tid], club_address)
        rows.append(dict(tid=tid, registers=observed['registers'],
                         selected_capacity_watches_present=observed['selected_capacity_watches_present']))
    return dict(thread_ids=[row['tid'] for row in rows], thread_count=len(rows),
                all_live_threads_armed=all(row['selected_capacity_watches_present'] for row in rows),
                per_thread=rows, continuous_all_thread_coverage_proven=False)


def finalize_user_thread_write_watch_coverage(coverage: dict, stop_debug_event_number: int) -> None:
    """Adjudicate the event-by-event user-mode coverage ledger at 0x5DA538."""
    if type(coverage) is not dict or type(stop_debug_event_number) is not int:
        raise CapacityWatchError('Invalid write-watch coverage ledger')
    start = coverage.get('start_debug_event_number')
    if type(start) is not int or stop_debug_event_number < start:
        raise CapacityWatchError('Write-watch coverage has no valid allocation start')
    expected = stop_debug_event_number - start + 1
    no_gap = bool(
        coverage.get('started') is True
        and coverage.get('broken') is False
        and coverage.get('checks') == expected
        and coverage.get('resumed_events_checked') == expected - 1
    )
    coverage.update(stop_debug_event_number=stop_debug_event_number,
                    expected_debug_events_through_read=expected,
                    debug_events_checked_without_gap=no_gap,
                    continuous_all_user_thread_write_watch_coverage_proven=no_gap,
                    kernel_or_external_writer_coverage_proven=False)


def attendance_receiver_observation(receiver: int, read) -> dict:
    """Actual ESI at qualified 5DA538; observed bytes are not report inputs."""
    vftable = struct.unpack('<I', read(receiver, 4))[0]
    if vftable != 0x7BD614:
        raise CapacityWatchError('Uncontrolled attendance receiver is not qualified DBRClub')
    return dict(address=receiver, vftable_u32=vftable,
                plus4_word_u16=struct.unpack('<H', read(receiver + 4, 2))[0],
                capacity_u32=list(struct.unpack('<II', read(receiver + 0x13C, 8))),
                capacity_initializer_proven=False, observation_not_runtime_input=True)


def startup_surface_return_observation(source_va: int, hresult: int, raw: bytes) -> dict:
    """Actual caller-local Lock output; never a patched result or pointer."""
    if (type(source_va) is not int or source_va not in STARTUP_SURFACE_RETURNS
            or type(raw) is not bytes or len(raw) != 108
            or type(hresult) is not int or not 0 <= hresult < 2**32):
        raise CapacityWatchError('Exact startup surface return and 108-byte descriptor required')
    size = struct.unpack_from('<I', raw)[0]
    surface = struct.unpack_from('<I', raw, 0x24)[0]
    return dict(source_va=source_va, hresult_u32=hresult,
                descriptor_stack_offset=STARTUP_SURFACE_RETURNS[source_va],
                descriptor_size_u32=size, caller_surface_u32=surface,
                caller_pitch_i32=struct.unpack_from('<i', raw, 0x10)[0],
                raw_descriptor=raw.hex(),
                diagnostic_stop_required=hresult != 0 or size != 108 or surface == 0,
                observation_only_no_result_or_surface_edit=True)


def window_presentation_adaptation(callsite: int, instruction: bytes, arguments: bytes) -> dict:
    """Authorized probe-only API argument adaptation, NEVER native game evidence."""
    if callsite != CREATE_WINDOW_CALL or instruction != CREATE_WINDOW_INSTRUCTION:
        raise CapacityWatchError('Presentation shim requires the exact qualified CreateWindowExA call')
    if type(arguments) is not bytes or len(arguments) != 48:
        raise CapacityWatchError('Presentation shim requires all twelve unchanged Win32 arguments')
    original = struct.unpack_from('<I', arguments)[0]
    modified = original & ~8
    return dict(source_va=callsite, original_dwExStyle=original, modified_dwExStyle=modified,
                original_dwStyle=struct.unpack_from('<I', arguments, 12)[0],
                changed_bits=original ^ modified, other_style_bits_unchanged=(original ^ modified) in (0, 8),
                applied=bool(original & 8), probe_only_compatibility_not_native_evidence=True)


def require_desktop_safety_qualification(executable: Path, receipt: Path | None) -> datetime | None:
    if receipt is None:
        raise CapacityWatchError('Original launch disabled: first qualify the exact non-exclusive display stage')
    require_private_output_path(receipt)
    stage = check_private_stage(executable.resolve().parent)
    data = json.loads(receipt.read_text(encoding='utf-8'))
    conditions = data.get('display_observation', {})
    until = None
    if data.get('approved_activation_windowed_qualification') is True:
        try:
            until = datetime.fromisoformat(data['activation_approval_expiry_utc'])
            validate_activation_approval(until)
        except (KeyError, TypeError, ValueError) as error:
            raise CapacityWatchError('Display receipt activation approval is missing/expired') from error
    allowed_problems = {'probe_took_foreground', 'probe_took_focus'} if until else set()
    window_observed = conditions.get('normal_window_observed') is True
    if data.get('qualification_mode') == DXGI_MODE:
        try:
            proof = windowed_dxgi_proof(data, data['dxgi_events'], data['dxgi_events_lost'])
            window_observed = proof == data['dxgi_windowed_proof']
        except (KeyError, TypeError, ValueError):
            raise CapacityWatchError('Loss-free exact-PID/HWND DXGI evidence missing')
    if (data.get('schema_version') != 4 or
            data.get('stop_reason') != 'display_qualification_complete' or
            data.get('display_qualification_only') is not True or
            data.get('activation_trace_only') is True or
            data.get('runtime_nonexclusive_qualified') is not True or
            data.get('source_sha256') != '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3' or
            data.get('private_stage') != str(executable.resolve().parent) or
            data.get('wrapper_sha256') != stage['wrapper_sha256'] or
            data.get('config_sha256') != stage['config_sha256'] or
            data.get('presentation_shim') != PRESENTATION_SHIM or
            data.get('presentation_shim_verified') is not True or
            data.get('private_wrapper_load_observed') is not True or
            data.get('native_graphics_initialization_accepted') is not True or
            not window_observed or
            not isinstance(conditions.get('problems'), list) or
            not set(conditions['problems']).issubset(allowed_problems)):
        raise CapacityWatchError('Display receipt does not qualify this exact private runtime stage')
    return until


def observe(executable: Path, output: Path, plan: WatchPlan, *, stop_at_entry: bool = False,
            calibrate_crt_writes: bool = False, display_receipt: Path | None = None) -> dict:
    if stop_at_entry and calibrate_crt_writes:
        raise CapacityWatchError('Entry-only and CRT write calibration are separate probes')
    until = require_desktop_safety_qualification(executable, display_receipt)
    return _observe(executable, output, plan, stop_at_entry=stop_at_entry,
                    calibrate_crt_writes=calibrate_crt_writes, activation_trace_until=until,
                    allow_approved_activation_qualification=until is not None)


def renew_display_activation_consent(executable: Path, previous: Path, output: Path, *,
                                    approved_until_utc: datetime) -> None:
    """New explicit HUMAN consent only; retain prior evidence, never overwrite it.

    Presentation facts/identity are unchanged, not relabeled as a new runtime
    observation. No CLI renewal/unsafe override: the caller must have new user
    approval for this exact scope/time, as the original consent has expired.
    """
    validate_activation_approval(approved_until_utc)
    require_private_output_path(previous)
    require_private_output_path(output)
    if output.exists():
        raise CapacityWatchError('Preserve prior private consent receipts')
    raw = previous.read_bytes()
    data = json.loads(raw)
    if data.get('approved_activation_windowed_qualification') is not True:
        raise CapacityWatchError('No qualified temporary-activation stage to renew')
    data['explicit_human_consent_renewal'] = dict(previous_receipt_sha256=sha256(raw).hexdigest(),
        previous_expiry_utc=data.get('activation_approval_expiry_utc'),
        new_expiry_utc=approved_until_utc.isoformat(),
        new_runtime_observation_claimed=False, no_other_safety_condition_changed=True)
    data['activation_approval_expiry_utc'] = approved_until_utc.isoformat()
    output.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    # Re-adjudicate all actual mode evidence and exact current stage identity.
    # Failed/partial original receipts NEVER gain qualification by renewal.
    require_desktop_safety_qualification(executable, output)


def observe_supervised(executable: Path, output: Path, *, display_receipt: Path,
                       approved_until_utc: datetime, club_index: int = 5) -> dict:
    validate_activation_approval(approved_until_utc)
    until = require_desktop_safety_qualification(executable, display_receipt)
    if until != approved_until_utc or until - datetime.now(timezone.utc) < timedelta(seconds=300):
        raise CapacityWatchError('Exact explicit consent must cover the five-minute supervised watch')
    result = observe(executable, output, SupervisedWatchPlan(club_index=club_index),
                     display_receipt=display_receipt)
    result['supervised_human_operated'] = True
    output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result


def trace_startup_surface_returns(executable: Path, output: Path, *, display_receipt: Path) -> dict:
    """Separately approved <=60s diagnostic; no capacity or GUI interaction."""
    until = require_desktop_safety_qualification(executable, display_receipt)
    if until is None or until - datetime.now(timezone.utc) < timedelta(seconds=60):
        raise CapacityWatchError('Live activation consent must cover the complete surface diagnostic')
    return _observe(executable, output, WatchPlan(seconds=60, max_events=4096),
                    activation_trace_until=until, allow_approved_activation_qualification=True,
                    startup_surface_trace_only=True)


def qualify_windowed_display(executable: Path, output: Path) -> dict:
    """Daniel-authorized smallest bounded original display probe, not a bypass."""
    return _observe(executable, output, WatchPlan(seconds=10, max_events=256), qualification_only=True)


def validate_activation_approval(approved_until_utc: datetime) -> None:
    now = datetime.now(timezone.utc)
    if (not isinstance(approved_until_utc, datetime) or approved_until_utc.utcoffset() != timedelta(0)
            or not now < approved_until_utc <= now + timedelta(hours=1)):
        raise CapacityWatchError('Live, UTC, at-most-one-hour human activation approval required')


def qualify_windowed_during_approved_activation(executable: Path, output: Path, *, approved_until_utc: datetime) -> dict:
    """Explicitly approved temporary foreground condition; no added game/API shim."""
    validate_activation_approval(approved_until_utc)
    return _observe(executable, output, WatchPlan(seconds=10, max_events=256), qualification_only=True,
                    activation_trace_until=approved_until_utc, allow_approved_activation_qualification=True)


def trace_window_activation(executable: Path, output: Path, *, approved_until_utc: datetime) -> dict:
    """Separately user-approved observation; can NEVER qualify a display receipt.

    No CLI safety override. Caller must hold live human approval for transient
    activation; timestamp is bounded to an hour and retained in the private receipt.
    All non-activation safety conditions and pre-call stops remain mandatory.
    """
    validate_activation_approval(approved_until_utc)
    return _observe(executable, output, WatchPlan(seconds=10, max_events=256),
                    qualification_only=True, activation_trace_until=approved_until_utc)


def _observe(executable: Path, output: Path, plan: WatchPlan, *, stop_at_entry: bool = False,
             calibrate_crt_writes: bool = False, qualification_only: bool = False,
             activation_trace_until: datetime | None = None,
             allow_approved_activation_qualification: bool = False,
             startup_surface_trace_only: bool = False) -> dict:
    if startup_surface_trace_only and (qualification_only or stop_at_entry or calibrate_crt_writes
                                      or plan.seconds != 60 or plan.max_events != 4096):
        raise CapacityWatchError('Surface diagnostic is a separate fixed 60s/4096-event mode')
    if allow_approved_activation_qualification and activation_trace_until is None:
        raise CapacityWatchError('Temporary activation qualification needs live human approval')
    if activation_trace_until is not None:
        validate_activation_approval(activation_trace_until)
    if activation_trace_until is not None and not allow_approved_activation_qualification and (
            not qualification_only or stop_at_entry or calibrate_crt_writes
            or plan.seconds != 10 or plan.max_events != 256):
        raise CapacityWatchError('Activation observation is separate from all capacity/calibration modes')
    require_private_output_path(output)
    require_private_output_path(executable)
    stage = check_private_stage(executable.resolve().parent)
    pe = OriginalPE32.parse(executable.read_bytes())
    if pe.read(CREATE_WINDOW_CALL, 6) != CREATE_WINDOW_INSTRUCTION:
        raise CapacityWatchError('Canonical presentation callsite instruction mismatch')
    if os.name != 'nt' or c.sizeof(PTR) != 8:
        raise CapacityWatchError('Requires 64-bit Windows Python and a WOW64 original process')
    if c.sizeof(Wow64Context) != 716 or c.sizeof(DebugEvent) != 176:
        raise CapacityWatchError('Unexpected Windows debugger ABI layout')
    pe_offset = struct.unpack_from('<I', pe.data, 0x3C)[0]
    entry = pe.image_base + struct.unpack_from('<I', pe.data, pe_offset + 24 + 16)[0]
    if startup_surface_trace_only:
        for address in STARTUP_SURFACE_RETURNS:
            if pe.read(address - 3, 3) != bytes.fromhex('ff5164'):
                raise CapacityWatchError('Canonical surface Lock return instruction mismatch')
    sites = ((entry, *STARTUP_SITES, *STARTUP_SURFACE_RETURNS) if startup_surface_trace_only else
             (entry, *STARTUP_SITES) if qualification_only else
             (entry, *STARTUP_SITES, ALLOC_RETURN, CONSTRUCTED, IMPORTED, UNCONTROLLED_READ))
    originals = {va: pe.read(va, 1) for va in sites}
    k = c.WinDLL('kernel32', use_last_error=True)
    signatures = {
        'CreateProcessW': ([c.c_wchar_p, c.c_wchar_p, PTR, PTR, c.c_int, U32, PTR, c.c_wchar_p,
                            c.POINTER(StartupInfo), c.POINTER(CreatedProcess)], c.c_int),
        'WaitForDebugEvent': ([c.POINTER(DebugEvent), U32], c.c_int),
        'ContinueDebugEvent': ([U32, U32, U32], c.c_int),
        'ReadProcessMemory': ([PTR, PTR, PTR, c.c_size_t, c.POINTER(c.c_size_t)], c.c_int),
        'WriteProcessMemory': ([PTR, PTR, PTR, c.c_size_t, c.POINTER(c.c_size_t)], c.c_int),
        'FlushInstructionCache': ([PTR, PTR, c.c_size_t], c.c_int),
        'Wow64GetThreadContext': ([PTR, c.POINTER(Wow64Context)], c.c_int),
        'Wow64SetThreadContext': ([PTR, c.POINTER(Wow64Context)], c.c_int),
        'TerminateProcess': ([PTR, U32], c.c_int), 'CloseHandle': ([PTR], c.c_int),
        'SuspendThread': ([PTR], U32),
        'GetFinalPathNameByHandleW': ([PTR, c.c_wchar_p, U32, U32], U32),
    }
    for name, (args, result) in signatures.items():
        function = getattr(k, name)
        function.argtypes, function.restype = args, result

    def checked(result):
        if not result:
            raise c.WinError(c.get_last_error())

    display = DisplayWatch()  # baseline before the child can run; read-only APIs
    created, startup = CreatedProcess(), StartupInfo()
    startup.size, startup.flags, startup.show = c.sizeof(startup), 1, 0  # STARTF_USESHOWWINDOW / SW_HIDE
    checked(k.CreateProcessW(str(executable.resolve()), None, None, None, False, 2, None,
                             str(executable.resolve().parent), c.byref(startup), c.byref(created)))
    report = dict(schema_version=4, source_sha256=pe.sha256, club_array_index=plan.club_index,
                  capacity_initializer_proven=False, gate13_closed=False, events=[],
                  allocation_observed=False, uncontrolled_read_observed=False,
                  selected_club_import_observed=False,
                  observation_not_runtime_input=True, process_id=created.pid,
                  display_qualification_only=qualification_only,
                  startup_surface_trace_only=startup_surface_trace_only,
                  activation_trace_only=activation_trace_until is not None and not allow_approved_activation_qualification,
                  approved_activation_windowed_qualification=allow_approved_activation_qualification,
                  activation_approval_expiry_utc=activation_trace_until.isoformat() if activation_trace_until else None,
                  private_stage=str(executable.resolve().parent),
                  wrapper_sha256=stage['wrapper_sha256'], config_sha256=stage['config_sha256'],
                  private_wrapper_load_observed=False, native_graphics_initialization_accepted=False,
                  presentation_shim=PRESENTATION_SHIM, presentation_shim_verified=False,
                  presentation_adaptations=[],
                  write_watch_coverage=dict(
                      started=False, broken=False, checks=0, resumed_events_checked=0,
                      new_thread_events_armed=0,
                      continuous_all_user_thread_write_watch_coverage_proven=False,
                      kernel_or_external_writer_coverage_proven=False,
                      debugger_event_suspension_contract=(
                          'all process threads suspended until ContinueDebugEvent'),
                      create_thread_pre_user_mode_execution_contract=True,
                      checkpoints=[]),
                  runtime_nonexclusive_qualified=False, audio_condition='user_managed_volume_mixer')
    if calibrate_crt_writes:
        report['crt_write_watch_calibration_only'] = True
        report['crt_write_watch_calibration_complete'] = False
        report['crt_write_watch_post_instruction_vas'] = []
    threads, pending = {}, {}
    club, event_count, exited = None, 0, False
    started = time.monotonic()

    def read(address, size):
        buffer, done = c.create_string_buffer(size), c.c_size_t()
        checked(k.ReadProcessMemory(created.process, address, buffer, size, c.byref(done)))
        if done.value != size:
            raise CapacityWatchError('Short private memory read')
        return buffer.raw

    def write(address, data, *, instruction=True):
        buffer, done = c.create_string_buffer(data), c.c_size_t()
        checked(k.WriteProcessMemory(created.process, address, buffer, len(data), c.byref(done)))
        if done.value != len(data):
            raise CapacityWatchError('Short breakpoint write')
        if instruction:
            checked(k.FlushInstructionCache(created.process, address, len(data)))

    def context(tid):
        ctx = Wow64Context()
        ctx.ContextFlags = CONTEXT_FLAGS
        checked(k.Wow64GetThreadContext(threads[tid], c.byref(ctx)))
        return ctx

    def set_context(tid, ctx):
        checked(k.Wow64SetThreadContext(threads[tid], c.byref(ctx)))

    def verify_write_watch_coverage(stage, event, *, will_resume):
        if club is None or exited:
            return
        contexts = {tid: context(tid) for tid in sorted(threads)}
        observed = all_thread_write_watch_readback(contexts, club)
        observed.update(stage=stage, debug_event_number=event_count,
                        debug_event_code=int(event.code), debug_event_tid=int(event.tid),
                        will_resume=bool(will_resume))
        coverage = report['write_watch_coverage']
        coverage['checks'] += 1
        coverage['last_debug_event_number'] = event_count
        if will_resume:
            coverage['resumed_events_checked'] += 1
        retain = (
            coverage['checks'] == 1
            or int(event.code) == 2
            or not observed['all_live_threads_armed']
            or stage in ('constructor_return', 'selected_import_return',
                         'selected_uncontrolled_read', 'hardware_write_trap')
        )
        if retain:
            coverage['checkpoints'].append(observed)
        if not observed['all_live_threads_armed']:
            coverage['broken'] = True
            raise CapacityWatchError(
                'Capacity write-watch coverage lost before target-process continuation')

    def snapshot(kind, tid, ctx, **extra):
        row = dict(kind=kind, tid=tid, registers={n: int(getattr(ctx, n)) for n in
                   ('Eip', 'Eax', 'Ebx', 'Ecx', 'Edx', 'Esi', 'Edi', 'Esp', 'Ebp', 'Dr6')}, **extra)
        row['x87_control_word'] = struct.unpack('<I', bytes(ctx.FloatSave[:4]))[0]
        if kind == 'source_breakpoint' and extra.get('source_va') == UNCONTROLLED_READ:
            # Record the actual source-qualified attendance receiver, not just
            # the separately hardware-watched array member. These read values
            # are observations, never initialization or producer semantics.
            row['attendance_receiver'] = attendance_receiver_observation(int(ctx.Esi), read)
        if club is not None:
            row.update(club_address=club, observed_club_plus4_word_u16=struct.unpack('<H', read(club + 4, 2))[0],
                       identity_import_observed=report['selected_club_import_observed'],
                       visiting_capacity_u32=list(struct.unpack('<II', read(club + 0x13C, 8))),
                       write_watch_observation=write_watch_observation(ctx, club))
        report['events'].append(row)

    try:
        while time.monotonic() - started < plan.seconds and event_count < plan.max_events:
            if activation_trace_until and datetime.now(timezone.utc) >= activation_trace_until:
                raise CapacityWatchError('Human activation approval expired')
            try:
                display.check(created.pid)
            except DisplayWatchError:
                if (activation_trace_until is None or not display.problems
                        or not set(display.problems).issubset({'probe_took_foreground', 'probe_took_focus'})):
                    raise
                display.record_normal_window(created.pid)
                observations = report.setdefault('approved_activation_observations', [])
                if len(observations) < 64 and (not observations or observations[-1]['debug_events_processed'] != event_count):
                    observations.append(dict(debug_events_processed=event_count,
                        foreground_pid=display.last['foreground_pid'], focus_pid=display.last.get('focus_pid'),
                        observed_problems=list(display.problems)))
            display_ready = (display.ready() if activation_trace_until is None else
                allow_approved_activation_qualification and display.normal_window_ready() and
                set(display.problems).issubset({'probe_took_foreground', 'probe_took_focus'}))
            if (qualification_only and display_ready and report['private_wrapper_load_observed']
                    and report['native_graphics_initialization_accepted'] and report['presentation_shim_verified']):
                report['stop_reason'] = 'display_qualification_complete'
                break
            event = DebugEvent()
            if not k.WaitForDebugEvent(c.byref(event), 100):
                if c.get_last_error() != 121:  # ERROR_SEM_TIMEOUT
                    checked(False)
                continue
            event_count += 1
            continuation, stop = 0x10002, False  # DBG_CONTINUE
            coverage_stage = f'debug_event_{int(event.code)}'
            try:
                if event.code == 3:
                    info = event.u.process
                    threads[event.tid] = info.thread
                    if info.file:
                        k.CloseHandle(info.file)
                    if info.base != pe.image_base:
                        raise CapacityWatchError('Relocated image: fixed source VA probes rejected')
                    for va in sites:
                        if read(va, 1) != originals[va]:
                            raise CapacityWatchError('Loaded code differs from checksum-qualified source')
                        write(va, b'\xCC')
                elif event.code == 2:
                    coverage_stage = 'create_thread'
                    threads[event.tid] = event.u.thread.thread
                    if club is not None:
                        ctx = context(event.tid)
                        arm_writes(ctx, club)
                        set_context(event.tid, ctx)
                        report['write_watch_coverage']['new_thread_events_armed'] += 1
                elif event.code == 4:
                    coverage_stage = 'exit_thread'
                    threads.pop(event.tid, None)
                    pending.pop(event.tid, None)
                elif event.code == 6 and event.u.dll_file:
                    buffer = c.create_unicode_buffer(32768)
                    length = k.GetFinalPathNameByHandleW(event.u.dll_file, buffer, len(buffer), 0)
                    if 0 < length < len(buffer):
                        loaded = Path(buffer.value.removeprefix('\\\\?\\')).resolve()
                        report.setdefault('private_loaded_modules', []).append(dict(
                            base=int(event.u.dll.base), path=str(loaded)))
                        if loaded == executable.resolve().parent / 'DDraw.dll':
                            report['private_wrapper_load_observed'] = True
                    k.CloseHandle(event.u.dll_file)
                elif event.code == 5:
                    exited, stop = True, True
                    report['stop_reason'] = 'native_process_exit'
                    report['exit_code'] = int(event.u.exit_code)
                elif event.code == 1:
                    exception = event.u.exception
                    code, address = int(exception.record.code), exception.record.address
                    if code in (0x80000003, 0x4000001F) and address in originals:
                        ctx = context(event.tid)
                        coverage_stage = f'source_breakpoint_{int(address):08x}'
                        if address == CONSTRUCTED:
                            coverage_stage = 'constructor_return'
                        if address == IMPORTED and ctx.Ebx == plan.club_index:
                            coverage_stage = 'selected_import_return'
                        if address == IMPORTED and ctx.Ebx == plan.club_index:
                            if club is None or struct.unpack('<I', read(club, 4))[0] != 0x7BD614:
                                raise CapacityWatchError('Selected import has no qualified DBRClub vftable')
                            report['selected_club_import_observed'] = True
                        if address != IMPORTED or ctx.Ebx == plan.club_index:
                            snapshot('source_breakpoint', event.tid, ctx, source_va=address)
                        if startup_surface_trace_only and address in STARTUP_SURFACE_RETURNS:
                            observed = startup_surface_return_observation(address, int(ctx.Eax),
                                read(ctx.Esp + STARTUP_SURFACE_RETURNS[address], 108))
                            observed.update(tid=int(event.tid), debug_event_number=event_count)
                            report.setdefault('startup_surface_call_returns', []).append(observed)
                            if observed['diagnostic_stop_required']:
                                # Terminate while suspended before native copy; never
                                # manufacture success, restore a surface or edit a pointer.
                                report['stop_reason'], stop = 'startup_surface_return_guard', True
                        if address == 0x515C11:
                            # Exact RegOpenKeyExA argument from the source-qualified
                            # call site. Record the actual key, not a guessed install path.
                            report['native_install_key_hklm'] = read(ctx.Eax, 256).split(b'\0', 1)[0].decode('latin1')
                        if address == 0x515C17:
                            report['native_install_key_open_result'] = int(ctx.Eax)
                        if address in INSTALL_QUERY_RETURNS:
                            report.setdefault('native_install_query_results', {})[INSTALL_QUERY_RETURNS[address]] = int(ctx.Eax)
                            if address in RESOURCE_SELECTOR_RETURNS and ctx.Eax == 0:
                                # Source call arguments: size +10, DWORD payload +14,
                                # returned registry type +18. No defaults on failure.
                                size, value, registry_type = struct.unpack('<III', read(ctx.Esp + 0x10, 12))
                                report.setdefault('native_resource_selectors', {})[INSTALL_QUERY_RETURNS[address]] = dict(
                                    size=size, value=value, registry_type=registry_type)
                        if address == 0x530DD9:
                            report['native_install_setup_accepted'] = bool(ctx.Eax & 0xFF)
                        if address == GRAPHICS_SUCCESS:
                            # 61539E writes AL=1 immediately before this successful
                            # 615180 return. 6151B5 is a software-renderer query,
                            # NOT graphics startup acceptance.
                            report['native_graphics_initialization_accepted'] = (ctx.Eax & 0xFF) == 1
                        if address == CREATE_WINDOW_CALL:
                            # Only the qualified API argument on this suspended
                            # thread's stack is adapted. Fullscreen/game globals,
                            # disk code, simulation/capacity and other calls stay intact.
                            instruction = originals[address] + read(address + 1, 5)
                            arguments = read(ctx.Esp, 48)
                            adaptation = window_presentation_adaptation(address, instruction, arguments)
                            report['presentation_adaptations'].append(adaptation)
                            if adaptation['applied']:
                                write(ctx.Esp, struct.pack('<I', adaptation['modified_dwExStyle']), instruction=False)
                            after = read(ctx.Esp, 48)
                            adaptation['other_api_arguments_unchanged'] = after[4:] == arguments[4:]
                            adaptation['write_readback_verified'] = after == (
                                struct.pack('<I', adaptation['modified_dwExStyle']) + arguments[4:])
                            if not adaptation['write_readback_verified']:
                                report['stop_reason'], stop = 'presentation_shim_readback_failed', True
                            else:
                                report['presentation_shim_verified'] = True
                        if address == FOREGROUND_REQUEST:
                            # Independent source-proven presentation request;
                            # record and STOP, never suppress/fake its return.
                            report['native_foreground_request'] = dict(source_va=address,
                                requested_hwnd=struct.unpack('<I', read(ctx.Esp, 4))[0],
                                api_execution_permitted_by_live_approval=allow_approved_activation_qualification)
                            if not allow_approved_activation_qualification:
                                report['stop_reason'], stop = 'native_foreground_request_guard', True
                        if address == FOREGROUND_RETURN:
                            report['native_foreground_call_result'] = int(ctx.Eax)
                        if address == WINDOW_CREATED:
                            report.setdefault('native_window_creation_returns', []).append(dict(
                                source_va=address, returned_hwnd=int(ctx.Eax)))
                        if address == 0x50D630:
                            report['native_fresh_world_loader_observed'] = True
                        if address == 0x461F31:
                            # Aligned native caller: path/flags/callback arguments
                            # are already pushed, before 461900. Observe only.
                            path_address = struct.unpack('<I', read(ctx.Esp, 4))[0]
                            report['native_startup_movie_requested_path'] = read(path_address, 260).split(b'\0', 1)[0].decode('latin1')
                        if address == 0x461F36:
                            report['native_startup_movie_return_observed'] = True
                        if address == 0x6154CC:
                            report['native_renderer_wait_call'] = dict(source_va=address,
                                receiver=int(ctx.Eax), vftable=int(ctx.Ecx),
                                actual_target=struct.unpack('<I', read(ctx.Ecx + 0x58, 4))[0],
                                arguments=list(struct.unpack('<3I', read(ctx.Esp, 12))))
                            if report.get('native_root_redraw_call_observed'):
                                report['native_root_redraw_wait_call'] = dict(report['native_renderer_wait_call'])
                        if address == 0x6154CF:
                            report['native_renderer_wait_first_return'] = int(ctx.Eax)
                            if report.get('native_root_redraw_call_observed'):
                                report['native_root_redraw_wait_return'] = int(ctx.Eax)
                        if address == 0x531092:
                            report['native_database_setup_return_observed'] = True
                        if address == 0x5310B7:
                            report['native_5327e0_call_observed'] = True
                        if address == 0x5310BC:
                            report['native_5327e0_return_observed'] = True
                        if address == 0x53120A:
                            report['native_root_redraw_call_observed'] = True
                            # Separate the original first root redraw from movie
                            # frame waits. Re-arm only the observational probes.
                            for site in ONE_SHOT_SITES:
                                write(site, b'\xCC')
                        if address == 0x53120F:
                            report['native_root_redraw_return_observed'] = True
                        if address in (0x6A93FB, 0x6A941E):
                            report.setdefault('native_driver_load_results', []).append(dict(
                                source_va=address, handle=int(ctx.Eax),
                                requested_driver=read(ctx.Esi, 128).split(b'\0', 1)[0].decode('latin1')))
                        if address == ALLOC_RETURN:
                            if club is not None:
                                raise CapacityWatchError('Second array allocation: lifecycle scope exhausted')
                            coverage_stage = 'allocation_return'
                            club = plan.club_address(ctx.Eax, ctx.Esi)
                            report['allocation_observed'] = True
                            coverage = report['write_watch_coverage']
                            coverage['started'] = True
                            coverage['start_debug_event_number'] = event_count
                            coverage['allocation_thread_ids'] = sorted(threads)
                            for tid in threads:
                                target = ctx if tid == event.tid else context(tid)
                                arm_writes(target, club)
                                set_context(tid, target)
                            snapshot('allocation_before_constructor', event.tid, ctx, count=int(ctx.Esi))
                        if address == UNCONTROLLED_READ and ctx.Esi == club:
                            coverage_stage = 'selected_uncontrolled_read'
                            report['uncontrolled_read_observed'] = True
                            report['stop_reason'], stop = 'selected_club_uncontrolled_read', True
                        if address == entry and stop_at_entry:
                            report['stop_reason'], stop = 'entry_calibration_only', True
                        if address == entry and calibrate_crt_writes:
                            # Known CRT global MOV writes at 66AAF7/66AB05 are
                            # positive controls for hardware watch delivery, NOT
                            # DBRClub receivers or visiting-capacity producers.
                            ctx.Dr0, ctx.Dr1 = 0x9FAC00, 0x9FABFC
                            ctx.Dr2 = ctx.Dr3 = ctx.Dr6 = 0
                            ctx.Dr7 = 0xDD0005
                        write(address, originals[address])
                        ctx.Eip, ctx.EFlags = address, ctx.EFlags | 0x100
                        # Stop observing every other imported club after the selected
                        # slot. Hardware writes stay armed throughout the lifecycle.
                        if address not in ONE_SHOT_SITES and (address != IMPORTED or ctx.Ebx != plan.club_index):
                            pending[event.tid] = address
                        else:
                            ctx.EFlags &= ~0x100
                        set_context(event.tid, ctx)
                    elif code in (0x80000004, 0x4000001E):
                        ctx = context(event.tid)
                        coverage_stage = 'single_step'
                        if ctx.Dr6 & 3:
                            coverage_stage = 'hardware_write_trap'
                            snapshot('hardware_dword_write_after_instruction', event.tid, ctx,
                                     preceding_bytes_not_decoded=read(ctx.Eip - 16, 16).hex())
                            if calibrate_crt_writes:
                                report['crt_write_watch_post_instruction_vas'].append(int(ctx.Eip))
                                if report['crt_write_watch_post_instruction_vas'] == [0x66AAFD, 0x66AB0B]:
                                    report['crt_write_watch_calibration_complete'] = True
                                    report['stop_reason'], stop = 'crt_write_watch_calibration_complete', True
                        rearm = pending.pop(event.tid, None)
                        if rearm is not None:
                            write(rearm, b'\xCC')
                            ctx.EFlags &= ~0x100
                        ctx.Dr6 = 0
                        set_context(event.tid, ctx)
                    elif code not in (0x80000003, 0x4000001F):
                        report['events'].append(dict(kind='native_exception', code=code,
                                                     address=address, first_chance=int(exception.first_chance),
                                                     information=[int(exception.record.information[i]) for i in
                                                                  range(min(int(exception.record.count), 15))]))
                        ctx = context(event.tid)
                        snapshot('native_exception_context', event.tid, ctx,
                                 stack_dwords=list(struct.unpack('<64I', read(ctx.Esp, 256))))
                        continuation = 0x80010001  # DBG_EXCEPTION_NOT_HANDLED
                        if not exception.first_chance:
                            report['stop_reason'], stop = 'unhandled_native_exception', True
                if club is not None and not exited:
                    verify_write_watch_coverage(coverage_stage, event, will_resume=not stop)
                    if stop and report.get('stop_reason') == 'selected_club_uncontrolled_read':
                        finalize_user_thread_write_watch_coverage(
                            report['write_watch_coverage'], event_count)
            except (OSError, CapacityWatchError, ProbeSafetyError, DisplayWatchError):
                stop = True
                raise
            finally:
                # Terminate while the debug event still suspends the child;
                # never resume a source-proven unsafe window request first.
                if stop and not exited:
                    checked(k.TerminateProcess(created.process, 0xE013))
                checked(k.ContinueDebugEvent(event.pid, event.tid, continuation))
            if stop:
                break
        report.setdefault('stop_reason', 'event_bound' if event_count >= plan.max_events else 'time_bound')
        if report['stop_reason'] == 'time_bound' and not exited and created.tid in threads:
            # One terminal diagnostic only: suspend the owned main thread, read
            # registers/stack, then terminate in finally. Never alter its state
            # or resume it to manufacture native progress.
            prior = k.SuspendThread(threads[created.tid])
            if prior == 0xFFFFFFFF:
                checked(False)
            ctx = context(created.tid)
            snapshot('terminal_suspended_main_thread', created.tid, ctx,
                observation_only_terminated_not_resumed=True,
                stack_dwords=list(struct.unpack('<64I', read(ctx.Esp, 256))))
    except (OSError, CapacityWatchError, ProbeSafetyError, DisplayWatchError) as error:
        report['stop_reason'], report['error'] = 'probe_error', str(error)
    finally:
        if not exited:
            k.TerminateProcess(created.process, 0xE013)
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                event = DebugEvent()
                if not k.WaitForDebugEvent(c.byref(event), 100):
                    continue
                if event.code == 6 and event.u.dll_file:
                    k.CloseHandle(event.u.dll_file)
                k.ContinueDebugEvent(event.pid, event.tid, 0x10002)
                if event.code == 5:
                    break
        k.CloseHandle(created.thread)
        k.CloseHandle(created.process)
        try:
            display.check(created.pid)
        except DisplayWatchError as error:
            if (activation_trace_until is None or not display.problems or
                    not set(display.problems).issubset({'probe_took_foreground', 'probe_took_focus'})):
                report['stop_reason'], report['error'] = 'display_safety_stop', str(error)
        report['display_observation'] = display.receipt()
        report['runtime_nonexclusive_qualified'] = bool(
            qualification_only and not report['activation_trace_only'] and report['stop_reason'] == 'display_qualification_complete'
            and display.normal_window_ready() and report['private_wrapper_load_observed']
            and report['native_graphics_initialization_accepted'] and report['presentation_shim_verified'])
        if activation_trace_until and datetime.now(timezone.utc) >= activation_trace_until:
            report['runtime_nonexclusive_qualified'] = False
            report['stop_reason'] = 'activation_approval_expired'
        report.update(debug_events=event_count, elapsed_seconds=round(time.monotonic() - started, 3))
        output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original_executable', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--club-index', type=int, default=5)
    parser.add_argument('--seconds', type=int, default=30)
    parser.add_argument('--max-events', type=int, default=512)
    parser.add_argument('--stop-at-entry', action='store_true')
    parser.add_argument('--calibrate-crt-writes', action='store_true')
    parser.add_argument('--qualify-display', action='store_true', help='Separate ten-second display-only probe; audio user-managed')
    parser.add_argument('--display-receipt', type=Path, help='Private exact-stage successful windowed qualification receipt')
    args = parser.parse_args()
    if args.qualify_display:
        if args.stop_at_entry or args.calibrate_crt_writes or args.display_receipt:
            parser.error('Display qualification cannot be combined with other launch modes')
        result = qualify_windowed_display(args.original_executable, args.output)
    else:
        result = observe(args.original_executable, args.output,
                     WatchPlan(args.club_index, args.seconds, args.max_events), stop_at_entry=args.stop_at_entry,
                     calibrate_crt_writes=args.calibrate_crt_writes, display_receipt=args.display_receipt)
    print(json.dumps({key: result[key] for key in ('stop_reason', 'allocation_observed',
          'uncontrolled_read_observed', 'capacity_initializer_proven', 'debug_events')}))
    if args.qualify_display:
        return 0 if result['runtime_nonexclusive_qualified'] else 2
    return 2 if result['stop_reason'] in ('probe_error', 'display_safety_stop',
                    'native_foreground_request_guard', 'presentation_shim_readback_failed') else 0


if __name__ == '__main__':
    raise SystemExit(main())
