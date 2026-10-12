# Recovery545: Original PSupportStart handoff, returned action byte, screen bounds and source art shapes

**Evidence**: private unchanged owner-supplied original `footballmanager.exe`,
4,714,541 bytes; SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Static disassembly and previously separately verified source art byte reads
only. **Original executable NOT launched**; no Windows GUI accepted.

## TeamSelect to PSupportStart source control route and return

Original TeamSelect internal routine `0x4D91C0` (guarded by
`0x64F960` and `0x652F80`) passes pointers to
its private seven-staff record `+0x0C/+0x28` into original
`0x450BB0` at `0x4D9224`. This factory:
- obtains current registered user `0x4139D0`, selected
  original DBRClub pointer from `DBRUser+0x5B4`
  (`0x450BC9..0x450BD3`);
- allocates **0x29C0 bytes** for the original PSupportStart object
  (`0x450BD9`) and calls constructor `0x4CF0F0`
  (`0x450C07`) using the passed records;
- calculates caller-dependent positioning and passes original
  width `0x2F8=760` and height `0x1F4=500` to
  `0x653320` at `0x450C74..0x450C86`.
  **Proven** arguments are original object dimensions; they are
  NOT proof of fixed absolute top-left in every display mode;
- resolves the selected club's native short caption through
  `0x40DA70` and configures a child at `+0x1E70`
  (`0x450C8B..0x450C9D`);
- registers/displays the UI through `0x5EB540`
  (`0x450CA2..0x450CAA`), calls
  `0x532650` at `0x450CBA`, which delegates
  to `0x654210`, then **reads**
  PSupportStart `+0x1DE4` at `0x450CBF`,
  performs cleanup `0x5EB920`, and returns
  that byte as the factory's return value
  (`0x450CD9..0x450CE8`).
  The fact that this result is read **after** the
  GUI routine is the original source return handoff,
  not a guessed reconstruction callback.

The established PSupportStart virtual event dispatcher
`0x4D05E0` handles original event 1 without
calling apply virtual: sets `+0x1DE4=0` and invokes
`0x6539F0(0)` at `0x4D061F..0x4D062A`.
Event 2 first invokes vtable `+0x4C=0x4D0830`
which commits actual selected staff-list mutations and
edited user first/surname, then sets `+0x1DE4=1`
and invokes `0x6539F0(0)`
(`0x4D0606..0x4D0618`).
This results in an explicit original return byte
**0 cancel/no apply, 1 apply**. Neither path is a
generic modern back/forward action.

Original `0x6539F0` passes Windows message code
`0x400` plus zeros through wrapper `0x659650`,
which invokes an imported native UI message function
via `0x7BD2D8`. This establishes a real
source event/message request, **not** independent
proof of observed window closure or follow-on scene
after `0x4D91C0`. The `0x4D91C0` caller
does **not consume the returned boolean explicitly** in
the immediate `0x4D9229` instructions. The
post-PSupportStart actual management transition,
staff list synchronization and modal stack restore
remain incomplete. Do not introduce a visible
name-only editor or an invented screen transition.

## Independent original resource header dimensions

The five individual original `FM2001_Art/Support/`
files from the owner's connected private Drive
were already separately materialized, their complete
file sizes/SHA-256 pinned in
`GATE13_PSUPPORTSTART_NAME_EDITOR_NATIVE_RECOVERY544.md`.
Rechecked actual first four bytes of each original
EA444 header (two little-endian unsigned dimensions):

| Original Support file | Bytes | 444 header dimensions |
| --- | ---: | --- |
| `support_title_bar.444` | 4,076 | 336 x 20 |
| `sub_title_bar.444` | 3,988 | 336 x 19 |
| `support_bars.444` | 4,516 | 336 x 19 |
| `stars.444` | 2,776 | 75 x 10 |
| `stars2.444` | 1,504 | 75 x 10 |

The header dimensions are **verified original asset shapes**,
but not original on-screen geometry, drawing order, hover
frame offsets or whether every file belongs to this exact
PSupportStart state. The original executable embeds all
five paths and loader references (Recovery544).
**No proprietary asset was committed.**

## Original source reproduction

```bash
sha256sum footballmanager.exe
objdump -D -Mintel --start-address=0x4d91c0 --stop-address=0x4d9239 footballmanager.exe
objdump -D -Mintel --start-address=0x450bb0 --stop-address=0x450ce9 footballmanager.exe
objdump -D -Mintel --start-address=0x532650 --stop-address=0x532675 footballmanager.exe
objdump -D -Mintel --start-address=0x654210 --stop-address=0x6542a5 footballmanager.exe
objdump -D -Mintel --start-address=0x4d05e0 --stop-address=0x4d0679 footballmanager.exe
objdump -D -Mintel --start-address=0x6539f0 --stop-address=0x653a0a footballmanager.exe
```

## Committed implementation and exact open scope

PR #641, squash merge
`164060699535d1e7ab25319d9d36524af5f0f84c`,
adds a strict seven-selector **source-data contract** in
`reconstruction/support_staff.py`, exercising the
original fresh-six-staff-to-seven-record boundary
with `reconstruction/test_support_staff.py` and
an original TeamSelect integration regression in
`reconstruction/test_original_teamselect_native.py`.
On exact PR head `322bdbb1b61f8da1ae62a4687d425cfcbd487893`,
Gate13 presentation source workflow `38195183810`
and asset policy `38195183808` both passed.
No full reconstruction suite was dispatched for
PR #641 and the five dedicated `test_support_staff.py`
new tests were not part of the focused Gate13
command; they still require the next meaningful
full-suite/local verification. **Do not falsely
claim all those tests executed**.
No original GUI behavior, native source-to-RNG
staff producer integration, existing user staff
mutation, original save format or genuine
Windows11 GUI was accepted by those checks.

**Next high-priority source task:** trace full
PSupportStart child geometry, event-to-physical
button/control IDs, currently unqualified staff
getter names/ratings, live selected user staff
record producers and apply/return effect, then
implement genuine PSupportStart UI with exact
source graphics and modal return.
Shared CRT TLS startup/Inbox reason blocker
PR638 remains unmerged; complete actual Inbox
selected message, PEAMMessage/ESC, R1 all
original match modes/results/return, all
shipped country/league/multi-human modes and
Gate13–17 release audit after verified original journeys.
