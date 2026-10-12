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
