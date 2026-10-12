# Gate 13 Recovery545: TeamSelect to PSupportStart seven staff selectors

## Original identity, scope and independent challenge

The private owner-supplied extracted-disc `footballmanager.exe` is **4,714,541
bytes** and independently hashes SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
This recovery inspected that exact executable via `objdump -D -Mintel`
without executing it. Previous Recovery544 proved the
`PSupportStart` RTTI/vtable identity, original user-name buffers
and event1/2 behavior. This audit follows both source *producers*
and *consumers* of the seven original selector records, and
checks the apparently contradictory count **six** in
`reconstruction/support_staff.py`.

**Six initial staff is source-correct for the fresh producer,
seven controls is source-correct for the later editor.** They
are different object counts in a connected player journey.

## Source-backed normal TeamSelect selection into editor

1. Original clicked TeamSelect club selection `0x4D8E90`, source
   successful select branch `0x4D8EB5`, obtains clicked club,
   registers a fresh DBRUser via `0x413BB0` at `0x4D8EF8`,
   saves selected user pointer in private 0x30-byte
   TeamSelect record `+0x08` (`0x4D8F07`).
   It resets that user’s staff-linked heads at native
   `DBRUser+0x5B8/+0x5C4/+0x5D0`
   (`0x4D8F2E/0x4D8F3E/0x4D8F4E`) before
   invoking the original fresh support producer.
2. `0x4D8F75` calls `0x4C9CD0`. This invokes
   `0x4C9B30` exactly six times with source staff
   type arguments **1, 2, 3, 4, 5, 13** (hex 0x0D)
   in that order at `0x4C9CDC..0x4C9D0B`.
   Native `0x4C9B30` allocates each original 0x218-byte
   staff, calls `0x4CA2F0` with shared RNG-bearing
   generated fields, sets its associated club using the
   selected DBRClub+0x14, inserts staff into
   original global source list `0x875600`
   and original selected user staff list
   `DBRUser+0x5D0/+0x5D4`. This confirms the
   `INITIAL_SUPPORT_STAFF_TYPES=(1,2,3,4,5,13)`
   source producer in `reconstruction/support_staff.py`
   is correctly **six**, not a conflicting editor size.
   Other startup RNG consumers remain unreconciled.
3. `0x4D8F7F` then calls **`0x4DA4F0`**
   on the 0x30-byte private selection record.
   It loops with `ebp=6` down through
   `ebp=0` (seven positions), walking the newly
   registered user’s staff list `DBRUser+0x5D4`
   by indexed linked-list traversal at
   `0x4DA4FE..0x4DA519`.
   For an existent staff record, it assigns the staff
   pointer at `record+0x0C + index*4`
   (`0x4DA57A`/`0x4DA592`) and source byte 1
   at `record+0x28+index` (`0x4DA57C`/`0x4DA594`).
   For an absent position, it assigns NULL pointer
   (`0x4DA519`); the branch does not set
   that index’s byte to 1. A clean six-staff
   producer therefore **does not warrant fabricating
   a seventh staff member**. Original default flag
   initialization for absent index must be separately
   checked before asserting it is zero.

## Editor construction and seven-selector child control evidence

4. TeamSelect native method `0x4D91C0`, via original
   vtable pointer `0x7C7628`, reaches
   `0x450BB0` at `0x4D9224` only when its
   `0x64F960` and `0x652F80` guards pass.
   It passes source private-record `+0x0C`
   (seven pointer entries) and `+0x28`
   (seven bytes) by address into the
   `PSupportStart` constructor `0x4CF0F0`.
   The exact source button/gesture and close
   navigation remain unresolved.
5. Constructor `0x4CF124..0x4CF12C` assigns those
   two external pointers to `PSupportStart+0x970`
   and `+0x974`. It builds **seven** objects at
   `PSupportStart+0x2224` with stride 0x4C
   using `0x6687C1` (count `push 7`,
   constructor `0x4C9340`, destructor
   `0x4D89E0`) at `0x4CF2EF..0x4CF309`.
   Each selector object `0x4C9340`
   allocates child controls at offsets
   `+0x38/+0x3C/+0x40/+0x44/+0x48`,
   registers event IDs **0x33, 0x31, 0x31,
   0x15, 0x15**, respectively through source
   `0x5D4580` at `0x4C948B..0x4C94C7`.
   These are original *child IDs*, not yet
   interpreted as particular on-screen labels.
   Additional widget property/configuration draws
   occur at `0x4C9510...`; exact geometry/colors
   require tracing this separate layout code.
