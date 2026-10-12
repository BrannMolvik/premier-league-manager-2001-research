# Recovery548: source-verified PSupportStart cumulative staff stars

**Original source, not GUI acceptance.** Verified exact original private `footballmanager.exe` (4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`) and original private extracted `FM2001_Art/Support/stars.444` (2,776 bytes; SHA-256 `16c619e305ebad013e7404ea9e5d4414a9f9a8bd0d6ad26f269ee82a49849633`). Neither original file is committed to Git.

**New original owner trace:**

1. PSupportStart's seven-row update at `0x4D06B0` for a non-null staff pointer invokes staff virtual+0x24, multiplies the result by original `1000.0` at `0x7C6828`, then separately invokes staff virtual+0x40, passing its integer return value to row refresh `0x4C9830`. The former is used in another row field; do not conflate these two values.
2. `0x4C9830` at `0x4C9861–0x4C9873` resolves the rating-like integer with `0x4C97D0` and writes the selected source wrapper into row child+0x44 at child+0x2C. The non-null path recomputes the child right boundary from source wrapper field+0x14; NULL uses a separate no-image path.
3. `0x4C97D0` maps 1..5 to `0x945890`, `0x945850`, `0x945810`, `0x9457D0`, `0x945790` respectively; unsigned out-of-range returns NULL.
4. Disassembly of initializer routines `0x5F6310`, `0x5F63A0`, `0x5F6430`, `0x5F64C0`, `0x5F6550` shows all five wrappers use the **same** original Support/stars.444 source loaded through `0x64D750` and filename literal `0x836414`. The `0x64E500` source rectangle fields are `left=0, top=0, right=15/30/45/60/75, bottom=10`. Original sprite dimensions 75x10. These are cumulative fills, not five different staff-role icons or x-shifted fragments.

| Native integer | Wrapper VA | Original image crop (left,top,right,bottom) |
|---|---|---|
| 1 | `0x945890` | `(0,0,15,10)` |
| 2 | `0x945850` | `(0,0,30,10)` |
| 3 | `0x945810` | `(0,0,45,10)` |
| 4 | `0x9457D0` | `(0,0,60,10)` |
| 5 | `0x945790` | `(0,0,75,10)` |
| other | NULL | none |

**Proof reproduction (private original bytes must remain outside Git):**
```bash
sha256sum footballmanager.exe stars.444
objdump -D -Mintel --start-address=0x4d06b0 --stop-address=0x4d0786 footballmanager.exe
objdump -D -Mintel --start-address=0x4c9830 --stop-address=0x4c98a8 footballmanager.exe
objdump -D -Mintel --start-address=0x4c97d0 --stop-address=0x4c9824 footballmanager.exe
objdump -D -Mintel --start-address=0x5f6300 --stop-address=0x5f6580 footballmanager.exe
objdump -D -Mintel --start-address=0x64e500 --stop-address=0x64e5a5 footballmanager.exe
cd reconstruction && python -m unittest test_original_supportstart_stars
```

**Scoped code:** `reconstruction/original_supportstart_stars.py` and dedicated `test_original_supportstart_stars.py` preserve the exact original rectangle and NULL result; rejecting non-integer Python inputs is an explicit port guard, not a claim about native input validation.

**Unresolved:** original fourth-child parent transform and hit/hover behavior, fifth-child text/control, source staff role-label derivation, seven-row edit/Apply/Cancel, actual TeamSelect close/return, Inbox shared CRT, R1 all match modes, multi-human/all leagues, and real Win11 acceptance. The complete player-visible PSupportStart remains missing. No PR/CI is opened for this minor source fragment. Resume this feature branch and trace `0x651BA0`, `0x652400`, `0x4C9830` source interaction semantics, then group a genuinely reviewable complete editor integration. Existing PR645 is draft and touches the separate layout module; do not overwrite it.

## Further source-verified native star child layout (Recovery548)

At `0x4C969F–0x4C96BC`, the source row routine increments its incoming
row x by `0xE6=230`, its row y by `4`, then passes x/y/sprite/0
to `0x651BA0`. The original call to `0x651BA0`
uses source wrapper `+0x14/+0x18` as image width/height,
or width=height=0 for NULL, and forwards x/y/width/height to
`0x64F380`. The original `0x64F380` stores x, y and right/bottom
boundaries using `x+width`, `y+height`.
Thus with native row origins `(391,181+40*i)`:

- **native child local x** = 391+230 = **621**
- **native child local y** = 181+40*i+4 = **185+40*i**, for i=0..6
- native sprite rectangle = `(621,185+40*i,15*grade,10)` for grade1..5
- NULL/out-of-range state has geometry `(621,185+40*i,0,0)`.

These are original **native layout child bounds**, not independently
observed screen-space coordinates and **not** native mouse hit rectangles.
The source-backed `original_supportstart_star_local_rect()` and added
test encode this precisely without claiming GUI acceptance. Original
`0x651BA0` also stores sprite pointer into child+0x2C and
zeroes child+0x30. Exact visible draw ordering/parent transforms and
hit behavior remain unresolved.


## Seven-row selection-state propagation, separate from the stars

Further native disassembly clarifies the original selected-state control
hierarchy without assuming mouse-hit behavior:

- Original row constructor `0x4C9340` sets row vtable
  `0x7C6780`. Its virtual offset `+0x98`
  points exactly to `0x5D6200` (pointer at `0x7C6818`).
- Original `0x4D06B0` at `0x4D078A–0x4D07A0` reads
  source selected-byte array `PSupportStart+0x974`, index0..6,
  computes `selected_byte == 0`, and calls row vft+0x98.
  This is original **row refresh / selection-state initialization**,
  not proof of a physical click or state mutation.
- `0x5D6200` walks registered row children (count at row+0x34,
  pair entries at row+0x2C, per-child registration flag byte+4).
  It changes control bit `0x8000` only for children
  whose registration flag has bit `0x20` set.
  It calls original `0x64F710` (OR bit) for true,
  `0x64F750` (clear bit) for false; it also
  changes the same flag on the parent row object.
- `0x4C9340` registers five children with exact flags
  `0x33,0x31,0x31,0x15,0x15`. Therefore this selected-state
  propagation applies to first three children
  `+0x38,+0x3C,+0x40` (bit `0x20` set), but *not*
  star sprite `+0x44` or fifth child `+0x48`.
  This independently differentiates the cumulative star
  display from the row's selectable/control region.
- Original `0x652F80` reads bit15 of object+0x18.
  In the existing original `0x4D0830` Apply trace,
  that bit is inverted for selected staff record+0x28.
  The native read/set/commit relation is supported;
  user input hit routing and complete transaction are still unknown.

Reproduce with source x86:
```bash
objdump -D -Mintel --start-address=0x4c9340 --stop-address=0x4c94d0 footballmanager.exe
objdump -D -Mintel --start-address=0x4d0788 --stop-address=0x4d07a8 footballmanager.exe
objdump -D -Mintel --start-address=0x5d6200 --stop-address=0x5d6268 footballmanager.exe
objdump -D -Mintel --start-address=0x64f710 --stop-address=0x64f795 footballmanager.exe
objdump -D -Mintel --start-address=0x652f80 --stop-address=0x652f89 footballmanager.exe
```

**Next source objective:** establish which of `+0x38,+0x3C,+0x40`
actually receives pointer/keyboard events and the exact parent row event
dispatch, rather than conflating the passive stars or text rendering
with source-verified click behavior. Preserve all seven original slots.


## Recovery549: native row acceptance and selection bit toggle

The original private 4,714,541-byte `footballmanager.exe` was freshly
SHA-256 checked as `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Disassembly of exact original `0x4C9340`, `0x5D4790`,
`0x5D6200`, `0x5D6270`, `0x64F710`, `0x64F750`,
`0x64F7A0`, `0x652F80`, `0x4D0796` and `0x4D088A`
establishes a **bounded original input-state path**:

1. `PSupportStart` source row vft `0x7C6780` has virtual
   `+0x6C=0x5D6270` and `+0x98=0x5D6200`.
   `0x5D6270` first calls `0x5D4790` with the original
   two event arguments. When that function returns zero, it
   returns without changing bit15. When nonzero, it calls
   `0x652F80` on row+0x18, inverts the bit, then calls
   row vft+0x98, `0x5D6200`, with that Boolean.
2. `0x5D4790` first optionally invokes source
   `0x64F7A0` for the parent gate, then iterates the
   five registered row children, **requiring registration
   flag & 0x04**, the child to pass source
   `0x64F570`, and its virtual+0x6C result. Source
   registration flags are `0x33,0x31,0x31,0x15,0x15`;
   **only fourth+fifth** (offsets `+0x44,+0x48`)
   participate in that child-dispatch loop. This is a
   registration/dispatch property, **not yet a verified
   clickable screen rectangle**.
3. Conversely, native `0x5D6200` updates bit `0x8000`
   for parent and ONLY children whose registration
   flag & `0x20` is set, the **first three**
   (offsets `+0x38,+0x3C,+0x40`), through exact
   `0x64F710` OR or `0x64F750` AND-NOT.
   It does NOT propagate that visual selection bit to the
   fourth star sprite or fifth control.
4. Native `0x4D0796` refreshes a row with
   `(selected_byte==0)` and native Apply `0x4D088A→0x652F80`
   stores `!bit15` back to `source+0x974[i]`,
   before the original staff linked-list transfers. Hence
   for an **initialized** selected byte 1, initial row
   bit15 is 0; one accepted row event makes it 1
   and the eventual Apply byte becomes 0.
   A second accepted input reverses this. **NULL staff
   record bytes are not proven initialized.**

### Source correction to the preceding Recovery547 report

Earlier `GATE13_PSUPPORTSTART_CHILD_CONTROL_RECOVERY547.md`
mistakenly described the first child `+0x38` as
`0x64F300` final vft `0x7BE530`. The actual
source constructor `0x4C938B..0x4C9398` creates
that first child with `0x42DE80` and installs
**final vtable `0x7BE9BC`**. The subsequent row
children are `+0x3C/+0x40→0x7C66C8`,
`+0x44→0x7BE530`, and `+0x48→0x7BFF14`.
Static original .rdata vtable read confirms these
final pointers and their distinct virtual+0x6C methods.
The source-original first-child art `0x945950`
continues to be configured by `0x4C9510`, but
that does not make the first child a plain sprite-control
instance or one of the child input-dispatch candidates.

### Bounded implementation and verification

On the **same unopened** `worker/recovery548-psupportstart-star-strip`
feature branch, `reconstruction/original_supportstart_input.py`
models five native child registration masks, correct
final vtable identities, bit15 propagation to first three,
row initial state from an explicit initialized source byte,
the effect of explicitly upstream-accepted native event,
and original inverse-bit15 value consumed by the existing
`support_staff.original_supportstart_flag_after_selector_state`.
`test_original_supportstart_input.py` contains five
focused regression tests for the source mask split,
one/two accepted events, rejection no-op, preserving
other native bits, unknown empty bytes and input validation.
Five local tests passed in an isolated test copy using a
temporary exact-function local dependency extracted from
`support_staff.py`; **this does not constitute running
the complete GitHub checkout, required exact-head CI or
Windows 11 acceptance**. No original bytes were copied
into the public repository and no new PR/CI was opened.

Reproduce:
```bash
objdump -D -Mintel --start-address=0x4c9340 --stop-address=0x4c94cd footballmanager.exe
objdump -D -Mintel --start-address=0x5d4790 --stop-address=0x5d47fc footballmanager.exe
objdump -D -Mintel --start-address=0x5d6200 --stop-address=0x5d62b0 footballmanager.exe
objdump -D -Mintel --start-address=0x4d0786 --stop-address=0x4d07a5 footballmanager.exe
objdump -D -Mintel --start-address=0x4d088a --stop-address=0x4d08a2 footballmanager.exe
```

**Still P0 and exact next:** trace source `0x64F7A0`'s gate
and child+0x44/+0x48 hit/availability contracts;
`0x652400→0x651F00→0x651E90→0x651BF0`
text-child geometry and effective `0x4C97A0` event
ownership, then fully wire original seven-row
select/edit/Apply/Cancel/TeamSelect return with
original art. Source-verified pure helpers are **not**
player-visible completion. PR645 remains a
separate draft touching `original_supportstart_layout.py`,
PR638 shared CRT remains blocked, and Gates13–17/real
Win11 acceptance remain open.


### Recovery549: fifth child native text rectangle, direct parameter-chain proof

In addition to the previous star sprite `+0x44` layout
`(621,185+40*i,15*stars,10)`, native `0x4C9510`
at `0x4C9723` adds `0x15` to the original row y
and has already added `0xE6` to row x.
It calls `0x652400` at `0x4C978A`
with **first four arguments** `x+230, y+21, 95, 15`.
An independent original-x86 stack argument trace demonstrates
the **first four** args of `0x652400→0x651F00→0x651E90
→0x651BF0→0x64F380` are forwarded unchanged
at every wrapper; `0x64F380` stores the resulting child bounds.
For each of original seven row indices `i=0..6`, fifth child `+0x48`
native local rectangle **`(x=621,y=202+40*i,width=95,height=15)`**.
That is row0 y202 and row6 y442. Original separate
`0x4C9830→0x652470` updates the fifth child's text payload
during staff-row refresh, not the already source-proven setup rectangle.

Evidence:
```bash
objdump -D -Mintel --start-address=0x4c969f --stop-address=0x4c9794 footballmanager.exe
objdump -D -Mintel --start-address=0x652400 --stop-address=0x652470 footballmanager.exe
objdump -D -Mintel --start-address=0x651f00 --stop-address=0x651f3d footballmanager.exe
objdump -D -Mintel --start-address=0x651e90 --stop-address=0x651ef4 footballmanager.exe
objdump -D -Mintel --start-address=0x651bf0 --stop-address=0x651c27 footballmanager.exe
objdump -D -Mintel --start-address=0x64f380 --stop-address=0x64f3bd footballmanager.exe
```

The feature-branch pure function
`original_supportstart_fifth_child_native_rect`
and sixth focused test capture this **native layout**, not a proven physical
hit rectangle, parent transform, text font raster or a live editor.
`0x5D4790` dispatch flags include this fifth child as an input
candidate, but actual successful mouse hit conditions still
depend on the native gate and original frame/control state.


### Recovery549: precise native TeamSelect conditional SupportStart modal edge

Original TeamSelect final vft `0x7C7628` dispatches source
`0x4D91C0` for this original control action.
At `0x4D91C0–0x4D91E4`, source first invokes
`0x64F960` with the input event's two arguments,
then **only if its result is nonzero** invokes
`0x652F80` on the actual TeamSelect control and
continues **only if its control+0x18 bit15 is set**.
The qualified branch then looks up its current user,
retains user identity `0x8755D4`, computes a
selected-record array index via `0x4D9240`, and
passes the source arrays `record+0x0C` (staff pointer slots)
and `record+0x28` (selected bytes) into
`0x450BB0` at exact call `0x4D9224`.
The modal `0x450BB0` constructs `0x29C0`
PSupportStart, enters original native GUI
`0x5EB540` and `0x532650`, reads
`PSupportStart+0x1DE4` only **after** GUI return
and returns that result as AL. Original event1
Cancel=0 and event2 Apply=1 were previously
verified at `0x4D05E0`; the UI's complete
original parent navigation on result still needs tracing.

**This is a conditional event route, not permission to
show SupportStart on every club-row toggle or solely on
TeamSelect Start/Continue.** Generic `0x64F960`
event acceptance and the actual TeamSelect control's
bit15 are both required. The source-bounded helper
`original_supportstart_teamselect_modal_entry` accepts
both verified upstream inputs; a seventh focused test
asserts all four gate/bit combinations. It does NOT
implement a pointer hit test or launch a dialog.

**Present port observable gap:** `reconstruction/front_end_session.py`
`toggle_club_selection` currently changes the selected club IDs
without a native SupportStart session, and its
`TEAM_SELECT/START_CONTINUE` block calls
`gameplay.select_club` and immediately dispatches
to management. `reconstruction/original_game_host.py`
`on_click` handles TeamSelect club rows with
`_update_teamselect_club_row` or accepts
`TEAMSELECT_START_CONTINUE` and draws management.
Neither is the source `0x4D91C0→0x450BB0`
PSupportStart modal/return journey. This is a
**PARTIAL / MISSING original player-visible path**;
do not introduce an unconditional compatibility dialog
until the original source event owner, seven-row GUI,
Cancel/Apply staff state and name edits are qualified.

Repeat:
```bash
objdump -D -Mintel --start-address=0x4d91c0 --stop-address=0x4d926d footballmanager.exe
objdump -D -Mintel --start-address=0x450bb0 --stop-address=0x450ce9 footballmanager.exe
cd reconstruction && python -m unittest test_original_supportstart_input
```


### Further source counterexample: TeamSelect native 0x64F960 flag gating

The original `0x64F960` (distinct from generic row
`0x64F7A0`) begins at `0x64F965–0x64F980`:
it **rejects unless control+0x18 bit `0x0002` is set**
and **bit `0x0020` is clear**. It then may
invoke an owner-dependent virtual input callback before returning
success, so these flags are **necessary, not sufficient**.
The caller `0x4D91C0` also requires control bit
`0x8000` via `0x652F80`.
The modal predicate is consequently:

```text
source_64F960_event_accepted AND (DWORD & 0x0002 != 0)
AND (DWORD & 0x0020 == 0) AND (DWORD & 0x8000 != 0)
```

The `original_supportstart_teamselect_modal_entry`
feature-branch helper now **fails closed** for even a contradictory
`accepted_by_native_64f960=True` if those original
bit guards are not satisfied. A previous staged helper/test
incorrectly permitted `0x8000` without bit0x2;
that isolated test expectation was corrected **before integration**
using source disassembly and positive/negative counterexamples
`0x8000` rejected, `0x8002` accepted (if callback verified),
`0x8022` rejected. Seven focused local tests pass.
Do not conflate `0x64F960`'s bit0x20 guard with the
separate generic row `0x64F7A0` bit0x10 guard.

Repeat:
```bash
objdump -D -Mintel --start-address=0x64f960 --stop-address=0x64fa1a footballmanager.exe
```


## Recovery550: actual native child handlers, input pre-gates, and modal return ownership

The exact original first-party executable (SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`)
was inspected statically, not executed. PE `.rdata` direct
vtable DWORD verification finds both fourth child
`vft 0x7BE530+0x6C` and fifth
`vft 0x7BFF14+0x6C` resolve to **the same
`0x64F7A0` native input-handler routine**.
The first three child final vtable+0x6C pointers
instead resolve to `0x652B50`; their source
registration flags do not permit child event dispatch
through `0x5D4790`.

Disassembly of original `0x5D4790` proves a
**necessary** child input path, in this order:

1. If its second event argument is nonzero, require
   `0x64F7A0` to accept the *parent* row first;
   otherwise the function returns 0 before children.
2. Iterate source registered children with
   **registration flag & 0x04** set
   (actual fourth/fifth only).
3. Require child's `0x64F570` bit0x01 to be set.
4. Invoke the child's own vtable+0x6C (here
   `0x64F7A0`). Native `0x64F7A0` rejects
   child control+0x18 unless bit `0x0002` set
   and bit `0x0010` clear. It may also
   require owner callback +0x0C to accept an
   event and invokes other input notifier paths.
5. Combine accepted child return(s) with the
   upstream parent return, then `0x5D6270`
   toggles row selection bit15 only when
   final accepted return is nonzero.

The bounded
`original_supportstart_source_dispatch_candidates()`
returns the source child **indices that clear only
the deterministic pre-gates** (3 or 4); it never
claims an actual event, hit rectangle, or renderer.

**TeamSelect modal return correction:** native
`0x4D91C0` calls `0x64F960` and
retains its return in EBX, conditionally invokes
the SupportStart modal `0x450BB0`,
which returns `PSupportStart+0x1DE4`
as AL (0=Cancel, 1=Apply). However immediately
after that call, at `0x4D922C`, the
caller **overwrites EAX with the saved EBX**
(`mov eax,ebx`) and returns from
`0x4D9231` with the input-handler result.
Thus **Cancel does not imply TeamSelect
input handler returned 0**. The internal
staff/name side effects still differ.
The feature branch's bounded
`original_supportstart_teamselect_event_outcome()`
keeps these independent result values and fails
closed on impossible modal-result combinations.

Reproduce from private source without putting binaries in Git:
```bash
objdump -s --start-address=0x7be590 --stop-address=0x7be5b0 footballmanager.exe
objdump -s --start-address=0x7bff70 --stop-address=0x7bff95 footballmanager.exe
objdump -D -Mintel --start-address=0x5d4790 --stop-address=0x5d47fc footballmanager.exe
objdump -D -Mintel --start-address=0x64f570 --stop-address=0x64f579 footballmanager.exe
objdump -D -Mintel --start-address=0x64f7a0 --stop-address=0x64f85b footballmanager.exe
objdump -D -Mintel --start-address=0x4d91c0 --stop-address=0x4d923b footballmanager.exe
objdump -D -Mintel --start-address=0x450ca2 --stop-address=0x450ce9 footballmanager.exe
cd reconstruction && python -m unittest test_original_supportstart_input
```

**Qualification:** these are source routine control-flow
facts, not an integrated player-visible SupportStart,
complete native owner callback acceptance, or
Windows 11 GUI test. Extra isolated regression
cases do not justify a new PR/CI until the original
editor can be assembled safely. Continuing task:
trace the owner callback path for the two
event candidates and source modal's screen
transition, then construct complete original seven
staff rows, name editing, Apply/Cancel and return
without overriding existing original-game host behavior
with invented hot zones.


### Recovery550 constructor initialization: star and text event candidates are initially enabled

Disassembly of `0x64F300` at `0x64F30B`
writes control DWORD `+0x18 = 0x183`
(`bit0x01`, `bit0x02`, `bit0x80`,
`bit0x100` set; `bit0x10` clear).
Original `0x4C9340` creates parent row through
`0x5D45B0→0x64F300`, first
three children `+0x38/+0x3C/+0x40`
through `0x42DE80→0x64F300`,
and fourth/fifth children `+0x44/+0x48`
directly through `0x64F300`.
**All six constructor-time DWORDs start at 0x183**.

For an untouched *constructor-time* row, both
input-dispatch candidate children 3 and 4
clear `0x64F570` bit0x01 and
`0x64F7A0` bit0x02 / not-bit0x10
pre-gates. This does **not** show that an
actual mouse position was within either child
or that an owner event callback accepted.
The source render/setup and selected-byte refresh
may subsequently change state, so do not promote
this constructor invariant to an unconditional
all-frames GUI rule.

The feature branch adds
`original_supportstart_fresh_native_row()`
and one focused regression that establishes
original untouched constructor value, eligible
fourth/fifth children, bit15 propagation and
Apply inverse flag without conflating native event
acceptance with click coordinates.

Reproduction:
```bash
objdump -D -Mintel --start-address=0x64f300 --stop-address=0x64f324 footballmanager.exe
objdump -D -Mintel --start-address=0x42de80 --stop-address=0x42dea2 footballmanager.exe
objdump -D -Mintel --start-address=0x5d45b0 --stop-address=0x5d45d9 footballmanager.exe
objdump -D -Mintel --start-address=0x4c9340 --stop-address=0x4c94cd footballmanager.exe
```


## Recovery551: source-verified empty staff row input disabling

Original SHA-256 checked executable `footballmanager.exe`,
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
The precise NULL-staff branch at `0x4D07B0..0x4D07CB`
calls `0x4C9830` with empty labels `0x874BA0`,
zero rating and no stars, then invokes the native row
virtual+0x3C. **This branch never reads the original
selected-byte record+0x28[i]**. This matters for the
seventh fresh-user row, which receives no staff pointer.

Original row final vft `0x7C6780+0x3C = 0x64F540`
(the apparent immediate helper alone is not the final mutation).
The actual call chain:

1. `0x64F540` calls row virtual+0x10(0).
2. Row virtual+0x10 is **`0x4C97A0`**, which forwards
   0 into the fifth child `+0x48` virtual+0x0C.
3. Fifth child vft `0x7BFF14+0x0C = 0x64F3E0`,
   which on false clears bit0x08 and bit0x01 from
   its control+0x18.
4. `0x4C97A0` then calls `0x5D4940(0)` on
   the parent row. It iterates **all five** registered children,
   invokes each child virtual+0x10(0) = `0x64F410`,
   then invokes `0x64F410(0)` on the parent row.
   This clears control+0x18 bit0x02 from all six
   while preserving unrelated bits.
5. Original control constructor `0x64F300` starts
   parent/five child DWORDs at `0x183`, therefore after
   the NULL staff refresh:
   **parent=0x181;
   first four children=(0x181,0x181,0x181,0x181);
   fifth child=0x180**.
   Both original candidate input children now fail
   source pre-gates, so a normal native row input is
   disabled independently of guessed screen-space
   coordinates.

This also clarifies an easy-to-miss vtable mapping:
row `+0x3C=0x64F540` routes via `+0x10=0x4C97A0`,
**not directly to `0x64F410`**. The fifth child gets
additional bit0x01 cleared, beyond general disabled bit0x02.

The feature branch adds source-backed
`original_supportstart_empty_row_after_refresh` and
`original_supportstart_initial_seven_rows` that
preserve original six fresh staff + seventh null row,
as well as every-empty-row edge cases. These
represent **control flags only**, not complete user
input or modal integration. The uninitialized
empty-row selection record remains UNKNOWN;
do not fill it from a fabricated value.

Reproduce from the private original:
```bash
objdump -D -Mintel --start-address=0x4d06e0 --stop-address=0x4d07e9 footballmanager.exe
objdump -s --start-address=0x7c6780 --stop-address=0x7c67c0 footballmanager.exe
objdump -s --start-address=0x7bff14 --stop-address=0x7bff30 footballmanager.exe
objdump -D -Mintel --start-address=0x4c97a0 --stop-address=0x4c97c4 footballmanager.exe
objdump -D -Mintel --start-address=0x5d4940 --stop-address=0x5d4971 footballmanager.exe
objdump -D -Mintel --start-address=0x64f3e0 --stop-address=0x64f40c footballmanager.exe
objdump -D -Mintel --start-address=0x64f410 --stop-address=0x64f42a footballmanager.exe
cd reconstruction && python -m unittest test_original_supportstart_input
```

**Next:** finish complete SupportStart modal source-owned
name/staff edit/Apply/Cancel transaction and integrate
original parent route only after its source input
and original graphics are faithfully established.
All Gates13–17 remain OPEN; source evidence is
not original-runtime or Windows11 GUI acceptance.
