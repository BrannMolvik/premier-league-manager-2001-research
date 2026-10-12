# Recovery544: native current-human name field edit/commit traced to GUI owner

## Original identity and scope

Owner-supplied private original `footballmanager.exe`, 4,714,541 bytes,
SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`,
was independently checked with local `sha256sum` on 12 October 2026.
All evidence below comes from **static x86 disassembly of that file**. Original
game was **not executed**; Windows 11 GUI and screen control visuals remain unverified.

## Source-confirmed complete bounded field lifecycle

1. Native `DBRUser::0x4258D0` receives selected **DBRClub pointer**, writes
   `user+0x5B4` at `0x4258F2`, and subsequently calls
   `0x426090`. After original club manager validator
   `0x403E10` (club+0x40 not -1, manager+0x24 not -1),
   `0x4260A4..0x4260DC` copies the prior manager table's
   **static first name** through source manager+0x08 into
   `DBRUser+0x05`, and `0x4260DE..0x426114` copies its static
   surname from manager+0x0C into `DBRUser+0x25`.
   The fallback branch `0x426118..0x426160` copies original
   literal `John` (VA `0x8195E4`) to +0x05 and
   `Smith` (VA `0x8195DC`) to +0x25 when the club's
   prior manager fails original validation. These literal bytes
   were read directly from the SHA-authenticated PE.
   NOTE: first user name is copied *before* original
   `0x4261B8` changes selected club+0x40 to placeholder human
   manager slot.
2. Native original GUI owner constructor `0x4CF58D..0x4CF609`
   resolves current selected user with `0x4139D0` and allocates
   editable text buffers of **0x30 bytes each** at
   owner offsets `+0x97C` (first name), `+0x980`
   (surname), with other nearby fields. At `0x4CF6AC..0x4CF6F0`
   it copies the selected user's current `+0x05/+0x25`
   null-terminated strings into these editable buffers.
   This is a *read/preload*, not the original write.
3. Original GUI commit/update method beginning `0x4D0830`
   again resolves current selected user at
   `0x4D09FD..0x4D0A15`. At `0x4D0A1C..0x4D0A40`
   it copies source editable buffer owner+0x97C into
   **current DBRUser+0x05**, and at
   `0x4D0A42..0x4D0A61` owner+0x980 into
   **current DBRUser+0x25**.
   `0x4D0A63..0x4D0A6C` also commits a separate
   source byte from owner+0x1FF0 to `DBRUser+0x04`;
   do not confuse that byte with name text.
   The source GUI thus permits a real first/surname change
   after TeamSelect without rewriting manager table placeholder
   data. The screen's full native controls, edit event routing,
   validation and disk save serialization remain UNKNOWN.
4. Original manager name getters `0x414F30` and
   `0x414FA0` check whether the manager's associated club
   is human controlled; if yes, `0x403850` finds the
   registered DBRUser for that club and returns
   `+0x05/+0x25`, **not the immutable imported manager
   table's `+0x08/+0x0C`**. Native Inbox
   `0x56FE0C->0x612FD0->0x613040` therefore reads
   the current editable human name, with original
   `%s %s` format literal at `0x81858C`.

## Reconstruction comparison and high-priority task

The current reconstruction's normal single-human
`HumanGameplayController.select_club` installs
`HumanManagerState(club_id,...)` then calls
`GameState.bind_original_user_mail_recipient`, which
only computes a `native_user_recipient_key` index using
a static `!` marker scan. `HumanManagerState`
has **no actual source user first/surname fields**;
`GameState` has no DBRUser+0x05/+0x25 fields; internal
JSON save writes only `native_user_recipient_key`,
mailboxes, and selected club. Original manager
table static names cannot replace this original
user-specific editable source. This is a
confirmed **missing production original capability**.

**Implementation P0:** introduce a distinctly owned
native current-human first/surname plus verified selected
club/free-manager-slot identity in the live controller/state,
initialized before manager rebind per `0x426090`, without
overwriting original immutable source manager names. Preserve
the user names through save/reload. Add selected-manager name
edits only through a future original-proven native GUI route,
with source text length/encoding/click validation.
Apply original `{MANAGERNAME:1}` only when actual
source-qualified selected-user name state is present;
unknown 2–6-user contexts and legacy saves remain
fail-closed. PR638 remains DRAFT/BLOCKED until original
shared CRT stream is reconciled. Complete actual Inbox
preview/modal/ESC, R1 match return, and every original
country/league/human flow before Gate13–17 release claims.

## Reproduce

```bash
sha256sum footballmanager.exe
objdump -D -Mintel --start-address=0x403e10 --stop-address=0x403e3d footballmanager.exe
objdump -D -Mintel --start-address=0x426090 --stop-address=0x4261e5 footballmanager.exe
objdump -D -Mintel --start-address=0x4cf58d --stop-address=0x4cf725 footballmanager.exe
objdump -D -Mintel --start-address=0x4d0830 --stop-address=0x4d0a74 footballmanager.exe
objdump -D -Mintel --start-address=0x414f30 --stop-address=0x415008 footballmanager.exe
```

**Evidence levels:** ORIGINAL SOURCE exact for these named
instruction paths; reconstructed identity and original GUI
name editing integration **NOT implemented**; original
process observation and Win11 GUI acceptance **NOT done**.
