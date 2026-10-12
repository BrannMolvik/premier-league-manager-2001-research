# Recovery546: correction of original staff list-field ownership and bounded Apply projection

## Owner evidence and critical correction

Owner-provided original footballmanager.exe size 4,714,541, SHA-256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3. Exact binary independently rechecked. Only static objdump. No original executable launch, no W11 GUI acceptance.

Earlier Recovery546 notes and the report GATE13_PSUPPORTSTART_STAFF_ASSIGNMENT_DISPATCH_RECOVERY546.md called the DWORDs cleared at 0x4D0844, 0x4D0854, 0x4D0864 and 0x4D086F "list heads". **That label is WRONG and superseded**. The original list is three DWORD fields:

| Container | +0 owner/deletion flag | +4 actual first node | +8 actual last node |
| --- | --- | --- | --- |
| Original global staff | 0x875600 | 0x875604 | 0x875608 |
| DBRUser inactive types1..5 | +0x5B8 | +0x5BC | +0x5C0 |
| DBRUser inactive types6..16 | +0x5C4 | +0x5C8 | +0x5CC |
| DBRUser current staff | +0x5D0 | +0x5D4 | +0x5D8 |

Independent x86 cross-check:
- Native 0x617D70 reads [ecx+8] for last node, updates [ecx+4] for first node when empty, appends new linked node tail via +4(next)/+8(prev). Source nodes 0xC bytes holding CSupportStaff pointer at node+0.
- Native 0x42CBF0 reads/stores [ecx+4],[ecx+8] and node+4/+8 to unlink without freeing.
- Native 0x4D1880 calls 0x42CBF0, then tests **[container+0]**, and only when nonzero invokes CSupportStaff::0x4CA630 plus free on the removed staff object; whether or not payload freed, it releases the 12-byte node. Thus [container+0] controls whether removal DISPOSES the payload.
- TeamSelect 0x4D8F23/0x4D8F33/0x4D8F43/0x4D8F4E and PSupportStart Apply 0x4D0844/0x4D0854/0x4D0864/0x4D086F write 0 into those OWNER flags so original staff payload survives transfers, not into linked-list heads. An implementation resetting actual lists would be unfaithful and would leak/corrupt staff.

The original TeamSelect warmup 0x4DA4F0 walks pre-existing active staff list user+0x5D4, stages seven pointers and flags; calls 0x4CA070 to add selected staff to respective inactive user lists +0x5B8/+0x5C4, removes from active list +0x5D4 and from global +0x875604, using non-deleting 0x4D1880. Staff is MOVED between lists, not generated anew or destroyed.

## Original Apply source control effects for bounded 7-slot state

Original 0x4D0830 loops selector indexes 6 down to0, stores inverse 0x652F80 bit15 in record+0x28+i, skips NULL source staff pointer. Flag nonzero: skip if pointer already present in either inactive list; otherwise 0x4CA070 appends pointer to appropriate inactive source type bucket and 0x4D1880 unlinks matching current list node. Flag zero: 0x4D1880 removes pointer if present from both inactive lists, appends the pointer to active current user list if absent through 0x617D70, appends to global staff list when absent. The original generally appends to end and preserves existing source order; processed slots are reverse (6..0). Native flags set to 0 ensure non-destructive pointer moves.

An isolated source-list projection is implemented as original_supportstart_staff_lists.py, accepting source-ordered lists and exact source slot pointers (both existing source records), plus seven explicit native DWORDs. It retains object identity by Python `is` rather than conflating two distinct staff pointers with equal values. It protects existing global staff from other users. It does not patch actual controller staff state, allocate actual C++ nodes, create or destroy original payloads, derive selector HWND/mouse inputs, re-seed the shared CRT RNG, claim an original PSupportStart screen, or parse original save data. It is a SOURCE-BOUNDED partial simulation to enable future safe integration and tests, not native full journey acceptance.

## Exact source reproduction

```bash
sha256sum footballmanager.exe
objdump -D -Mintel --start-address=0x4d0830 --stop-address=0x4d09ff footballmanager.exe
objdump -D -Mintel --start-address=0x4d8f17 --stop-address=0x4d8f82 footballmanager.exe
objdump -D -Mintel --start-address=0x4da4f0 --stop-address=0x4da59b footballmanager.exe
objdump -D -Mintel --start-address=0x617d70 --stop-address=0x617da7 footballmanager.exe
objdump -D -Mintel --start-address=0x42cbf0 --stop-address=0x42cc24 footballmanager.exe
objdump -D -Mintel --start-address=0x4d1880 --stop-address=0x4d18b9 footballmanager.exe
```

Original EXE static only, no actual GUI interaction. Gates13–17 OPEN, PR638 first Inbox CRT shared stream DRAFT/BLOCKED. Further work: verify all seven row control state bit producers and original physical controls, source intact staff pointer initialization/multi-human ownership, then implement real PSupportStart Apply/Cancel and original visual assets/complete user flow with save and real Win11 acceptance.
