# Recovery544 native PSupportStart manager name editor: exact RTTI and constructor

## Authenticated source and reachability

Verified original private 4,714,541-byte `footballmanager.exe` PE SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
All addresses below were independently inspected with `objdump` and
little-endian PE byte reads, without running any original code.

- At original `0x7C6DD8` a vtable-before pointer targets
  RTTI Complete Object Locator `0x7E6E80`; the locator's
  type descriptor is `0x81E810`, containing exact
  original MSVC type-name bytes `.?AVPSupportStart@@`
  (type name begins at +8). Therefore final vtable
  `0x7C6DDC` identifies genuine native **PSupportStart**.
- Original constructor `0x4CF0F0` allocates/initializes
  the screen/object, with source `0x4CF57A` writing final
  vtable `0x7C6DDC`. It retains its source
  0x30-byte editable first/surname buffers at
  `object+0x97C`/`object+0x980` (allocation calls
  `0x4CF5CA..0x4CF603`), then resolves current user
  and loads its first/surname at `0x4CF6AC..0x4CF6F0`.
- Source caller `0x450BB0` obtains current registered user
  through `0x4139D0` and selected DBRClub pointer at
  `0x450BD3`, allocates `0x29C0`-byte object at
  `0x450BD9..0x450BDE` and calls actual PSupportStart
  constructor `0x4CF0F0` at **`0x450C07`**.
  The containing outer GUI action and exact order relative to
  all Start/Continue transitions still require separate call-chain proof;
  do not infer a complete ordinary path solely from this call.
- Final source vtable entry `0x7C6DDC+0x4C =
  0x7C6E28` holds exact pointer `0x004D0830`.
  Thus `PSupportStart` virtual +0x4C invokes
  native `0x4D0830`. Its source branch
  `0x4D09FD..0x4D0A61` obtains current user,
  copies current edit buffer +0x97C to native
  `DBRUser+0x05`, and +0x980 to
  `DBRUser+0x25` (separate state byte +0x04
  at `0x4D0A63..0x4D0A6C`).
  This confirms **source virtual ownership**, though
  which on-screen action/event invokes that virtual and
  what validation preceded it remain unresolved.
- Native DBRUser name destinations are adjacent
  0x20-byte fields. Original UI editor buffers allocate
  0x30 bytes; the recovered native string copy uses
  unbounded string length. A Windows 11 port must not
  rely on potential native overrun. The experimental
  PR640 bounds reconstructed user first/surname to
  <=31 CP1252 bytes plus terminator as a safety guard;
  **that limit is not claimed to be the original input-widget
  validation**, which still needs source verification.

## Correct scope and priority

This PSupportStart source UI lifecycle is original,
not a new settings/preferences feature.
`HumanGameplayController.select_club` currently installs
one `HumanManagerState`, and the Tk reconstructed
front end lacks a complete native PSupportStart
human-name editor, source controls and return behavior.
Consequently original player workflow is still
**P0 PARTIAL** even if PR640's model state and
save/load tests pass. Next investigate `0x450BB0`
caller/parent navigation, PSupportStart original
editable controls and action/return, and integrate it
with exact source names and multi-user distinctions
before claiming source-correct manager name UI.

**Original process observation:** NONE.
**Windows 11 visual/interactive acceptance:** NONE.
**Gate13–17:** OPEN. Draft PR638 CRT mismatch remains BLOCKED.

## Private reproduction

```bash
sha256sum footballmanager.exe
objdump -s --start-address=0x7c6dd8 --stop-address=0x7c6e3c footballmanager.exe
objdump -s --start-address=0x81e810 --stop-address=0x81e830 footballmanager.exe
objdump -D -Mintel --start-address=0x450bb0 --stop-address=0x450c40 footballmanager.exe
objdump -D -Mintel --start-address=0x4cf0f0 --stop-address=0x4cf159 footballmanager.exe
objdump -D -Mintel --start-address=0x4cf570 --stop-address=0x4cf725 footballmanager.exe
objdump -D -Mintel --start-address=0x4d0830 --stop-address=0x4d0a74 footballmanager.exe
```


## Follow-up source caller chain through TeamSelect vtable

Source examination after PR #640 merged identifies the **sole direct** executable
CALL to PSupportStart factory `0x450BB0`: native
`0x4D9224` in method `0x4D91C0`. Raw little-endian pointer search
in original `.rdata` shows `0x4D91C0` at
`0x7C7628`, within the same original TeamSelect-style
class vtable block `0x7C7600..0x7C7644` which also
contains native `0x4D8E90` (the previously proven
club selection handler). This bounds the source call
owner to the original TeamSelect class's event/method path.
Neither a new Settings action nor a generic invented
manager-home is the original PSupportStart opener.

Crucially, original `0x4D91C0` is **conditional**.
At `0x4D91D0` it first calls native
`0x64F960` and tests a result, then at
`0x4D91DD` it calls `0x652F80` and
tests its Boolean. If either fails it branches to
`0x4D9234` and never opens PSupportStart.
The successful branch resolves an original TeamSelect
private record via `0x4D9240`,
reads record+0x08 as a registered user pointer,
calls original `0x413B80` removal at `0x4D91FC`,
writes the returned selected-user index at
`0x4D9207`, then resolves a distinct private
record again at `0x4D9216`, pushing its
`+0x0C/+0x28` fields plus the calculated index
into `0x450BB0` at **`0x4D9224`**.
That factory obtains **the current selected registered user**
through `0x4139D0` and its club pointer
`user+0x5B4`, then calls PSupportStart constructor
`0x4CF0F0`. It is not a proof that
every first TeamSelect selection automatically opens
this editor, nor that the editor opens only on deselection.
The *exact UI triggering action*, `0x652F80` conditions,
screen transition/close, edit validation and return remain
UNKNOWN and require following this vtable event and
parent wrapper before building player-visible UI.

Independent reproduction on the unchanged SHA-matched
private original:
```bash
objdump -D -Mintel --start-address=0x4d91c0 --stop-address=0x4d9240 footballmanager.exe
objdump -s --start-address=0x7c7600 --stop-address=0x7c7650 footballmanager.exe
objdump -D -Mintel --start-address=0x450bb0 --stop-address=0x450c35 footballmanager.exe
```
Exact source direct-call candidates obtained by decoding
original text `E8 rel32` targets; `0x4D9224` was the only
direct CALL to `0x450BB0` in the original `.text`.
There may be other indirect caller paths, which were **not**
excluded by this particular xref enumeration.

Original PSupportStart GUI still NOT in the port.
No original binary was run or Windows 11 GUI accepted.
