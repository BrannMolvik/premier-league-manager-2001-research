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
from dataclasses import dataclass
import json
import os
from pathlib import Path
import struct
import time

from gate13_button_source_trace import OriginalPE32, OriginalPETraceError, require_private_output_path
from gate13_native_probe_safety import check_private_stage, ProbeSafetyError
from gate13_native_display_watch import DisplayWatch, DisplayWatchError

U32, U16, PTR = c.c_uint32, c.c_uint16, c.c_void_p
CONTEXT_FLAGS = 0x1001F  # WOW64 control/integer/segments/FPU/debug registers
ALLOC_RETURN, CONSTRUCTED, IMPORTED, UNCONTROLLED_READ = 0x40BC14, 0x40BC43, 0x40BA2C, 0x5DA538
STRIDE, CAPACITY_OFFSETS = 0x2A8, (0x13C, 0x140)
GRAPHICS_SUCCESS, CREATE_WINDOW_CALL = 0x6153A0, 0x6A6363
STARTUP_SITES = (0x66AB26, 0x66AB37, 0x66AB74, 0x530DAB, 0x530DD9, 0x66ABA7, 0x66ABF4,
                 0x515C11, 0x515C17, 0x53078D, 0x5307F8, 0x53085F,
                 0x53093A, 0x5309DC, 0x530A79, 0x50D630,
                 0x530E29, 0x530E47, 0x615188, GRAPHICS_SUCCESS, CREATE_WINDOW_CALL, 0x6A93FB, 0x6A941E,
                 0x530EEE, 0x530F02, 0x530F3B, 0x530F9E)
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


class DebugUnion(c.Union):
    _fields_ = [('exception', ExceptionInfo), ('process', ProcessInfo), ('thread', ThreadInfo),
                ('exit_code', U32), ('dll_file', PTR)]


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


def arm_writes(context: Wow64Context, club_address: int) -> None:
    if type(club_address) is not int or not 0 < club_address <= 2**32 - STRIDE or club_address % 4:
        raise CapacityWatchError('Invalid watch receiver')
    context.Dr0, context.Dr1 = (club_address + off for off in CAPACITY_OFFSETS)
    context.Dr2 = context.Dr3 = context.Dr6 = 0
    context.Dr7 = 0xDD0005  # local DR0/1, each RW=01(write), LEN=11(dword)


def require_desktop_safety_qualification(executable: Path, receipt: Path | None) -> None:
    if receipt is None:
        raise CapacityWatchError('Original launch disabled: first qualify the exact non-exclusive display stage')
    require_private_output_path(receipt)
    stage = check_private_stage(executable.resolve().parent)
    data = json.loads(receipt.read_text(encoding='utf-8'))
    if (data.get('schema_version') != 2 or
            data.get('stop_reason') != 'display_qualification_complete' or
            data.get('display_qualification_only') is not True or
            data.get('runtime_nonexclusive_qualified') is not True or
            data.get('source_sha256') != '833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3' or
            data.get('private_stage') != str(executable.resolve().parent) or
            data.get('wrapper_sha256') != stage['wrapper_sha256'] or
            data.get('config_sha256') != stage['config_sha256'] or
            data.get('private_wrapper_load_observed') is not True or
            data.get('native_graphics_initialization_accepted') is not True or
            data.get('display_observation', {}).get('normal_window_observed') is not True or
            data.get('display_observation', {}).get('problems') != []):
        raise CapacityWatchError('Display receipt does not qualify this exact private runtime stage')


def observe(executable: Path, output: Path, plan: WatchPlan, *, stop_at_entry: bool = False,
            calibrate_crt_writes: bool = False, display_receipt: Path | None = None) -> dict:
    if stop_at_entry and calibrate_crt_writes:
        raise CapacityWatchError('Entry-only and CRT write calibration are separate probes')
    require_desktop_safety_qualification(executable, display_receipt)
    return _observe(executable, output, plan, stop_at_entry=stop_at_entry,
                    calibrate_crt_writes=calibrate_crt_writes)


