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


## PSupportStart native input event table: source-proven apply vs cancel (follow-on)

A new bounded disassembly identifies original PSupportStart **virtual
+0x10** at VFT `0x7C6DEC` as `0x4D05E0`, a genuine
native PSupportStart event dispatch function. The event arg
is dereferenced `[arg+0x20]`; native source decrements it,
rejects values outside 1–20, maps 20 event IDs through a
five-entry jump table and executes the original behaviors.
Raw original PE table `0x4D0690` and target table
`0x4D067C` were independently decoded:

| Native event value | Branch | Proven behavior |
| --- | --- | --- |
| 1 | `0x4D061F` | Writes PSupportStart `+0x1DE4 = 0` and invokes `0x6539F0` with argument 0; **does NOT call edit commit virtual** |
| 2 | `0x4D0606` | Invokes PSupportStart **virtual +0x4C = `0x4D0830`**, then writes `+0x1DE4 = 1` and invokes `0x6539F0` with argument 0; **commits edited current DBRUser+0x05/+0x25 first** |
| 3 | `0x4D0631` | Invokes PSupportStart virtual +0x48 (`0x4D06B0`); distinct function, effects require further source audit |
| 4–17 | `0x4D0641` | No special branch before shared base `0x653350` processing |
| 18–20 | `0x4D063A` | Invokes `0x4CFA70`; source semantics not yet qualified |

`0x4D05E0` then computes original surface rect
and calls base `0x653350`, so a branch-local edit
action is **not** all parent event/render work.
The event #1 vs #2 distinction is source-exact:
event 1 discards current text-buffer changes as far
as native commit virtual is concerned; event 2
applies current name buffers before initiating closing.
The functions have not been run, and interpreting
`0x6539F0` as an actual observed close is not
allowed: it is a source caller/action edge that
needs control-owner confirmation. Do not label
these events as specific on-screen text/buttons
until source control mapping is independently checked.
The third action and 18–20 remain unresolved.

The `0x4D0830` original commit does **more than
names**: it first processes a six-element source
selection list at owner `+0x970/+0x974` and
connected registered-user nodes `+0x5B8/+0x5C4/+0x5D0`
before writing name fields. Hence the new source
name-state implementation PR640 is only a bounded
subset, **not** a complete original PSupportStart
apply transaction. Routing event 2 to a name-only
modern form would silently discard shipped support
selection behavior and must not be presented as an
original-complete port.

Reproduction on the private original executable:
```bash
objdump -s --start-address=0x7c6ddc --stop-address=0x7c6e34 footballmanager.exe
objdump -D -Mintel --start-address=0x4d05e0 --stop-address=0x4d06b0 footballmanager.exe
objdump -D -Mintel --start-address=0x4d0830 --stop-address=0x4d0a74 footballmanager.exe
```
Decode five 32-bit branch VAs from original
`0x4D067C`; decode 20 one-byte branch indexes
from original `0x4D0690`. Use checked canonical
original SHA-256 at top. No original runtime
or native Windows GUI acceptance.


## Original `FM2001_Art/Support/` resources directly retrieved and hashed

Owner's private extracted original game tree in connected Google Drive has an
actual `FM2001/FM2001_Art/Support/` directory. On 12 October
2026, five original files were separately materialized into
a **private temporary analysis directory**, actual bytes read and
SHA-256 independently recomputed. No proprietary bytes were
committed to the public Git repository.

| Original path under FM2001 | Actual bytes | SHA-256 |
| --- | ---: | --- |
| `FM2001_Art/Support/stars.444` | 2,776 | `16c619e305ebad013e7404ea9e5d4414a9f9a8bd0d6ad26f269ee82a49849633` |
| `FM2001_Art/Support/stars2.444` | 1,504 | `54c2b86375695d3b8a5df9cf463e11e877f0e47f64f6883e6eea108784db953d` |
| `FM2001_Art/Support/sub_title_bar.444` | 3,988 | `4088bc5c0580c74026b8dadb6a876deb00e474b1da9429a7fec05901624284c0` |
| `FM2001_Art/Support/support_bars.444` | 4,516 | `518fbf6d7f7d44d55c3c76daa48f132e06b9011791b916cb5a125207eceb290c` |
| `FM2001_Art/Support/support_title_bar.444` | 4,076 | `0b79b83a23fc5f3bea97b4390256034c2439c83be9998a412dba7b57c0d6ef6b` |

Direct private Drive file IDs (same table order):
`1yEyn00p8t8r_PixdxmRz_VJze7fUm835`,
`1TC02F1WZf7kPdRNZpxOtUULXsGJfQ6uP`,
`17EME3n6W14pzQp2X3OKxL3X7q18F15dI`,
`1oP-AfHy-Wda3sriy7j9pc86hzRhuEIZZ`,
`1YlyeQyKYEn6A85LVH4s5QPqP3FUdH5hx`.
Folder is the owner's original private source; no public sharing changes.

Canonical original EXE SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
has exact original source-path literals at PE VAs
`0x8362AC` (support title),
`0x8362D8` (subtitle),
`0x836354` (support bars),
`0x836414` (stars) and `0x836434` (stars2).
They are loaded via native `0x64D750`
from `0x5F5DC0` into `0x945AD0`,
`0x5F5E50` into `0x945A90`,
`0x5F6050` into `0x9459B0`,
and separate `0x5F62C0..0x5F6595` paths for
stars and stars2 respectively. The support-title loader
builds native resource wrapper `0x945AB0` via
`0x5F5E00..0x5F5E38`, called at
`0x4C92A0` as a drawing input. These
are **original resource load mappings**, not proof
of their exact ownership on PSupportStart,
coordinates, selection frames, or user-visible UI.
The PSupportStart constructor has a direct
`0x4C9340` callback at `0x4CF2F4`; mapping
that callback's child/control resource and
screen origin to these particular files remains
a specific **next source investigation**.

**Reproduce original path literals** with
`strings -a -t x footballmanager.exe | grep -iE 'support_bars|support_title_bar|sub_title_bar|stars2|stars\.444'`,
and disassemble:
```bash
objdump -D -Mintel --start-address=0x5f5dc0 --stop-address=0x5f5e60 footballmanager.exe
objdump -D -Mintel --start-address=0x5f6050 --stop-address=0x5f6064 footballmanager.exe
objdump -D -Mintel --start-address=0x4c92a0 --stop-address=0x4c9337 footballmanager.exe
objdump -D -Mintel --start-address=0x4cf2ef --stop-address=0x4cf30e footballmanager.exe
```
No original executable was launched. Native
GUI and Windows 11 acceptance remain unverified.
Do not import images into `original_assets`
until genuine PSupportStart use/transform is qualified
according to asset policy.
