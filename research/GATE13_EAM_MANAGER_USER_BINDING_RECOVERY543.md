# Recovery543 corrected: source DBRUser+0x5B4 is selected **club** pointer, not manager pointer

## Critical correction of first Recovery543 interpretation

The earlier Recovery543 audit incorrectly called the pointer in native
`DBRUser+0x5B4` a **manager object**. A deliberate cross-check against
`0x403E10`, `0x413020`, `0x426090`, and
`0x4261B8` conclusively disproves that label: it is an original
**DBRClub pointer**. The prior interpretation is **WRONG/SUPERSEDED**,
not a valid source contract. The source first-screen selected entity
`[[first_screen+0x3C]+0x4C]` is the selected **club**, not a manager.
This distinction changes which identity is required for Inbox
`{MANAGERNAME:1}`.

## Verified source evidence, no original execution

Actual owner-supplied private original `footballmanager.exe` is 4,714,541
bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Static x86 disassembly only; did not launch the original or test Win11 GUI.

1. Original TeamSelect handler `0x4D8EBE..0x4D8EF8` reads the **selected
   club pointer** from `[[screen+0x3C]+0x4C]`, calls `0x4D9800`
   to prepare club-related view, reads **DBRClub+0x40 manager index**,
   and registers the same **club pointer** through `0x413BB0`.
2. `0x413BB0` traverses previously registered users,
   dereferences their `DBRUser+0x5B4` **club pointers**, and
   compares previous `club+0x04` to candidate `club+0x04`
   (`0x413BD8..0x413BE6`) to prevent duplicate chosen clubs.
   In the new-user branch, it allocates DBRUser, attaches it to
   the registry `+0x9CC`, and passes the **club pointer**
   to DBRUser setup `0x4258D0` (`0x413C4F..0x413C54`).
   `0x4258F2` writes it verbatim to `user+0x5B4`.
3. `DBRUser::0x426090` immediately dereferences the **club pointer**
   at user+0x5B4 and calls `0x403E10` on it. The latter reads
   **club+0x40 manager index**; it validates manager table record
   `manager[index*0x40]+0x24` and can clear invalid assignments
   (`0x403E10..0x403E3C`). It is not a manager-pointer validator.
4. At `0x4260A4..0x426116`, source setup obtains source manager first
   and surname strings via `DBRClub+0x40` indexing the table
   `0x875628` (0x40-byte records) at +0x08/+0x0C, and copies
   them to DBRUser's own name buffers at `+0x05` and `+0x25`;
   source fallback text applies only when the selected club
   has no valid previous manager.
5. At `0x426162..0x4261E1`, it searches the original manager table
   via `0x4151C0` for a new/free manager slot, handles the old
   manager, **writes the new manager index into the selected club's
   +0x40 at `0x4261B8`**, then writes that club's +0x04 ID
   to new manager[index*0x40]+0x24 (`0x4261C1..0x4261D2`).
   This is an important mutable club-to-user-manager rebind;
   treating the selected club's imported pre-registration
   manager index as the ongoing identity is wrong.
6. Current registered user `0x4139D0` returns registry-selected
   user; original Inbox `0x56FE01..0x56FE2D` passes
   **user+0x5B4 selected club pointer** to
   typed MANAGERNAME constructor `0x612FD0`, which extracts
   the club's **current manager index from club+0x40**
   (`0x612FEA`). `0x613040` indexes original manager table
   by `index*0x40`, loads first and surname through
   `0x414F30/0x414FA0`, then formats original `%s %s`
   literal `0x81858C`. Therefore the correct user-specific
   greeting depends on the **registered selected club's
   currently rebound manager index and actual manager name**,
   not on an arbitrary registered-manager key or blank
   DBRUser+0xD0 club alias.
7. Independent first-screen capacity source `0x4DA4D0`
   checks current number of users at `0x8755E4` against six.
   This six-user cap was ALREADY recorded in
   `gate17_multi_human_start_source_trace.py`, and is not
   presented as a new discovery.

## Modern reconstruction comparison and unresolved boundary

`GameState.bind_original_user_mail_recipient` currently derives
`native_user_recipient_key` by scanning modern `state.managers`
for a `first_name.startswith('!')` manager (or a fallback).
`state.user_controlled_club_id` and current club manager
`state.clubs[club_id].manager_id` are separate fields.
Original source requires provenance of actual selected club,
manager replacement at `0x4261B8`, original manager name source
and ordering, including 2–6 human users. The modern heuristic
cannot by itself establish that this actual original rebind
happened or that the manager's first/surname name is authentic.
Do NOT derive a visible Inbox `Dear` from the
pre-registration imported AI manager, `native_user_recipient_key`
alone, or the club alias.