def qualify_windowed_display(executable: Path, output: Path) -> dict:
    """Daniel-authorized smallest bounded original display probe, not a bypass."""
    return _observe(executable, output, WatchPlan(seconds=10, max_events=256), qualification_only=True)


def _observe(executable: Path, output: Path, plan: WatchPlan, *, stop_at_entry: bool = False,
             calibrate_crt_writes: bool = False, qualification_only: bool = False) -> dict:
    require_private_output_path(output)
    require_private_output_path(executable)
    stage = check_private_stage(executable.resolve().parent)
    pe = OriginalPE32.parse(executable.read_bytes())
    if os.name != 'nt' or c.sizeof(PTR) != 8:
        raise CapacityWatchError('Requires 64-bit Windows Python and a WOW64 original process')
    if c.sizeof(Wow64Context) != 716 or c.sizeof(DebugEvent) != 176:
        raise CapacityWatchError('Unexpected Windows debugger ABI layout')
    pe_offset = struct.unpack_from('<I', pe.data, 0x3C)[0]
    entry = pe.image_base + struct.unpack_from('<I', pe.data, pe_offset + 24 + 16)[0]
    sites = ((entry, *STARTUP_SITES) if qualification_only else
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
    report = dict(schema_version=2, source_sha256=pe.sha256, club_array_index=plan.club_index,
                  capacity_initializer_proven=False, gate13_closed=False, events=[],
                  allocation_observed=False, uncontrolled_read_observed=False,
                  selected_club_import_observed=False,
                  observation_not_runtime_input=True, process_id=created.pid,
                  display_qualification_only=qualification_only,
                  private_stage=str(executable.resolve().parent),
                  wrapper_sha256=stage['wrapper_sha256'], config_sha256=stage['config_sha256'],
                  private_wrapper_load_observed=False, native_graphics_initialization_accepted=False,
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

    def write(address, data):
        buffer, done = c.create_string_buffer(data), c.c_size_t()
        checked(k.WriteProcessMemory(created.process, address, buffer, len(data), c.byref(done)))
        if done.value != len(data):
            raise CapacityWatchError('Short breakpoint write')
        checked(k.FlushInstructionCache(created.process, address, len(data)))

    def context(tid):
        ctx = Wow64Context()
        ctx.ContextFlags = CONTEXT_FLAGS
        checked(k.Wow64GetThreadContext(threads[tid], c.byref(ctx)))
        return ctx

    def set_context(tid, ctx):
        checked(k.Wow64SetThreadContext(threads[tid], c.byref(ctx)))

    def snapshot(kind, tid, ctx, **extra):
        row = dict(kind=kind, tid=tid, registers={n: int(getattr(ctx, n)) for n in
                   ('Eip', 'Eax', 'Ebx', 'Ecx', 'Edx', 'Esi', 'Edi', 'Esp', 'Ebp', 'Dr6')}, **extra)
        row['x87_control_word'] = struct.unpack('<I', bytes(ctx.FloatSave[:4]))[0]
        if club is not None:
            row.update(club_address=club, observed_club_plus4_word_u16=struct.unpack('<H', read(club + 4, 2))[0],
                       identity_import_observed=report['selected_club_import_observed'],
                       visiting_capacity_u32=list(struct.unpack('<II', read(club + 0x13C, 8))))
        report['events'].append(row)

    try:
        while time.monotonic() - started < plan.seconds and event_count < plan.max_events:
            display.check(created.pid)
            if (qualification_only and display.ready() and report['private_wrapper_load_observed']
                    and report['native_graphics_initialization_accepted']):
                report['stop_reason'] = 'display_qualification_complete'
                break
            event = DebugEvent()
            if not k.WaitForDebugEvent(c.byref(event), 100):
                if c.get_last_error() != 121:  # ERROR_SEM_TIMEOUT
                    checked(False)
                continue
            event_count += 1
            continuation, stop = 0x10002, False  # DBG_CONTINUE
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
                    threads[event.tid] = event.u.thread.thread
                    if club is not None:
                        ctx = context(event.tid)
                        arm_writes(ctx, club)
                        set_context(event.tid, ctx)
                elif event.code == 4:
                    threads.pop(event.tid, None)
                    pending.pop(event.tid, None)
                elif event.code == 6 and event.u.dll_file:
                    buffer = c.create_unicode_buffer(32768)
                    length = k.GetFinalPathNameByHandleW(event.u.dll_file, buffer, len(buffer), 0)
                    if 0 < length < len(buffer):
                        loaded = Path(buffer.value.removeprefix('\\\\?\\')).resolve()
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
                        if address == IMPORTED and ctx.Ebx == plan.club_index:
                            if club is None or struct.unpack('<I', read(club, 4))[0] != 0x7BD614:
                                raise CapacityWatchError('Selected import has no qualified DBRClub vftable')
                            report['selected_club_import_observed'] = True
                        if address != IMPORTED or ctx.Ebx == plan.club_index:
                            snapshot('source_breakpoint', event.tid, ctx, source_va=address)
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
                            exstyle = struct.unpack('<I', read(ctx.Esp, 4))[0]
                            report.setdefault('native_window_requests', []).append(dict(
                                source_va=address, extended_style=exstyle))
                            if exstyle & 8:  # WS_EX_TOPMOST, before the API executes
                                report['stop_reason'], stop = 'native_topmost_request_guard', True
                        if address == 0x50D630:
                            report['native_fresh_world_loader_observed'] = True
                        if address in (0x6A93FB, 0x6A941E):
                            report.setdefault('native_driver_load_results', []).append(dict(
                                source_va=address, handle=int(ctx.Eax),
                                requested_driver=read(ctx.Esi, 128).split(b'\0', 1)[0].decode('latin1')))
                        if address == ALLOC_RETURN:
                            if club is not None:
                                raise CapacityWatchError('Second array allocation: lifecycle scope exhausted')
                            club = plan.club_address(ctx.Eax, ctx.Esi)
                            report['allocation_observed'] = True
                            for tid in threads:
                                target = ctx if tid == event.tid else context(tid)
                                arm_writes(target, club)
                                set_context(tid, target)
                            snapshot('allocation_before_constructor', event.tid, ctx, count=int(ctx.Esi))
                        if address == UNCONTROLLED_READ and ctx.Esi == club:
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
                        if address != IMPORTED or ctx.Ebx != plan.club_index:
                            pending[event.tid] = address
                        else:
                            ctx.EFlags &= ~0x100
                        set_context(event.tid, ctx)
                    elif code in (0x80000004, 0x4000001E):
                        ctx = context(event.tid)
                        if ctx.Dr6 & 3:
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
            finally:
                # Terminate while the debug event still suspends the child;
                # never resume a source-proven unsafe window request first.
                if stop and not exited:
                    checked(k.TerminateProcess(created.process, 0xE013))
                checked(k.ContinueDebugEvent(event.pid, event.tid, continuation))
            if stop:
                break
        report.setdefault('stop_reason', 'event_bound' if event_count >= plan.max_events else 'time_bound')
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
            report['stop_reason'], report['error'] = 'display_safety_stop', str(error)
        report['display_observation'] = display.receipt()
        report['runtime_nonexclusive_qualified'] = bool(
            qualification_only and report['stop_reason'] == 'display_qualification_complete'
            and display.ready() and report['private_wrapper_load_observed']
            and report['native_graphics_initialization_accepted'])
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
    return 2 if result['stop_reason'] in ('probe_error', 'display_safety_stop', 'native_topmost_request_guard') else 0


if __name__ == '__main__':
    raise SystemExit(main())