6. Original `PSupportStart` method `0x4D06B0`
   iterates source seven pointers at
   `[PSupportStart+0x970][i]` in ascending
   index 0..6 (`0x4D06E0..0x4D07E7`),
   with selector object offset
   `+0x2224 + i*0x4C`.
   A **non-NULL** pointer invokes source staff
   virtual getters +0x08, +0x14, +0x24 and
   +0x40 before passing derived labels/rating
   and original byte `[+0x974][i]`
   to `0x4C9830` and selector virtual+0x98;
   a NULL pointer instead invokes
   `0x4C9830` with empty original source
   string `0x874BA0`, followed by selector
   virtual+0x3C. Do not display fabricated
   names/ratings for empty rows.
   The native resource at `0x945910` and
   `0x945950` is referenced in the nonempty
   row text path; source visual identity remains
   unqualified.

## Original apply is more than human-name editing

7. Native PSupportStart event 2 at `0x4D0606`
   invokes virtual +0x4C `0x4D0830`, while
   event 1 at `0x4D061F` does not.
   **Before** writing user first/surname
   (`0x4D0A22..0x4D0A61`), `0x4D0830`
   sets `DBRUser+0x5B8/+0x5C4/+0x5D0`
   list heads to zero, walks index 6..0 using
   `[PSupportStart+0x970][i]` and
   `[PSupportStart+0x974][i]`.
   It reads selector `+0x23EC - i*0x4C`
   via `0x652F80`, stores the *inverse*
   Boolean to selected record’s `+0x28+i`.
   It conditionally removes/re-inserts staff
   nodes through original `0x4D1880` and
   `0x617D70` into selected user’s
   source linked collections and global
   `0x875600`. The original also checks
   existing staff pointers across lists
   `DBRUser+0x5BC/+0x5C8/+0x5D4`
   to avoid duplicate assignments.
   **Current PR640 only persists the original human
   name subset; no source-equivalent staff editor
   commit was implemented.**
8. No original runtime/gameplay UI was executed.
   Neither original action labels nor exact
   closing/return, text glyphs, native hit rectangles,
   global staff mutation and serialized save
   remain fully established. Do not classify this
   as PSupportStart player-visible completion.
   The existing Python six-initial-staff generator
   is source-correct for its narrow contract,
   but its startup integration remains deferred
   due to the shared RNG ownership gap. In particular,
   seven **selector slots** do not justify
   creating a seventh generated staff.

## Reproduction

```bash
sha256sum footballmanager.exe
objdump -D -Mintel --start-address=0x4d8e90 --stop-address=0x4d8f85 footballmanager.exe
objdump -D -Mintel --start-address=0x4c9b30 --stop-address=0x4c9d35 footballmanager.exe
objdump -D -Mintel --start-address=0x4da4f0 --stop-address=0x4da59b footballmanager.exe
objdump -D -Mintel --start-address=0x4d91c0 --stop-address=0x4d9239 footballmanager.exe
objdump -D -Mintel --start-address=0x4cf0f0 --stop-address=0x4cf149 footballmanager.exe
objdump -D -Mintel --start-address=0x4cf2ef --stop-address=0x4cf30e footballmanager.exe
objdump -D -Mintel --start-address=0x4c9340 --stop-address=0x4c94df footballmanager.exe
objdump -D -Mintel --start-address=0x4d06b0 --stop-address=0x4d0823 footballmanager.exe
objdump -D -Mintel --start-address=0x4d0830 --stop-address=0x4d0a74 footballmanager.exe
```

## Next source-backed player work

Trace `0x4C9510` selector child geometry and text placement,
`0x4D05E0` event IDs and owning exact on-screen
controls, event 1/2 close and return callback, then
implement complete seven-control editor only after
full source contract. A bounded seven-slot original
staff selection owner can be implemented without
inventing staff or consuming unqualified CRT state.
Review the active Gate13 user journey and persist
before advancing to Inbox selected preview/R1.