**Required next P0:** inspect modern new-game human selection and its manager
assignment, compare to original `0x426090` entire rebind/name
lifecycle, including original `0x4151C0`, and establish how the
registered current user's new manager name is actually populated
after selection. Then implement/test explicit source-selected
club→current manager identity and authentic typed
`MANAGERNAME`; next reconcile native shared CRT TLS random
stream and first-click Inbox side effects. Keep PR638
DRAFT/BLOCKED; original selected body/PEAMMessage/ESC,
R1 all modes, full 2–6 humans/countries/leagues, and
Gates13–17 Win11 GUI release remain OPEN.

## Reproduce with private exact-byte original

```bash
sha256sum footballmanager.exe
objdump -D -Mintel --start-address=0x4d8e90 --stop-address=0x4d8f19 footballmanager.exe
objdump -D -Mintel --start-address=0x413bb0 --stop-address=0x413c89 footballmanager.exe
objdump -D -Mintel --start-address=0x4258d0 --stop-address=0x425901 footballmanager.exe
objdump -D -Mintel --start-address=0x426090 --stop-address=0x4261e5 footballmanager.exe
objdump -D -Mintel --start-address=0x403e10 --stop-address=0x403e3d footballmanager.exe
objdump -D -Mintel --start-address=0x56fdfe --stop-address=0x56fe4e footballmanager.exe
objdump -D -Mintel --start-address=0x612fd0 --stop-address=0x613079 footballmanager.exe
```


## Follow-up original 0x4151C0 and effective human name override

Source `0x4151C0..0x415208` **does not merely pick any
manager name beginning with '!'.** It iterates *all existing
registered users* via `0x413B10`, reads each selected
`DBRUser+0x5B4` **club pointer** and its **current**
`DBRClub+0x40` manager slot, compares it to candidate manager
`+0x04`, and rejects any already owned by a user.
Only when no registered user owns that candidate does
`0x4151F4..0x415203` inspect the manager's source
first-name first byte for ASCII `!` (0x21). Thus an
apparently free placeholder `!` entry already assigned
to a human user is ineligible. Modern single-user
`native_user_recipient_key` search by `startswith('!')`
can only be source-equivalent if current-user registry
and manager slot rebind are also correctly modeled;
it is NOT a provenance check by itself.

**Crucial human-display name resolution:** original
`0x414F30` and `0x414FA0` are not unconditional static
manager table readers. For manager+0x24 associated club,
`0x4037B0` asks whether that club is human controlled.
On true it calls `0x403850`, which invokes `0x413B40` to
look up **DBRUser by club+0x04**, and returns
`user+0x05` for first name (`0x414F70/0x414F8C`)
and `user+0x25` for surname
(`0x414FE0/0x414FFC`); only on no human owner do
`0x414F91..0x414F97` and `0x415001..0x415007`
read static manager `+0x08` and `+0x0C`.
`0x413B40` exactly compares `DBRUser+0x5B4
-> DBRClub+0x04` to a source club ID at
`0x413B4E..0x413B6F`.

At initial fresh-user setup `0x4260A4..0x426116`
copies the **old** associated club manager's effective
first and surname into `DBRUser+0x05/+0x25`,
or source fallback when no such previous manager.
`0x4261B8` subsequently rebinds the club
to an available placeholder human manager slot;
the *effective* name for the new manager can
therefore be drawn from **that human user's name
buffers**, not the new slot's literal leading-`!`
placeholder static name. Editable user name control
semantics and modern representation remain unresolved.

**New exact P0:** source-trace edits/persistence to
native user first/surname `+0x05/+0x25` and
compare actual modern selected-user creation and naming.
An honest live Inbox body should resolve the
currently selected club, rebound user manager ID, and
actual selected native DBRUser name fields *before*
applying original `%s %s` typed formatter. Without
those fields, keep selected preview absent instead
of showing a literal `!` or old imported AI manager.

Reproduce privately, source EXE unchanged:
`objdump -D -Mintel --start-address=0x4151c0 --stop-address=0x415209 footballmanager.exe`;
`--start-address=0x414f30 --stop-address=0x415008`;
`--start-address=0x4037b0 --stop-address=0x40386f`;
`--start-address=0x413b40 --stop-address=0x413b70`.
The original game has not been executed; this is
source-level proof, NOT integration or Win11 GUI acceptance.
