# Recovery553: native event acceptance and owner callbacks for SupportStart/TeamSelect

The original executable was inspected **statically**, SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
No original game process was run; this is not a screen-click or GUI acceptance.

## Source row and original support child dispatch

Original PSupportStart registered seven parent rows each with five
children; vft `0x7C6780+0x6C=0x5D6270` is the source row event owner.
The latter invokes `0x5D4790`; if rejected, no selection bit15 change.
If accepted, source `0x5D6200` flips the parent selection bit and
propagates to children with registration bit0x20 (first THREE).
Actual child dispatcher `0x5D4790` processes children with
registration bit0x04 (FOURTH star + FIFTH text), after
`0x64F570` control-bit0x01 enabled check.
**Neither set of flags by itself establishes a mouse click.**

## Source generic row handler 0x64F7A0

On each native row/child:
1. Reject if control+0x18 bit0x02 is **clear** or bit0x10 is **set**.
2. Read control+0x20. If nonzero AND the second native event argument
   is nonzero, obtain actual owner at control+0x24. Invoke its
   **vtable+0x0C** with (control, first native event argument);
   rejection returns zero immediately.
   When either control+0x20 or second argument is zero this optional
   owner callback is bypassed, but control bit checks still apply.
3. Only after qualification, optionally invoke source global event
   sink at `0x984810` using source virtual0 and notification code0.
4. Invoke control **virtual+0x1C(true)**.
5. When owner control+0x20 and second event argument are nonzero,
   invoke its **vtable+0x10** follow-up with the same event context.
6. Optionally signal source global input state `0x984818` and
   `0x984814`, return handler result1.
The original GUI's owner callbacks and screen-parent transform
have not yet been mapped to a pointer hit rectangle; do not
assume the known star/text child layout rectangles are hit masks.

## Distinct original TeamSelect modal trigger 0x64F960

TeamSelect source `0x4D91C0` first calls **0x64F960**,
which uses a different gate/owner callback:
1. Require native control bit0x02 **set**, bit0x20 **clear**.
2. If control+0x20 nonzero AND second event argument nonzero,
   invoke owner at control+0x24 **vtable+0x1C** as veto gate.
3. On acceptance, optionally report global event sink
   `0x984810` with different code3;
   invoke control **virtual+0x20(true)**.
4. When the owner second-argument route is active, invoke
   owner **vtable+0x20** notifier.
5. Call optional global `0x984818/0x984814` observers; return1.
The caller then ALSO tests control bit15 before invoking the
`0x450BB0` SupportStart modal. Source modal Cancel(0)/Apply(1)
are not caller event returns: `0x4D922C` restores saved
input-handler acceptance, so a Cancel can still be handled.

This trace sharply distinguishes native row source event
vft+0x0C/0x10 callbacks from TeamSelect vft+0x1C/+0x20.
It also explains why reusing a generic `point in visual rect`
check would not establish native source event ownership.
The next original source task is to find exactly which
actual owner objects are installed at control+0x24
and their vft+0x0C/0x10/0x1C/0x20 methods,
then bind source-authentic hit ownership and payload
to the modern host without invented GUI behavior.

## Reproduce

```bash
objdump -D -Mintel --start-address=0x64f7a0 --stop-address=0x64f85a footballmanager.exe
objdump -D -Mintel --start-address=0x5d4790 --stop-address=0x5d47fc footballmanager.exe
objdump -D -Mintel --start-address=0x5d6270 --stop-address=0x5d62b0 footballmanager.exe
objdump -D -Mintel --start-address=0x64f960 --stop-address=0x64fa18 footballmanager.exe
objdump -D -Mintel --start-address=0x4d91c0 --stop-address=0x4d923b footballmanager.exe
```

**Status:** source ownership trace only. Player-visible PSupportStart
full seven-row GUI, source-personal names from exact shared RNG and
native input owner, Apply/Cancel and TeamSelect return, Inbox selected
detail, R1 all modes, multi-league/multihuman, and Gates13–17
Windows11 acceptance remain incomplete.
