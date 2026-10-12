"""Independent original-PE/static audit of TeamSelect Continue queue lifecycle.

Manual source audit only: requires authorized private footballmanager.exe,
GNU objdump on PATH; does NOT execute the game or use its assets in public Git.
Run: python research/audit_original_teamselect_continue_static.py /path/footballmanager.exe
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ORIGINAL_SHA256 = "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"


def main(path: str) -> None:
    binary = Path(path).read_bytes()
    if hashlib.sha256(binary).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("Unexpected original executable source SHA256")
    listing = subprocess.check_output(
        ["objdump", "-D", "-Mintel", "--section=.text", path], text=True
    )

    def instruction(address: str) -> str:
        match = re.search(
            r"^\s*" + address + r":\s*(.*)$", listing, re.MULTILINE
        )
        if match is None:
            raise AssertionError("Native source address not recovered: " + address)
        return match.group(1)

    checks = (
        ("4da4a5", "call   0x4c41c0"),  # TeamSelect Continue source event
        ("4c4275", "call   0x4e9830"),  # queue clear/destruct
        ("4c4304", "call   0x413830"),  # subsequent competition init
        ("4c48b8", "call   0x6194d0"),  # later world event allocation
        ("4a8103", "call   0x6194d0"),  # weekly world event allocation
        ("4259b5", "call   0x614080"),  # user creation first drain
        ("412f1f", "call   0x614080"),  # user setup second drain
        ("53109e", "call   0x66950f"),  # original CRT seed
        ("5310eb", "call   0x619f70"),  # DIFFERENT precompute, not allocator
        ("4261b3", "call   0x415870"),  # manager old-slot detach
        ("4e9856", "call   DWORD PTR [edx]"),  # polymorphic event destructor
    )
    for address, target in checks:
        observed = instruction(address)
        if target not in observed:
            raise AssertionError((address, target, observed))
        print("PASS", address, target)
    # Direct native UI path, independently cross-checked against the owner EXE:
    # TeamSelect selection -> user registration -> first queue drain ->
    # manager binding -> second queue drain -> six staff and modal staging.
    click_calls = (
        ("4d8ef8", "call   0x413bb0"),  # successful selected club/user birth
        ("413c4a", "call   0x617d70"),  # register actual DBRUser
        ("413c54", "call   0x4258d0"),  # initialize selected user
        ("4258f8", "call   0x42c400"),  # thirteen player-name pairs
        ("4259b5", "call   0x614080"),  # FIRST global event drain
        ("413c5b", "call   0x426090"),  # manager slot binder
        ("4d8f19", "call   0x412ef0"),  # selected club user setup
        ("412f1f", "call   0x614080"),  # SECOND global event drain
        ("4d8f75", "call   0x4c9cd0"),  # six staff constructors
        ("4d8f7f", "call   0x4da4f0"),  # seven initial selector rows
        ("4d90c8", "call   0x413db0"),  # team deselect removes DBRUser
        ("43256f", "call   0x413c90"),  # distinct user event prune caller
    )
    for address, expected in click_calls:
        actual = instruction(address)
        if expected not in actual:
            raise AssertionError(("Unexpected native click/cancel edge", address, actual))
    if not (
        listing.index("  4d8ef8:") < listing.index("  4d8f19:")
        < listing.index("  4d8f75:") < listing.index("  4d8f7f:")
    ):
        raise AssertionError("Native TeamSelect first-user startup ordering altered")

    def direct_calls(target: str) -> tuple[str, ...]:
        return tuple(re.findall(
            r"^\s*([0-9a-f]+):[^\n]*call\s+0x" + target + r"(?:\s|$)",
            listing, re.MULTILINE
        ))

    # Counts enumerate *syntactic* direct callsites in this HASHED original
    # executable, NOT what is reachable/actually fires before either drain.
    if len(direct_calls("613ec0")) != 175:
        raise AssertionError("Original queue-enqueue helper xrefs changed")
    if len(direct_calls("613ee0")) != 5:
        raise AssertionError("Original timed queue-processor xrefs changed")
    if direct_calls("413c90") != ("43256f",):
        raise AssertionError("Original special queue-prune direct caller changed")
    print("PASS original native user first/second queue drain chronology")
    print("PASS 175 direct enqueue-helper, 5 timed-processor caller sites")
    print("PASS native TeamSelect deselect != special global event prune")
    print("WARNING direct xrefs do not prove pre-click producer reachability")

    # Nested editor return and TeamSelect's OUTER handler result are
    # distinct: native 0x450BB0 returns BL copied from PSupportStart
    # +0x1de4, but original TeamSelect 0x4D91C0 returns EBX saved from
    # earlier control acceptance 0x64F960, NOT the modal EAX result.
    modal_edges = (
        ("4d91d0", "call   0x64f960"),
        ("4d91d5", "mov    ebx,eax"),
        ("4d9224", "call   0x450bb0"),
        ("4d922c", "mov    eax,ebx"),
        ("450cbf", "mov    bl,BYTE PTR [esi+0x1de4]"),
        ("450cd9", "mov    al,bl"),
        ("4d060a", "call   DWORD PTR [edx+0x4c]"),
        ("4d0611", "mov    BYTE PTR [esi+0x1de4],0x1"),
        ("4d0623", "mov    BYTE PTR [esi+0x1de4],0x0"),
        ("4cf936", "push   0x4d89e0"),
        ("4d89e0", "jmp    0x5d4600"),
        ("41a352", "call   0x613ec0"),
        ("41a364", "call   0x613ee0"),
        ("41a463", "call   0x613ec0"),
        ("41a475", "call   0x613ee0"),
        ("5e3322", "call   0x613ec0"),
        ("5e3335", "call   0x613ee0"),
    )
    for address, expected in modal_edges:
        actual = instruction(address)
        if expected not in actual:
            raise AssertionError(("Nested modal/queue source edge changed", address, actual))
    print("PASS original nested editor return distinct from outer input acceptance")
    print("PASS Apply invokes vft+0x4C while Cancel only sets 0/requests close")
    print("PASS 3 enqueue -> immediate timed-process callsite pairs")
    print("WARNING no staff rollback or GUI fidelity follows from modal return")

    # Source-identical 0x7BD564 native queued-event wrapper vtable.
    # 0x40DFB0 returns zero; 0x404610 forwards virtual +0x24 of
    # the INNER object at wrapper+0x08; timed +0x10 forwards inner+0x3C.
    import struct
    wrapper_vft_offset = 0x3BD000 + (0x7BD564 - 0x7BD000)
    wrapper_vft = struct.unpack_from("<7I", binary, wrapper_vft_offset)
    expected_vft = (
        0x404620, 0x40DFB0, 0x5CE530, 0x5CE5E0,
        0x5CFA20, 0x404600, 0x404610,
    )
    if wrapper_vft != expected_vft:
        raise AssertionError(("Original native queued-event wrapper changed", wrapper_vft))
    wrapper_edges = (
        ("40dfb0", "xor    eax,eax"),
        ("40dfb2", "ret"),
        ("404610", "mov    ecx,DWORD PTR [ecx+0x8]"),
        ("404615", "jmp    DWORD PTR [eax+0x24]"),
        ("5cfa28", "call   DWORD PTR [eax+0x3c]"),
        ("5cfa2b", "test   eax,eax"),
        ("5cfa48", "call   0x413020"),
        ("404623", "call   0x404640"),
    )
    for address, expected in wrapper_edges:
        actual = instruction(address)
        if expected not in actual:
            raise AssertionError(("Native event wrapper target changed", address, actual))
    print("PASS original event wrapper vtable seven native function pointers")
    print("PASS original wrapper vft+4 zero; vft+18 forwards inner+0x24")
    print("PASS original timed wrapper vft+0x10 forwards inner+0x3c")
    print("WARNING inner event type/CRT/queue presence before first human UNKNOWN")

    # Native inner-event payload vtables for original 0x426220/0x426600
    # producer path; none are yet proven present during first human click.
    inner_vft_classes = (
        (0x7BDFD4, 0x4093E0),
        (0x7BDF80, 0x5CFF30),
        (0x7BE034, 0x5EB3E0),
    )
    for vtable_va, timed_handler in inner_vft_classes:
        vtable_offset = 0x3BD000 + (vtable_va - 0x7BD000)
        drain_handler = struct.unpack_from("<I", binary, vtable_offset + 0x24)[0]
        timed_actual = struct.unpack_from("<I", binary, vtable_offset + 0x3C)[0]
        if (drain_handler, timed_actual) != (0x40DFB0, timed_handler):
            raise AssertionError(("Inner native event vtable changed", vtable_va))
    dispatch_edges = (
        ("4093e0", "mov    eax,0x1"),
        ("5cff6c", "call   0x426600"),
        ("5eb428", "mov    eax,ecx"),
        ("413070", "cmp    eax,0x42"),
        ("413075", "cmp    eax,0x5b"),
        ("4130d5", "jmp    DWORD PTR [edx*4+0x413510]"),
        ("4132ab", "call   DWORD PTR [edx+0xc]"),
    )
    for address, expected in dispatch_edges:
        actual = instruction(address)
        if expected not in actual:
            raise AssertionError(("Native per-user event dispatcher changed", address, actual))
    print("PASS three typed inner event virtual drain/timed callback pairs")
    print("PASS 0x413020 user event dispatch; NOT a no-op registrar")
    print("WARNING these event constructors' first human reachability UNKNOWN")

    # Original 0x613EE0: virtual+0x10 result is NOT the event-removal
    # predicate; the second caller-pushed argument at [esp+0x14] is.
    # Every syntactic direct caller pushes explicit 1 and current global date.
    original_timed_queue_edges = (
        ("613eec", "mov    DWORD PTR [ebx+0x10],0x0"),
        ("613f00", "cmp    DWORD PTR [ecx+0x4],eax"),
        ("613f03", "jg     0x613f29"),
        ("613f07", "call   DWORD PTR [edx+0x10]"),
        ("613f0a", "mov    eax,DWORD PTR [esp+0x14]"),
        ("613f0e", "test   eax,eax"),
        ("613f1c", "call   0x4ea190"),
        ("613f37", "mov    eax,DWORD PTR [ebx+0x10]"),
        ("613f40", "call   0x614080"),
        ("613f62", "mov    ecx,DWORD PTR [eax+0x6b4]"),
        ("613f68", "call   0x5cf990"),
        ("41a35c", "push   0x1"),
        ("41a364", "call   0x613ee0"),
        ("41a46d", "push   0x1"),
        ("41a475", "call   0x613ee0"),
        ("432164", "push   0x1"),
        ("43216c", "call   0x613ee0"),
        ("4a807c", "push   0x1"),
        ("4a8084", "call   0x613ee0"),
        ("5e332d", "push   0x1"),
        ("5e3335", "call   0x613ee0"),
        ("616830", "call   0x404110"),
        ("616816", "cmp    al,BYTE PTR [ebp+0x14]"),
        ("4041bf", "call   0x4037b0"),
        ("4041c4", "cmp    al,0x1"),
        ("4041d1", "call   0x426220"),
        ("4f7f0f", "call   0x616620"),
        ("4f7f1b", "call   0x616620"),
        ("4f994e", "call   0x616620"),
        ("4259c0", "call   0x5cf830"),
        ("5cf838", "call   0x42c9f0"),
        ("42ca19", "call   0x686fe3"),
        ("42ca25", "call   0x686fe3"),
    )
    for address, expected in original_timed_queue_edges:
        actual = instruction(address)
        if expected not in actual:
            raise AssertionError(("Native queue or scheduler edge changed", address, actual))
    expected_direct_owners = {
        "613ee0": ("41a364", "41a475", "43216c", "4a8084", "5e3335"),
        "616620": ("4f7f0f", "4f7f1b", "4f994e"),
        "404110": ("616830",),
        "426220": ("4041d1",),
    }
    for target, callsites in expected_direct_owners.items():
        actual = direct_calls(target)
        if actual != callsites:
            raise AssertionError(("Unexpected direct callers", target, actual))
    print("PASS 5 original timed-queue direct sites all pass remove flag 1")
    print("PASS timed callback return ignored for node removal; +0x6B4 followup")
    print("PASS native schedule 616620 -> 404110 -> 426220 guarded chain")
    print("WARNING direct callers do NOT prove first-user queue population")

    # 0x426220 is reached via a *competition scheduler*, not directly
    # via TeamSelect selected club: 0x616620 -> 0x404110 -> 0x426220.
    # Scheduler entry 0x4F7C00 has one direct caller: 0x4C4381 INSIDE
    # 0x4C41C0 source Continue, after queue clear/precompetition.
    # Second scheduler entry 0x4F9010 (the 0x4F994E call is inside it)
    # has just two syntactic direct time-processing owners.
    confirmed_scheduler_direct_owners = {
        "4f7c00": ("4c4381",),
        "4f9010": ("4a86aa", "4a878b"),
        "4c41c0": ("4da4a5",),
    }
    for target, source_callsites in confirmed_scheduler_direct_owners.items():
        actual = direct_calls(target)
        if actual != source_callsites:
            raise AssertionError(("Original scheduler caller ancestry changed", target, actual))
    scheduler_edges = (
        ("4da4a5", "call   0x4c41c0"),
        ("4c4381", "call   0x4f7c00"),
        ("4a86aa", "call   0x4f9010"),
        ("4a878b", "call   0x4f9010"),
    )
    for address, expected in scheduler_edges:
        if expected not in instruction(address):
            raise AssertionError(("Original scheduler transition changed", address))
    if not (0x4c4275 < 0x4c4304 < 0x4c4381):
        raise AssertionError("Original Continue queue-clear/competitions order invalid")
    import re as _scheduler_re
    if any(
        0x4f9010 <= int(match.group(1), 16) < 0x4f994e
        for match in _scheduler_re.finditer(
            r"^\s*([0-9a-f]+):[^\n]*\bret(?:\s|$)", listing, _scheduler_re.MULTILINE
        )
    ):
        raise AssertionError("0x4F994E no longer in source 0x4F9010 body")
    print("PASS original selected click != direct scheduler producer")
    print("PASS source Continue -> 4C4381 -> 4F7C00 -> 616620")
    print("PASS 4F9010 third scheduler owner only two later-source direct callers")
    print("WARNING indirect callback reachability or prior session state NOT ruled out")

    # Next two original global queue producer families are NOT source-
    # qualified as first-human callbacks. One needs human-club predicate 1;
    # the other is reachable through polymorphic dispatch in 18 vtables.
    other_event_owner_edges = (
        ("41987d", "call   0x41a250"),
        ("41a285", "call   0x417340"),
        ("41a28a", "cmp    al,0x1"),
        ("417340", "call   0x417270"),
        ("417347", "jmp    0x4037b0"),
        ("5128b8", "call   0x4197c0"),
        ("5e30f4", "call   0x5e3110"),
        ("5e30d5", "call   DWORD PTR [eax+0x1c]"),
        ("5e30e0", "call   DWORD PTR [edx+0x20]"),
        ("5e30eb", "call   DWORD PTR [eax+0x24]"),
    )
    for address, expected in other_event_owner_edges:
        if expected not in instruction(address):
            raise AssertionError(("Original callback producer changed", address))
    for native, callers in {
        "41a250": ("41987d",),
        "4197c0": ("5128b8",),
        "5e3110": ("5e30f4",),
    }.items():
        if direct_calls(native) != callers:
            raise AssertionError(("Original callback caller changed", native))
    original_generic_event_virtual_slots = tuple(
        0x7d743c + (0x2c * i) for i in range(18)
    )
    if any(
        struct.unpack_from("<I", binary, slot - 0x400000)[0] != 0x5e30d0
        for slot in original_generic_event_virtual_slots
    ):
        raise AssertionError("Original 18 polymorphic event dispatch slot family changed")
    print("PASS source human-managed club gate for 41A250 enqueue producer")
    print("PASS generic 5E30D0 dispatch reused in 18 original vtable slots")
    print("WARNING vtable reachability and callback CRT effects are UNKNOWN")

    # Original RTTI disproves that 0x5E30D0 is an unidentified generic
    # event family. The eighteen vtables are actual injury/illness Aog
    # subclasses, and their shared +0x04 invokes 0x5E30D0.
    injury_rtti_source_types = (
        "AogCheekModerate", "AogNoseMild", "AogHeadMild",
        "AogRibsMild", "AogGroinSerious", "AogHamstringMild",
        "AogKneeModerate", "AogThighSerious", "AogCalfMild",
        "AogShinSerious", "AogAchillesMild", "AogDamagedShoulder",
        "AogDamagedAnkle", "AogBrokenFootSerious",
        "AogBrokenLegHeavy", "AogFluOut", "AogFluWeak", "AogVirus",
    )
    def original_rtti_type_name(vtable_va: int) -> str:
        col = struct.unpack_from("<I", binary, vtable_va - 0x400000 - 4)[0]
        desc = struct.unpack_from("<I", binary, col - 0x400000 + 12)[0]
        offset = desc - 0x400000 + 8
        return binary[offset:binary.index(b"\x00", offset)].decode("ascii")
    for n, identity in enumerate(injury_rtti_source_types):
        vtable = 0x7d7438 + (0x2c * n)
        if original_rtti_type_name(vtable) != ".?AV" + identity + "@@":
            raise AssertionError(("Native injury class identity changed", n))
    if original_rtti_type_name(0x7d7760) != ".?AVMPMInjuryReverse@@":
        raise AssertionError("Native delayed injury reversal event identity changed")
    injury_event_edges = (
        ("5e30d5", "call   DWORD PTR [eax+0x1c]"),
        ("5e30e0", "call   DWORD PTR [edx+0x20]"),
        ("5e30eb", "call   DWORD PTR [eax+0x24]"),
        ("5e30f4", "call   0x5e3110"),
        ("5e31e4", "mov    DWORD PTR [eax],0x7d7760"),
        ("5e3238", "call   0x613ec0"),
        ("5e32eb", "call   DWORD PTR [edx+0x8]"),
        ("5e330e", "mov    DWORD PTR [eax],0x7bd564"),
        ("5e3322", "call   0x613ec0"),
        ("5e3335", "call   0x613ee0"),
    )
    for address, expected in injury_event_edges:
        if expected not in instruction(address):
            raise AssertionError(("Original injury queue event owner changed", address))
    print("PASS original 18 injury/illness RTTI classes + MPMInjuryReverse")
    print("PASS injury conditional virtual gates and two event enqueue phases")
    print("WARNING no proof injury callback executes before first human creation")

    # Original guarded Match/FriendlyMatch virtual+0x3C owns this injury
    # producer, not native TeamSelect selected club callback.
    original_match_virtuals = (
        (0x7C4CE4, b".?AVMatch@@"),
        (0x7C9E14, b".?AVFriendlyMatch@@"),
    )
    for vtable, name in original_match_virtuals:
        target = struct.unpack_from("<I", binary, vtable - 0x400000 + 0x3C)[0]
        col = struct.unpack_from("<I", binary, vtable - 0x400000 - 4)[0]
        td = struct.unpack_from("<I", binary, col - 0x400000 + 12)[0]
        pos = td - 0x400000 + 8
        actual_name = binary[pos:binary.index(b"\x00", pos)]
        if target != 0x511370 or actual_name != name:
            raise AssertionError(("Original Match injury vtable changed", vtable))
    match_edges = (
        ("511434", "call   0x5112e0"),
        ("511443", "call   0x5127a0"),
        ("5128b8", "call   0x4197c0"),
    )
    for address, expected in match_edges:
        if expected not in instruction(address):
            raise AssertionError(("Original Match injury call changed", address))
    if direct_calls("5127a0") != ("511443",):
        raise AssertionError("Match injury direct caller changed")
    print("PASS guarded original Match/FriendlyMatch injury producer")

    # Modal result is captured BEFORE vtable-owned GUI destruction,
    # and the *outer* accepted callback explicitly ignores the result.
    # The native PSupportStart destructor owns seven child UI structs,
    # not direct original registered-human or staff-list cleanup.
    native_modal_close_edges = (
        ("450cbf", "mov    bl,BYTE PTR [esi+0x1de4]"),
        ("450ccd", "call   0x5eb920"),
        ("5eba9a", "mov    eax,DWORD PTR [edi]"),
        ("5ebaa0", "call   DWORD PTR [eax]"),
        ("4cf793", "call   0x4cf7b0"),
        ("4cf7cd", "mov    DWORD PTR [esi],0x7c6ddc"),
        ("4cf93b", "push   0x7"),
        ("4cf946", "mov    BYTE PTR [esp+0x20],0x10"),
        ("4cf94b", "call   0x66820d"),
        ("4cf9db", "call   0x5d4600"),
        ("4cfa5a", "call   0x6532a0"),
        ("4d060a", "call   DWORD PTR [edx+0x4c]"),
        ("4d0611", "mov    BYTE PTR [esi+0x1de4],0x1"),
        ("4d0623", "mov    BYTE PTR [esi+0x1de4],0x0"),
        ("4d9224", "call   0x450bb0"),
        ("4d922c", "mov    eax,ebx"),
        ("4d8f75", "call   0x4c9cd0"),
        ("4d8f7f", "call   0x4da4f0"),
        ("4da537", "call   0x4ca070"),
        ("4da561", "call   0x4d1880"),
        ("4da58d", "call   0x4d1880"),
        ("4d90c8", "call   0x413db0"),
    )
    for address, expected in native_modal_close_edges:
        if expected not in instruction(address):
            raise AssertionError(("Original source modal/owner instruction changed",address))
    if struct.unpack_from("<I", binary, 0x7c6ddc - 0x400000)[0] != 0x4cf790:
        raise AssertionError("Original SupportStart destructor vft+0 changed")
    if struct.unpack_from("<I", binary, 0x7c6e28 - 0x400000)[0] != 0x4d0830:
        raise AssertionError("Original SupportStart Apply vft+0x4c changed")
    for target, owners in {
        "4cf7b0": ("4cf793",),
        "450bb0": ("4d9224",),
        "4da4f0": ("4d8f7f",),
        "413db0": ("4d90c8",),
    }.items():
        if direct_calls(target) != owners:
            raise AssertionError(("Original modal caller set changed",target))
    print("PASS original modal event1 Cancel / event2 Apply and object teardown")
    print("PASS original first-human staff list staging before modal")
    print("WARNING transitive vft/callback/teardown side effects still unresolved")

    # Native modal exits do not synchronously tear down the HWND:
    # 0x6539F0 -> 0x659650 -> imported USER32.PostMessageA,
    # posting WM_USER (0x400) with original zero event payload.
    original_modal_postmessage_edges = (
        ("6539f4", "mov    ecx,DWORD PTR [ecx+0x64]"),
        ("6539fc", "push   0x0"),
        ("6539fe", "push   eax"),
        ("6539ff", "push   0x400"),
        ("653a04", "call   0x659650"),
        ("659658", "mov    ecx,DWORD PTR [ecx+0x4]"),
        ("659663", "call   DWORD PTR ds:0x7bd2d8"),
    )
    for addr, expected in original_modal_postmessage_edges:
        if expected not in instruction(addr):
            raise AssertionError(("Native SupportStart close message edge changed",addr))
    _close_users = direct_calls("6539f0")
    if len(_close_users) != 44 or not {"4d0618", "4d062a"}.issubset(_close_users):
        raise AssertionError("Native modal source close call sites changed")
    print("PASS SupportStart modal exit posts WM_USER 0x400 via USER32.PostMessageA")
    print("WARNING posted message handler and callback side effects unresolved")

    # Original MyWindow RTTI/vft+0 is 0x532B80; modal host
    # 0x450BB0 -> 0x532650 -> 0x654210 dispatches that MyWindow loop.
    # WM_USER 0x400 is filtered BEFORE USER32 Translate/DispatchMessage,
    # and returns MSG.wParam from stack. Both original action events
    # push literal zero to the posted close wrapper, so loop result=0.
    native_mywindow_loop_edges = (
        ("450cb2", "mov    ecx,0x877960"),
        ("450cba", "call   0x532650"),
        ("53266d", "call   0x654210"),
        ("654258", "mov    eax,DWORD PTR [edi]"),
        ("65425c", "call   DWORD PTR [eax]"),
        ("532ba8", "call   edi"),
        ("532bb9", "call   ebx"),
        ("532bbf", "cmp    DWORD PTR [esp+0x14],0x400"),
        ("532bc7", "je     0x532bf9"),
        ("532bce", "call   ebp"),
        ("532bd5", "call   DWORD PTR ds:0x7bd2ac"),
        ("532bf9", "mov    eax,DWORD PTR [esp+0x18]"),
        ("4d060d", "push   0x0"),
        ("4d061f", "push   0x0"),
    )
    for addr, expected in native_mywindow_loop_edges:
        if expected not in instruction(addr):
            raise AssertionError(("Original MyWindow event loop changed",addr))
    _mywindow_vft = 0x7cb294
    if struct.unpack_from("<I", binary, _mywindow_vft - 0x400000)[0] != 0x532b80:
        raise AssertionError("MyWindow virtual+0 native event pump changed")
    _mywindow_col = struct.unpack_from(
        "<I", binary, _mywindow_vft - 0x400000 - 4
    )[0]
    _mywindow_td = struct.unpack_from(
        "<I", binary, _mywindow_col - 0x400000 + 12
    )[0]
    _mywindow_name_start = _mywindow_td - 0x400000 + 8
    _mywindow_name = binary[
        _mywindow_name_start:binary.index(b"\x00", _mywindow_name_start)
    ]
    if _mywindow_name != b".?AVMyWindow@@":
        raise AssertionError("Original MyWindow RTTI class identity changed")
    print("PASS source MyWindow 0x400 loop intercept returns wParam zero")
    print("PASS Cancel/Apply store distinct modal bytes before same WM_USER close")

    # Fresh 0x874C10 world's registered-human linked list is owner flag=1.
    # Native TeamSelect deselect 0x4D90C8 -> 0x413DB0 unlinks via
    # 0x414680; this owner flag controls user payload destructor, not
    # merely the 0xC byte node freed on every unlink.
    native_human_owner_instruction_assertions = (
        ("412d04", "mov    DWORD PTR [esi+0x9c8],0x1"),
        ("412d0e", "mov    DWORD PTR [esi+0x9cc],ebx"),
        ("412d94", "mov    DWORD PTR [esi+0x9d4],ebx"),
        ("412d9a", "mov    DWORD PTR [esi+0x9c4],ebx"),
        ("413bef", "push   0x10f0"),
        ("413c44", "lea    ecx,[esi+0x9c8]"),
        ("413c4a", "call   0x617d70"),
        ("413c70", "inc    eax"),
        ("413c71", "mov    DWORD PTR [esi+0x9d4],eax"),
        ("4d90b6", "call   0x413b80"),
        ("4d90c8", "call   0x413db0"),
        ("413dfb", "call   0x414680"),
        ("41468d", "call   0x42cbf0"),
        ("414692", "cmp    DWORD PTR [esi],0x0"),
        ("41469f", "call   0x424fc0"),
        ("4146a5", "call   0x686fe3"),
        ("4146ae", "call   0x686fe3"),
        ("413e06", "dec    eax"),
        ("413e0d", "mov    DWORD PTR [esi+0x9c4],eax"),
        ("425000", "mov    DWORD PTR [eax],0x1"),
        ("42500c", "mov    DWORD PTR [ebx],0x1"),
        ("425016", "mov    DWORD PTR [eax],0x0"),
    )
    for address, expected in native_human_owner_instruction_assertions:
        if expected not in instruction(address):
            raise AssertionError(("Original registered human owner changed", address))
    print("PASS source registered-human linked list initially payload-owning")
    print("PASS 413BB0 user append and 413DB0 indexed deselect ownership")
    print("WARNING payload destructor's transitive staff/RNG effects unproven")

    # Registered-user payload destructor 0x424FC0 explicitly sets staff
    # list owner flags 1,1,0 then walks all three lists via 0x4145A0.
    # Each list node is always freed; staff payload destructed ONLY when
    # that list's owner flag is set and node has non-null payload.
    native_deselected_human_staff_destructor_edges = (
        ("425000", "mov    DWORD PTR [eax],0x1"),
        ("42500c", "mov    DWORD PTR [ebx],0x1"),
        ("425016", "mov    DWORD PTR [eax],0x0"),
        ("425319", "call   0x4145a0"),
        ("42532f", "call   0x4145a0"),
        ("425346", "call   0x4145a0"),
        ("4145b7", "cmp    DWORD PTR [ebx],0x0"),
        ("4145c4", "call   0x4ca630"),
        ("4145ca", "call   0x686fe3"),
        ("4145d6", "call   0x686fe3"),
        ("4d1892", "cmp    DWORD PTR [esi],0x0"),
        ("4d189f", "call   0x4ca630"),
    )
    for address, expected in native_deselected_human_staff_destructor_edges:
        if expected not in instruction(address):
            raise AssertionError(("Original user/staff ownership changed",address))
    print("PASS original DBRUser destructor inactive/current staff-list flags 1/1/0")
    print("PASS original 4145A0 frees nodes and conditionally destroys staff")
    print("WARNING global staff list and other transitive cleanup remain unresolved")

    # Recovery569 corrected input: 0x5D4790 tries parent base 0x64F7A0
    # FIRST for a nonnull second argument. A successful parent result
    # seeds EBP=1, so child virtual+0x6C acceptance is NOT necessary.
    # Rejected parent immediately returns false, bypassing all children.
    original_row_parent_first_edges = (
        ("5d479b", "test   ebx,ebx"),
        ("5d479d", "je     0x5d47b6"),
        ("5d47a5", "call   0x64f7a0"),
        ("5d47aa", "mov    ebp,eax"),
        ("5d47ae", "jne    0x5d47b6"),
        ("5d47b0", "pop    esi"),
        ("5d47ca", "test   cl,0x4"),
        ("5d47d1", "call   0x64f570"),
        ("5d47e8", "call   DWORD PTR [eax+0x6c]"),
        ("5d47eb", "or     ebp,eax"),
        ("5d47f6", "mov    eax,ebp"),
        ("5d6280", "call   0x5d4790"),
        ("5d6287", "test   edi,edi"),
        ("5d629d", "call   DWORD PTR [ebx+0x98]"),
        ("64f7a5", "mov    eax,DWORD PTR [esi+0x18]"),
        ("64f7ac", "test   cl,0x1"),
        ("64f7b8", "test   al,0x1"),
        ("64f7da", "call   DWORD PTR [edx+0xc]"),
        ("64f84b", "mov    eax,0x1"),
        ("64f856", "xor    eax,eax"),
    )
    for address, expected in original_row_parent_first_edges:
        if expected not in instruction(address):
            raise AssertionError(("Original row parent/child input changed", address))
    for va, target in (
        (0x7c6780+0x6c, 0x5d6270),
        (0x7c6780+0x98, 0x5d6200),
        (0x7be530+0x6c, 0x64f7a0),
        (0x7bff14+0x6c, 0x64f7a0),
    ):
        if struct.unpack_from("<I", binary, va - 0x400000)[0] != target:
            raise AssertionError(("Native row/child vtable input owner changed",hex(va)))
    print("PASS parent-first input and OR children; no fake last-two-only gating")

    # Accepted 0x64F7A0 calls original vft+0x1C(1),
    # native 0x64F470 -> 0x64F710 sets state bit0x10.
    # A later event with this bit still set is rejected until separate
    # vft+0x1C(0) path clears it; never manufacture release timing.
    row_press_state_edges = (
        ("64f803", "push   0x1"),
        ("64f807", "call   DWORD PTR [edx+0x1c]"),
        ("64f474", "push   0x10"),
        ("64f47a", "call   0x64f710"),
        ("64f482", "call   0x64f750"),
        ("64f720", "or     edx,eax"),
        ("64f722", "mov    DWORD PTR [esi+0x18],edx"),
        ("64f765", "mov    DWORD PTR [esi+0x18],edx"),
        ("64f863", "push   0x0"),
        ("64f867", "call   DWORD PTR [eax+0x1c]"),
    )
    for address, expected in row_press_state_edges:
        if expected not in instruction(address):
            raise AssertionError(("Original row pressed/released bit changed",address))
    for vtable_va in (0x7c6780, 0x7be530, 0x7bff14):
        if struct.unpack_from("<I", binary, vtable_va - 0x400000 + 0x1c)[0] != 0x64f470:
            raise AssertionError(("Original row/child vft+0x1C state handler changed",hex(vtable_va)))
    print("PASS accepted native row/child input sets bit0x10 before bit15 toggle")

    # Original +0x20/+0x24 are a callback-enabled flag/context pair:
    # row vft+0x08 -> 0x5D48C0 forwards callback binding to its five
    # original children; each child vft+0x08 -> 0x64F3C0 sets both.
    # 0x64F7A0 optionally invokes callback vft+0x0C if source both
    # has the callback flag and a nonnull 2nd event argument.
    original_modal_callback_binding_edges = (
        ("64f3c8", "mov    DWORD PTR [ecx+0x20],eax"),
        ("64f3cb", "mov    DWORD PTR [ecx+0x24],edx"),
        ("5d48d0", "call   0x64f3c0"),
        ("5d48e8", "call   DWORD PTR [edx+0x8]"),
        ("64f7c0", "mov    eax,DWORD PTR [esi+0x20]"),
        ("64f7cb", "test   eax,eax"),
        ("64f7cf", "test   ebp,ebp"),
        ("64f7d3", "mov    ecx,DWORD PTR [esi+0x24]"),
        ("64f7da", "call   DWORD PTR [edx+0xc]"),
        ("64f7df", "je     0x64f854"),
    )
    for address, expected in original_modal_callback_binding_edges:
        if expected not in instruction(address):
            raise AssertionError(("Source input callback binding changed",address))
    for vtable_va,target in (
        (0x7c6780,0x5d48c0), (0x7be9bc,0x64f3c0),
        (0x7c66c8,0x64f3c0), (0x7be530,0x64f3c0),
        (0x7bff14,0x64f3c0),
    ):
        if struct.unpack_from("<I", binary, vtable_va - 0x400000 + 0x8)[0] != target:
            raise AssertionError(("Native row input callback setter vft changed",hex(vtable_va)))
    print("PASS parent and all five child callback/context binding; hit callback opaque")

    # Native 0x450C37..0x450C86 determines modal origin from actual
    # viewport globals, not a hardcoded 800x600 or centered layout.
    source_modal_native_viewport_instructions = (
        ("450c12", "mov    eax,ds:0x8779c0"),
        ("450c17", "mov    ecx,DWORD PTR ds:0x8779c4"),
        ("450c3c", "cmp    eax,0x14"),
        ("450c3f", "jge    0x450c45"),
        ("450c41", "mov    ecx,eax"),
        ("450c45", "cmp    eax,0x30c"),
        ("450c4a", "lea    ecx,[eax-0x2f8]"),
        ("450c50", "jge    0x450c57"),
        ("450c52", "mov    ecx,0x14"),
        ("450c57", "mov    eax,ds:0x8779c4"),
        ("450c5c", "cmp    eax,0x32"),
        ("450c5f", "jl     0x450c74"),
        ("450c61", "cmp    eax,0x226"),
        ("450c66", "jl     0x450c6f"),
        ("450c68", "add    eax,0xfffffe0c"),
        ("450c6f", "mov    eax,0x32"),
        ("450c78", "push   0x1f4"),
        ("450c7d", "push   0x2f8"),
        ("450c86", "call   0x653320"),
    )
    for address, expected in source_modal_native_viewport_instructions:
        if expected not in instruction(address):
            raise AssertionError(("Original SupportStart viewport origin changed",address))
    print("PASS original PSupportStart conditional viewport-relative modal origin")

    # Source original native window 0x653480 computes LOCAL event x/y
    # subtracting window x/y, filters each child control state bit0,
    # uses four signed half-open x/y rectangle comparisons BEFORE
    # passing source point + literal1 to the child's vft+0x6C.
    modal_native_halfopen_hit_prefilter_edges = (
        ("65348b", "mov    ecx,DWORD PTR [eax]"),
        ("65348d", "mov    edx,DWORD PTR [esi+0xc]"),
        ("653493", "sub    ecx,edx"),
        ("653495", "mov    edx,DWORD PTR [eax+0x4]"),
        ("6534a2", "sub    edx,edi"),
        ("6534c7", "test   BYTE PTR [ecx+0x18],0x1"),
        ("6534cd", "cmp    edx,DWORD PTR [ecx+0x8]"),
        ("6534d0", "jl     0x6534f5"),
        ("6534d2", "cmp    edx,DWORD PTR [ecx+0x10]"),
        ("6534d5", "jge    0x6534f5"),
        ("6534d7", "cmp    eax,DWORD PTR [ecx+0xc]"),
        ("6534da", "jl     0x6534f5"),
        ("6534dc", "cmp    eax,DWORD PTR [ecx+0x14]"),
        ("6534df", "jge    0x6534f5"),
        ("6534e7", "push   0x1"),
        ("6534ea", "call   DWORD PTR [edx+0x6c]"),
    )
    for address, expected in modal_native_halfopen_hit_prefilter_edges:
        if expected not in instruction(address):
            raise AssertionError(("Original window event rectangle gate moved",address))
    print("PASS original window half-open child bounds before virtual input")

    # Native window 0x653480 always calls window's vft+0x10 with
    # literal event0 and local x/y point BEFORE it even inspects the
    # registered children. Original PSupportStart vft+0x10=0x4D05E0,
    # whose zero-event branch bypasses action event1/2 and calls
    # 0x653350 with window bounds. The source callback could affect
    # child/window state; geometry prefilter requires post-callback.
    native_modal_prechild_parent_virtual_edges = (
        ("653498", "mov    eax,DWORD PTR [esi]"),
        ("6534a4", "push   ecx"),
        ("6534a5", "push   0x0"),
        ("6534ad", "call   DWORD PTR [eax+0x10]"),
        ("6534b0", "mov    eax,DWORD PTR [esi+0x3c]"),
        ("4d05e7", "test   eax,eax"),
        ("4d05ec", "je     0x4d0641"),
        ("4d0670", "call   0x653350"),
    )
    for addr, target in native_modal_prechild_parent_virtual_edges:
        if target not in instruction(addr):
            raise AssertionError(("Native modal prechild source callback changed",addr))
    if struct.unpack_from("<I",binary,0x7c6ddc - 0x400000 + 0x10)[0] != 0x4d05e0:
        raise AssertionError("PSupportStart vft+0x10 source null event owner changed")
    print("PASS pre-child modal vft+0x10(0,point) before child geometry prefilter")
    print("WARNING actual scene graph routing, post-callback state still unverified")

    # SHA-verified original MyWindow stack owner, Recovery570.
    source_window_stack_570 = (
        ("532692", "call   0x653b40"),
        ("653b5e", "mov    eax,DWORD PTR [ebx]"),
        ("653b6a", "je     0x653c02"),
        ("653b70", "mov    edi,DWORD PTR [ebx+0x8]"),
        ("653b76", "dec    edi"),
        ("653b77", "mov    esi,DWORD PTR [eax+edi*4]"),
        ("653b82", "call   DWORD PTR [edx+0x44]"),
        ("653b87", "je     0x653b73"),
        ("653b94", "cmp    eax,edi"),
        ("653b98", "cmp    eax,DWORD PTR [esi+0x14]"),
        ("653b9d", "cmp    edx,DWORD PTR [esi+0x10]"),
        ("653ba2", "cmp    edx,DWORD PTR [esi+0x18]"),
        ("653baa", "call   0x653480"),
        ("653bc2", "push   0x0"),
        ("653bd1", "call   0x668995"),
        ("653bea", "call   0x6539f0"),
        ("653c05", "cmp    edi,DWORD PTR [ebx+0x8]"),
        ("653c15", "cmp    eax,DWORD PTR [ecx+0xc]"),
        ("653c1a", "cmp    eax,DWORD PTR [ecx+0x14]"),
        ("653c1f", "cmp    edx,DWORD PTR [ecx+0x10]"),
        ("653c24", "cmp    edx,DWORD PTR [ecx+0x18]"),
        ("653c2a", "call   0x653480"),
        ("654222", "mov    DWORD PTR [esi+0x64],edi"),
        ("654225", "call   0x6542b0"),
        ("6542ba", "mov    DWORD PTR [esi+0x4],0x1"),
        ("654320", "mov    DWORD PTR [eax+edx*4],esi"),
        ("654327", "mov    DWORD PTR [ebx+0x8],edi"),
        ("65434a", "inc    DWORD PTR [ebx]"),
    )
    for address, expected in source_window_stack_570:
        if expected not in instruction(address):
            raise AssertionError(("Original native window stack changed", address))
    for va, expected in ((0x7cb294+0x10, 0x532680), (0x7c6ddc+0x44, 0x628060)):
        if struct.unpack_from("<I", binary, va - 0x400000)[0] != expected:
            raise AssertionError(("Original window selector vft changed", hex(va)))
    print("PASS MyWindow captured/uncaptured source window dispatch")

    # Original Win32 WndProc mouse callbacks, kept separate from row hits.
    original_mywindow_win32_button_events_570 = (
        ("531cc3", "push   0x531f70"),
        ("531cc8", "push   0x201"),
        ("531cd2", "push   0x531f70"),
        ("531cd7", "push   0x203"),
        ("531ce1", "push   0x532010"),
        ("531ce6", "push   0x202"),
        ("531cbe", "call   0x6a4ba0"),
        ("531ccd", "call   0x6a4ba0"),
        ("531cdc", "call   0x6a4ba0"),
        ("531f27", "test   bl,bl"),
        ("531f2a", "jne    0x531f3b"),
        ("531fb7", "test   bl,bl"),
        ("531fba", "jne    0x531fe2"),
        ("531fbc", "mov    eax,DWORD PTR [esp+0x30]"),
        ("531fc7", "and    ecx,0xffff"),
        ("531fd6", "shr    eax,0x10"),
        ("531fdd", "call   0x532680"),
        ("53205c", "mov    eax,DWORD PTR [esp+0x30]"),
        ("532067", "and    ecx,0xffff"),
        ("532076", "shr    eax,0x10"),
        ("53207d", "call   0x5326a0"),
        ("532689", "call   0x6596e0"),
        ("532692", "call   0x653b40"),
        ("6596e0", "mov    DWORD PTR [ecx+0xc],0x1"),
        ("6596f0", "mov    DWORD PTR [ecx+0xc],0x0"),
        ("5326a9", "call   0x6596f0"),
        ("5326b2", "call   0x653c40"),
    )
    for address, expected in original_mywindow_win32_button_events_570:
        if expected not in instruction(address):
            raise AssertionError(("Original Win32 left-button event changed",address))
    print("PASS native WM_LBUTTONDOWN/DBLCLK and WM_LBUTTONUP source handlers")

    actual_allocators = [
        match.group(1) for match in re.finditer(
            r"^\s*([0-9a-f]+):[^\n]*call\s+0x6194d0(?:\s|$)",
            listing, re.MULTILINE
        )
    ]
    if actual_allocators != ["4a8103", "4c48b8"]:
        raise AssertionError(("Unexpected direct world allocator xrefs", actual_allocators))
    if not (
        listing.index("  4c4275:") < listing.index("  4c4304:")
        < listing.index("  4c48b8:")
    ):
        raise AssertionError("Original Continue queue/competition/allocator order changed")
    print("PASS exact original source queue-clear -> competition -> allocator order")
    print("This audits static original instructions, NOT gameplay or GUI execution.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python audit_original_teamselect_continue_static.py ORIGINAL_EXE")
    main(sys.argv[1])
